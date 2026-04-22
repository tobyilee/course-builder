#!/usr/bin/env python3
"""
Synthesize audio from a course transcript.txt.

Supports two TTS engines:
  --engine openai  (default) — uses gpt-4o-mini-tts with `instructions` for tone
  --engine edge    — uses edge-tts CLI (free, Microsoft)

Parses [slide N] (slide boundary) and [pause:ms] (silence) markers.
Per slide: synthesize each text chunk, insert silence via ffmpeg for pauses,
concat into slide_NN.mp3. Finally concat all slides into full.mp3.

Env:
  OPENAI_API_KEY — required when --engine openai

Usage:
  synthesize-tts.py <transcript.txt> <out_dir>
    [--engine openai|edge]
    [--model gpt-4o-mini-tts|tts-1|tts-1-hd]
    [--voice nova|coral|shimmer|...]
    [--rate +0%]                  # edge only
    [--instructions "tone hint"]  # openai only
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SLIDE_RE = re.compile(r'^\s*\[slide\s+(\d+)\]\s*$')
PAUSE_RE = re.compile(r'\[pause:(\d+)\]')

DEFAULT_INSTRUCTIONS_KO = (
    "친근하고 명료한 한국어 개발자 튜토리얼 강사 톤. "
    "자연스러운 호흡과 보통 속도. 질문은 살짝 올리고, 강조는 부드럽게. "
    "딱딱하지 않게, 하지만 집중력 있게."
)

DEFAULT_INSTRUCTIONS_EN = (
    "A friendly and clear English developer-tutorial narrator tone. "
    "Natural breath, moderate pace. Slight inflection rise for questions, "
    "soft emphasis. Conversational yet focused."
)

# Affect overlay — maps beat.speaker_affect substring to extra tone instruction.
# Substring match (beat sheets may use compound phrases like "호기심 유발" / "curious and warm").
AFFECT_OVERLAYS_KO = {
    "호기심": "호기심을 자극하는 질문형 톤. 문장 끝을 살짝 올리고 기대감을 실어라.",
    "미스터리": "약간 비밀스럽고 기대감 있는 톤. 정답을 바로 노출하지 말 것.",
    "단호": "단호하고 선언적인 톤. 결론을 분명하게, 군더더기 없이.",
    "친근": "친근하고 편안한 대화 톤. 축약어를 자연스럽게.",
    "차분": "차분하고 또렷한 설명 톤. 안정된 호흡으로.",
    "명료": "명료하고 단정한 설명 톤. 애매한 수식어 최소화.",
    "가이드": "한 단계씩 안내하는 차분한 가이드 톤.",
    "흥분": "라이브 데모 같은 생동감 있는 톤. 에너지를 실어서.",
    "라이브": "실제 시연하듯 생생한 톤.",
    "시연": "눈앞에서 보여주는 듯한 생생한 톤.",
    "질문": "질문하는 톤. 답을 유도하는 느낌으로.",
    "여백": "학습자가 생각할 여백을 두는 톤.",
    "침묵": "답을 기다리는 듯한 여유 있는 톤.",
    "확신": "확신에 찬 정리 톤. 힘있게 마무리.",
    "엄숙": "진중한 톤.",
    "공감": "공감하는 따뜻한 톤.",
    "정리": "핵심을 추리는 정리 톤.",
}

AFFECT_OVERLAYS_EN = {
    "curious": "Curious, question-evoking tone. Raise inflection at sentence ends to imply anticipation.",
    "mystery": "Mildly cryptic, anticipatory tone. Don't reveal the answer too soon.",
    "firm": "Firm, declarative tone. Clear conclusions, no filler.",
    "decisive": "Decisive tone. Minimize hedging.",
    "friendly": "Friendly, conversational tone with natural contractions.",
    "warm": "Warm, empathetic tone.",
    "calm": "Calm, clear explanatory tone with steady pacing.",
    "crisp": "Crisp, precise tone. Avoid vague qualifiers.",
    "guide": "Patient, step-by-step guide tone.",
    "excited": "Lively demo tone with energy.",
    "live": "Feels like a live demo — genuinely in the moment.",
    "demo": "As if demonstrating right in front of the learner.",
    "question": "Questioning tone. Invite the learner to think along.",
    "space": "Leave breathing space for the learner to think.",
    "pause": "Patient-pause tone — room for thought.",
    "confident": "Confident closing tone. Wrap up firmly.",
    "serious": "Serious, weighty tone.",
    "empathy": "Warm, empathetic tone.",
    "summary": "Summarizing tone that distills the essentials.",
    "emphasis": "Emphatic tone. Deliver key points with weight.",
}


def affect_to_instruction(affect: str, base: str, language: str = "ko") -> str:
    """Overlay matching affect entries onto base instructions (language-aware)."""
    if not affect:
        return base
    overlays = AFFECT_OVERLAYS_EN if language == "en" else AFFECT_OVERLAYS_KO
    affect_l = affect.lower()
    hits = [v for k, v in overlays.items() if k.lower() in affect_l]
    if not hits:
        return base
    suffix = " Additional tone: " if language == "en" else " 추가 톤 지시: "
    return base + suffix + " ".join(hits)


def build_slide_to_affect(beats_path: Path, slide_count: int) -> dict:
    """Map slide_no (1-indexed) to affect string by stretching beats over slides.

    Convention: slide 1 = title (no beat, neutral). slides 2..slide_count map
    proportionally to beats[0..N-1]. If slides > beats+1, beats stretch (one
    beat covers multiple slides); if slides < beats+1, trailing beats collapse.
    """
    data = json.loads(beats_path.read_text(encoding="utf-8"))
    beats = data.get("beats", [])
    if not beats:
        return {}

    mapping = {1: ""}  # title slide uses base instructions
    content_slides = max(slide_count - 1, 1)
    for i in range(content_slides):
        beat_idx = min(int(i * len(beats) / content_slides), len(beats) - 1)
        mapping[i + 2] = beats[beat_idx].get("speaker_affect", "")
    return mapping


def parse_transcript(text: str):
    slides = []
    current = None
    for line in text.splitlines():
        m = SLIDE_RE.match(line)
        if m:
            current = {"slide_no": int(m.group(1)), "raw": ""}
            slides.append(current)
            continue
        if current is None:
            continue
        current["raw"] += line + "\n"

    for s in slides:
        chunks = []
        tokens = re.split(r'(\[pause:\d+\])', s["raw"])
        buf = ""
        for tok in tokens:
            if not tok:
                continue
            pm = PAUSE_RE.fullmatch(tok)
            if pm:
                if buf.strip():
                    chunks.append({"text": buf.strip(), "pause_after_ms": int(pm.group(1))})
                    buf = ""
                else:
                    if chunks:
                        chunks[-1]["pause_after_ms"] += int(pm.group(1))
            else:
                buf += tok
        if buf.strip():
            chunks.append({"text": buf.strip(), "pause_after_ms": 0})
        s["chunks"] = chunks
    return slides


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


# ── TTS backends ──────────────────────────────────────────────────────────

def tts_edge(text: str, out_path: Path, voice: str, rate: str, **_):
    run([
        "edge-tts",
        "-v", voice,
        "--rate", rate,
        "-t", text,
        "--write-media", str(out_path),
    ])


_OPENAI_CLIENT = None

def _openai_client():
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        try:
            from openai import OpenAI
        except ImportError:
            sys.exit("ERROR: `openai` package not installed. Run: pip install openai")
        if not os.environ.get("OPENAI_API_KEY"):
            sys.exit("ERROR: OPENAI_API_KEY not set in environment.")
        _OPENAI_CLIENT = OpenAI()
    return _OPENAI_CLIENT


def tts_openai(text: str, out_path: Path, voice: str, model: str, instructions: str,
               speed: float = 1.0, **_):
    client = _openai_client()
    kwargs = dict(model=model, voice=voice, input=text, response_format="mp3", speed=speed)
    # Only gpt-4o-mini-tts supports `instructions`
    if instructions and model.startswith("gpt-4o"):
        kwargs["instructions"] = instructions
    with client.audio.speech.with_streaming_response.create(**kwargs) as resp:
        resp.stream_to_file(str(out_path))


ENGINES = {"openai": tts_openai, "edge": tts_edge}


def with_retry(fn, max_retries=4, base_delay=1.5):
    """Retry transient TTS failures (edge-tts rate limits, OpenAI 429/5xx)."""
    def wrapped(*a, **kw):
        last_err: Exception = RuntimeError("retry exhausted")
        for i in range(max_retries):
            try:
                return fn(*a, **kw)
            except Exception as e:
                last_err = e
            if i < max_retries - 1:
                delay = base_delay * (2 ** i)
                print(f"    ⚠ retry {i+1}/{max_retries-1} in {delay:.1f}s: {type(last_err).__name__}",
                      flush=True)
                time.sleep(delay)
        raise last_err
    return wrapped


# ── ffmpeg helpers ────────────────────────────────────────────────────────

def silence(ms: int, out_path: Path):
    sec = max(ms, 1) / 1000.0
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", f"{sec}",
        "-c:a", "libmp3lame", "-b:a", "48k", "-ar", "24000", "-ac", "1",
        str(out_path),
    ])


def concat(parts, out_path: Path):
    list_file = out_path.parent / (out_path.stem + "_list.txt")
    list_file.write_text("\n".join(f"file '{p.name}'" for p in parts) + "\n")
    try:
        run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file.name,
            "-c:a", "libmp3lame", "-b:a", "48k", "-ar", "24000", "-ac", "1",
            out_path.name,
        ], cwd=str(out_path.parent))
    finally:
        list_file.unlink(missing_ok=True)


# ── main ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--engine", choices=list(ENGINES), default="openai")
    ap.add_argument("--language", choices=["ko", "en"], default="ko",
                    help="course language — drives default voice, instructions, and affect overlay map")
    ap.add_argument("--model", default="gpt-4o-mini-tts",
                    help="openai only: gpt-4o-mini-tts | tts-1 | tts-1-hd")
    ap.add_argument("--voice", default=None,
                    help="openai: nova|coral|shimmer|... (multilingual) ; "
                         "edge: ko-KR-SunHiNeural (ko) | en-US-AriaNeural (en)")
    ap.add_argument("--rate", default="+0%", help="edge only")
    ap.add_argument("--instructions", default=None,
                    help="openai gpt-4o only: tone instructions (defaults by --language)")
    ap.add_argument("--speed", type=float, default=1.3,
                    help="openai only: 0.25–4.0, default 1.3 (30%% faster than natural)")
    ap.add_argument("--beats", type=Path, default=None,
                    help="optional beats.json — enables per-slide speaker_affect overlay")
    args = ap.parse_args()

    if args.voice is None:
        if args.engine == "openai":
            args.voice = "nova"  # multilingual (handles both ko and en)
        else:
            args.voice = "en-US-AriaNeural" if args.language == "en" else "ko-KR-SunHiNeural"

    if args.instructions is None:
        args.instructions = DEFAULT_INSTRUCTIONS_EN if args.language == "en" else DEFAULT_INSTRUCTIONS_KO

    if not args.transcript.exists():
        sys.exit(f"ERROR: {args.transcript} not found")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tts_fn = with_retry(ENGINES[args.engine])
    tts_kwargs = dict(voice=args.voice, rate=args.rate, model=args.model,
                      instructions=args.instructions, speed=args.speed)

    slides = parse_transcript(args.transcript.read_text(encoding="utf-8"))
    if not slides:
        sys.exit("ERROR: no [slide N] markers found in transcript")

    # Build slide → affect map if beats file provided
    slide_affect = {}
    if args.beats and args.beats.exists():
        slide_affect = build_slide_to_affect(args.beats, len(slides))
        print(f"Affect overlay: ON ({len(slide_affect)} slides mapped from {args.beats.name})")
    elif args.beats:
        print(f"⚠ --beats {args.beats} not found, using base instructions only")

    print(f"Engine: {args.engine} / Language: {args.language} / Voice: {args.voice}"
          + (f" / Model: {args.model} / Speed: {args.speed}x" if args.engine == "openai" else ""))

    slide_mp3s = []
    for s in slides:
        n = s["slide_no"]
        affect = slide_affect.get(n, "") if slide_affect else ""
        slide_instructions = affect_to_instruction(affect, args.instructions, args.language)
        affect_tag = f" [{affect}]" if affect else ""
        print(f"  → slide {n}: {len(s['chunks'])} chunks{affect_tag}", flush=True)
        parts = []
        per_slide_kwargs = {**tts_kwargs, "instructions": slide_instructions}
        for i, ch in enumerate(s["chunks"]):
            chunk_mp3 = args.out_dir / f"_tmp_s{n:02d}_c{i:02d}.mp3"
            tts_fn(ch["text"], chunk_mp3, **per_slide_kwargs)
            parts.append(chunk_mp3)
            if ch["pause_after_ms"] > 0:
                # Scale pauses by speed so "30% faster" covers breathing pauses too
                effective_ms = int(ch["pause_after_ms"] / max(args.speed, 0.01))
                if effective_ms >= 50:  # floor: don't produce imperceptible blips
                    sil = args.out_dir / f"_tmp_s{n:02d}_c{i:02d}_p.mp3"
                    silence(effective_ms, sil)
                    parts.append(sil)
        slide_mp3 = args.out_dir / f"slide_{n:02d}.mp3"
        concat(parts, slide_mp3)
        for p in parts:
            p.unlink(missing_ok=True)
        slide_mp3s.append(slide_mp3)

    full = args.out_dir / "full.mp3"
    concat(slide_mp3s, full)
    total = sum(p.stat().st_size for p in slide_mp3s) + full.stat().st_size
    print(f"✓ {len(slide_mp3s)} slide mp3s + full.mp3 ({total/1024:.1f} KB total)")


if __name__ == "__main__":
    main()
