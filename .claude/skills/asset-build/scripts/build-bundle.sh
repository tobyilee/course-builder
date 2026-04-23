#!/usr/bin/env bash
# Build the full course bundle after coherence review passes.
#
# Extended pipeline (Phase 5 one-shot):
#   1. Gate — coherence_report.overall must be "pass"
#   2. Render Marp slide.html (per class)
#   3. Render Marp PNG slides (per class, for player)
#   4. TTS synthesis (per class, if OPENAI_API_KEY set and SKIP_TTS!=1)
#   5. Synthesize manifest (aggregates existing assets)
#   6. Generate HTML player + quiz + index (if script present)
#   7. SSML validate (warn only)
#   8. Package bundle.zip
#
# Env overrides:
#   SKIP_TTS=1      — skip TTS even if API key present
#   FORCE_TTS=1     — re-synthesize even if audio/full.mp3 exists
#   SKIP_PLAYER=1   — skip player HTML generation
#
# Usage: build-bundle.sh <course_root>

set -euo pipefail

COURSE_ROOT="${1:?Usage: build-bundle.sh <course_root>}"
BUILD_DIR="$COURSE_ROOT/build"
ROOT_DIR="$(cd "$(dirname "$COURSE_ROOT")" && pwd)"
WORKSPACE="$ROOT_DIR/_workspace"
LOG="$WORKSPACE/98_build_log.txt"

mkdir -p "$WORKSPACE"
: > "$LOG"
log(){ echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }

# ── Gate ───────────────────────────────────────────────────────────────
REPORT="$WORKSPACE/99_coherence_report.json"
if [ ! -f "$REPORT" ]; then
  log "BUILD_REFUSED: $REPORT not found"
  exit 10
fi
if command -v jq >/dev/null 2>&1; then
  OVERALL=$(jq -r '.overall' "$REPORT")
  if [ "$OVERALL" != "pass" ]; then
    log "BUILD_REFUSED: coherence.overall=$OVERALL"
    exit 11
  fi
  # Sanity check: JSON verdict must match MD header (catches reviewer dual-write bug)
  REPORT_MD="$WORKSPACE/99_coherence_report.md"
  if [ -f "$REPORT_MD" ]; then
    MD_VERDICT=$(grep -m1 '^## VERDICT:' "$REPORT_MD" | awk '{print $3}' | tr '[:upper:]' '[:lower:]' || echo "")
    if [ -n "$MD_VERDICT" ] && [ "$MD_VERDICT" != "$OVERALL" ]; then
      log "WARN: verdict mismatch — JSON=$OVERALL, MD=$MD_VERDICT (reviewer dual-write drift; build continues)"
    fi
  fi
fi

# ── Tool checks ────────────────────────────────────────────────────────
command -v marp   >/dev/null 2>&1 || { log "ERROR: marp missing";   exit 20; }
command -v zip    >/dev/null 2>&1 || { log "ERROR: zip missing";    exit 21; }
command -v ffmpeg >/dev/null 2>&1 || { log "ERROR: ffmpeg missing"; exit 22; }

# Load env for TTS
if [ -f "$ROOT_DIR/.env" ]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
fi

log "BUILD START"

# ── Step 1+2: Render Marp HTML + PNG ──────────────────────────────────
OK_HTML=0; FAIL_HTML=0; OK_PNG=0; FAIL_PNG=0
while IFS= read -r -d '' f; do
  dir=$(dirname "$f")
  if marp --html --allow-local-files "$f" -o "$dir/slide.html" </dev/null >>"$LOG" 2>&1; then
    OK_HTML=$((OK_HTML+1))
  else
    FAIL_HTML=$((FAIL_HTML+1))
    log "WARN: marp html failed for $f"
  fi
  mkdir -p "$dir/slides_png"
  if marp --images png --image-scale 1.5 -o "$dir/slides_png/slide.png" "$f" </dev/null >>"$LOG" 2>&1; then
    OK_PNG=$((OK_PNG+1))
  else
    FAIL_PNG=$((FAIL_PNG+1))
    log "WARN: marp png failed for $f"
  fi
done < <(find "$COURSE_ROOT/sections" -name 'slide.source.md' -print0)
log "Marp HTML: $OK_HTML/$((OK_HTML+FAIL_HTML)) · PNG: $OK_PNG/$((OK_PNG+FAIL_PNG))"

# ── Step 3: TTS synthesis ──────────────────────────────────────────────
TTS_WRAP="$ROOT_DIR/.claude/skills/tts-synthesis/scripts/run.sh"
# Read language from Course Spec for language-aware TTS defaults
COURSE_LANG=$(jq -r '.language // "ko"' "$WORKSPACE/01_architect_course_spec.json" 2>/dev/null || echo "ko")
if [ -n "${OPENAI_API_KEY:-}" ] && [ "${SKIP_TTS:-0}" != "1" ] && [ -x "$TTS_WRAP" ]; then
  OK_TTS=0; SKIP_TTS_CNT=0; FAIL_TTS=0
  while IFS= read -r -d '' t; do
    cls_dir=$(dirname "$t")
    audio_dir="$cls_dir/audio"
    # Skip if audio exists and not forced
    if [ -f "$audio_dir/full.mp3" ] && [ "${FORCE_TTS:-0}" != "1" ]; then
      SKIP_TTS_CNT=$((SKIP_TTS_CNT+1))
      continue
    fi
    # Find matching beats.json (by class slug path)
    cls_slug=$(basename "$cls_dir")
    beats_arg=""
    for candidate in "$WORKSPACE"/03_class_*_beats.json; do
      [ -f "$candidate" ] || continue
      c_id=$(jq -r '.class_id' "$candidate" 2>/dev/null || echo "")
      # Heuristic match: if cls.json has class_id matching candidate's
      cls_json="$cls_dir/class.json"
      if [ -f "$cls_json" ]; then
        ccid=$(jq -r '.id // empty' "$cls_json" 2>/dev/null)
        if [ "$ccid" = "$c_id" ]; then
          beats_arg="--beats $candidate"
          break
        fi
      fi
    done
    rm -rf "$audio_dir"; mkdir -p "$audio_dir"
    log "TTS: $cls_slug [$COURSE_LANG]${beats_arg:+ (affect)}"
    # shellcheck disable=SC2086
    if bash "$TTS_WRAP" "$t" "$audio_dir" --language "$COURSE_LANG" $beats_arg >>"$LOG" 2>&1; then
      OK_TTS=$((OK_TTS+1))
    else
      FAIL_TTS=$((FAIL_TTS+1))
      log "WARN: TTS failed for $cls_slug"
    fi
  done < <(find "$COURSE_ROOT/sections" -name 'transcript.txt' -print0)
  log "TTS: $OK_TTS synthesized, $SKIP_TTS_CNT cached, $FAIL_TTS failed"
else
  if [ -z "${OPENAI_API_KEY:-}" ]; then
    log "TTS skipped (OPENAI_API_KEY not set)"
  elif [ "${SKIP_TTS:-0}" = "1" ]; then
    log "TTS skipped (SKIP_TTS=1)"
  else
    log "TTS skipped (wrapper missing)"
  fi
fi

# ── Step 4: Manifest synthesis ────────────────────────────────────────
SYNTH="$ROOT_DIR/scripts/synth-manifest.py"
if [ -f "$SYNTH" ]; then
  python3 "$SYNTH" "$COURSE_ROOT" >>"$LOG" 2>&1 || { log "ERROR: manifest synthesis failed"; exit 30; }
  log "Manifest synthesized"
else
  log "WARN: $SYNTH missing — manifest not refreshed"
fi

# ── Step 5: Player HTML ───────────────────────────────────────────────
PLAYER_GEN="$ROOT_DIR/scripts/generate-player.py"
if [ -f "$PLAYER_GEN" ] && [ "${SKIP_PLAYER:-0}" != "1" ]; then
  python3 "$PLAYER_GEN" "$COURSE_ROOT" >>"$LOG" 2>&1 || log "WARN: player generation failed"
  log "Player HTML generated"
fi

# ── Step 6: SSML validate ─────────────────────────────────────────────
SSML_OK=0; SSML_WARN=0
VALIDATOR="$ROOT_DIR/.claude/skills/script-writing/scripts/validate-ssml.sh"
if [ -x "$VALIDATOR" ]; then
  while IFS= read -r -d '' f; do
    if bash "$VALIDATOR" "$f" >>"$LOG" 2>&1; then
      SSML_OK=$((SSML_OK+1))
    else
      SSML_WARN=$((SSML_WARN+1))
    fi
  done < <(find "$COURSE_ROOT/sections" -name 'transcript.ssml' -print0)
fi
log "SSML: $SSML_OK OK, $SSML_WARN warn"

# ── Step 7: Bundle ────────────────────────────────────────────────────
rm -rf "$BUILD_DIR"; mkdir -p "$BUILD_DIR"
( cd "$COURSE_ROOT" && zip -qr "build/bundle.zip" . \
    -x 'build/*' -x '_workspace/*' -x '.DS_Store' -x '*/.*' )
SIZE=$(du -h "$BUILD_DIR/bundle.zip" | awk '{print $1}')
log "Bundle: $BUILD_DIR/bundle.zip ($SIZE)"

log "BUILD COMPLETE"
