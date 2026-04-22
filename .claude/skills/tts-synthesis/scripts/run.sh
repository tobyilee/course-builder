#!/usr/bin/env bash
# TTS synthesis wrapper — guarantees pipefail and loads .env.
# Usage: run.sh <transcript.txt> <out_dir> [extra flags passed to synthesize-tts.py]

set -euo pipefail

TRANSCRIPT="${1:?Usage: run.sh <transcript.txt> <out_dir> [flags]}"
OUT_DIR="${2:?Usage: run.sh <transcript.txt> <out_dir> [flags]}"
shift 2

# Resolve project root (two dirs up from this script: skills/tts-synthesis/scripts/)
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"

# Load env (for OPENAI_API_KEY) if .env exists
if [ -f "$ROOT/.env" ]; then
  # shellcheck disable=SC1091
  source "$ROOT/.env"
fi

SCRIPT="$ROOT/scripts/synthesize-tts.py"
[ -f "$SCRIPT" ] || { echo "ERROR: $SCRIPT not found" >&2; exit 2; }

# Use PIPESTATUS to propagate python3 exit through tee
LOG="${TTS_LOG:-/tmp/tts-$(date +%s).log}"
python3 "$SCRIPT" "$TRANSCRIPT" "$OUT_DIR" "$@" 2>&1 | tee "$LOG"
exit "${PIPESTATUS[0]}"
