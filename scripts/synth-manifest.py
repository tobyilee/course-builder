#!/usr/bin/env python3
"""
Synthesize course/manifest.json from _workspace/ specs + course/ asset files.

Idempotent — reads current state, writes fresh manifest. Detects which assets
exist (audio, slides_png) and records their paths. Computes stats from actual
files so re-running after adding TTS/player updates duration etc.

Usage: synth-manifest.py <course_root>
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def mp3_duration(path: Path) -> float:
    if not path.exists():
        return 0.0
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def count_slides(slide_source_md: Path) -> int:
    """Count '---' separators to estimate slide count (minus 1 for frontmatter)."""
    if not slide_source_md.exists():
        return 0
    text = slide_source_md.read_text(encoding="utf-8")
    # Rough: count lines that are exactly '---'
    seps = sum(1 for line in text.splitlines() if line.strip() == "---")
    # frontmatter contributes 2 separators (open + close), each slide adds 1 separator
    return max(seps - 1, 0)


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: synth-manifest.py <course_root>")
    root = Path(sys.argv[1])
    ws = root.parent / "_workspace"

    spec_path = ws / "01_architect_course_spec.json"
    los_path = ws / "01_architect_learning_objectives.json"
    if not spec_path.exists() or not los_path.exists():
        sys.exit(f"ERROR: {spec_path} or {los_path} missing")

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    los = json.loads(los_path.read_text(encoding="utf-8"))

    # Write meta/
    meta_dir = root / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "learning_objectives.json").write_text(
        json.dumps(los, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    audience_md = meta_dir / "audience.md"
    if not audience_md.exists():
        aud = spec.get("audience", "")
        if isinstance(aud, dict):
            lines = ["# 대상 학습자", ""]
            for k in ("profile", "level"):
                if aud.get(k):
                    lines.append(f"- **{k.title()}:** {aud[k]}")
            if aud.get("assumed_knowledge"):
                lines.append("\n## 전제 지식")
                lines.extend(f"- {x}" for x in aud["assumed_knowledge"])
            lines.append(f"\n- **Depth:** {spec.get('depth','')}")
            lines.append(f"- **Language:** {spec.get('language','')}")
            lines.append(f"- **Tone:** {spec.get('tone','')}")
            if spec.get("prerequisites"):
                lines.append("\n## 선수 과목")
                lines.extend(f"- {p}" for p in spec["prerequisites"])
            audience_md.write_text("\n".join(lines), encoding="utf-8")
        else:
            audience_md.write_text(
                f"# 대상 학습자\n\n- **Audience:** {aud}\n"
                f"- **Depth:** {spec.get('depth','')}\n- **Language:** {spec.get('language','')}\n"
                f"- **Tone:** {spec.get('tone','')}\n\n"
                f"## 전제조건\n" + "\n".join(f"- {p}" for p in spec.get("prerequisites", [])),
                encoding="utf-8",
            )

    # Build section/class tree
    sections_out = []
    total_slides = 0
    total_audio = 0.0
    bloom_dist: dict[str, int] = {}
    for lo in los:
        b = lo.get("bloom", "")
        bloom_dist[b] = bloom_dist.get(b, 0) + 1

    for sec in spec["sections"]:
        sid = sec["id"]
        sec_dir_rel = f"sections/{sec['slug']}"
        sec_json = ws / f"02_section_{sid}.json"
        if not sec_json.exists():
            continue
        sec_data = json.loads(sec_json.read_text(encoding="utf-8"))

        classes_out = []
        for cls in sec_data.get("classes", []):
            cls_rel = f"{sec_dir_rel}/classes/{cls['slug']}"
            cls_abs = root / cls_rel

            slide_src = cls_abs / "slide.source.md"
            n_slides = count_slides(slide_src)
            total_slides += n_slides

            assets = {
                "slide_source": f"{cls_rel}/slide.source.md",
                "slide_html": f"{cls_rel}/slide.html" if (cls_abs / "slide.html").exists() else None,
                "note_md": f"{cls_rel}/note.md" if (cls_abs / "note.md").exists() else None,
                "transcript_txt": f"{cls_rel}/transcript.txt" if (cls_abs / "transcript.txt").exists() else None,
            }
            # SSML
            ssml = cls_abs / "transcript.ssml"
            if ssml.exists():
                assets["transcript_ssml"] = f"{cls_rel}/transcript.ssml"
            # Audio
            audio_dir = cls_abs / "audio"
            if (audio_dir / "full.mp3").exists():
                assets["audio_full"] = f"{cls_rel}/audio/full.mp3"
                slide_mp3s = sorted(f"{cls_rel}/audio/{p.name}"
                                    for p in audio_dir.glob("slide_*.mp3"))
                if slide_mp3s:
                    assets["audio_slides"] = slide_mp3s
                total_audio += mp3_duration(audio_dir / "full.mp3")
            # Slide PNGs
            png_dir = cls_abs / "slides_png"
            if png_dir.exists():
                pngs = sorted(f"{cls_rel}/slides_png/{p.name}" for p in png_dir.glob("slide.*.png"))
                if pngs:
                    assets["slide_pngs"] = pngs
            # Player HTML
            if (cls_abs / "player.html").exists():
                assets["player_html"] = f"{cls_rel}/player.html"
            # Remove None entries
            assets = {k: v for k, v in assets.items() if v is not None}

            classes_out.append({
                "id": cls["id"],
                "slug": cls["slug"],
                "title": cls["title"],
                "lo_ids": cls.get("lo_ids", []),
                "duration_min": cls.get("duration_min"),
                "assets": assets,
            })

        sec_entry = {
            "id": sid,
            "slug": sec["slug"],
            "title": sec["title"],
            "summary": sec.get("summary", ""),
            "lo_ids": [lo["id"] for lo in los if lo.get("section_id") == sid],
            "classes": classes_out,
        }
        # Quiz
        quiz_path = root / sec_dir_rel / "quiz.json"
        if quiz_path.exists():
            sec_entry["quiz_path"] = f"{sec_dir_rel}/quiz.json"
        # Section quiz HTML
        quiz_html = root / sec_dir_rel / "quiz.html"
        if quiz_html.exists():
            sec_entry["quiz_html"] = f"{sec_dir_rel}/quiz.html"
        sections_out.append(sec_entry)

    manifest = {
        "course": {
            "topic": spec["topic"],
            "audience": spec["audience"],
            "depth": spec["depth"],
            "language": spec["language"],
            "tone": spec["tone"],
            "total_duration_min": spec.get("total_duration_min"),
            "build_ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "harness_version": "1.1.0",
        },
        "learning_objectives": los,
        "sections": sections_out,
        "stats": {
            "sections": len(sections_out),
            "classes": sum(len(s["classes"]) for s in sections_out),
            "total_slides": total_slides,
            "lo_count": len(los),
            "bloom_distribution": bloom_dist,
            "actual_audio_duration_sec": round(total_audio, 1),
        },
    }
    # Player index HTML
    if (root / "index.html").exists():
        manifest["player_index"] = "index.html"

    out = root / "manifest.json"
    # Preserve TTS stats if previously written (tts_voice/tts_engine/tts_speed etc.)
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8"))
            for k, v in existing.get("stats", {}).items():
                if k.startswith("tts_"):
                    manifest["stats"].setdefault(k, v)
        except Exception:
            pass

    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    s = manifest["stats"]
    print(f"✓ manifest: {s['sections']} sections, {s['classes']} classes, "
          f"{s['total_slides']} slides, audio={s['actual_audio_duration_sec']}s")


if __name__ == "__main__":
    main()
