---
name: tts-synthesis
description: Synthesize TTS audio from course transcripts with pluggable engines (OpenAI gpt-4o-mini-tts default, edge-tts fallback). Use when turning a class transcript.txt into per-slide MP3s plus a concatenated full.mp3, handling [slide N] / [pause:ms] markers, retries, and per-slide speaker_affect overlays. Triggered after coherence-review passes and before/within asset-build, or as a standalone step. Also invoke for "오디오 생성", "TTS 합성", "강의 음성 만들어", "voice 변경", "speed 조정".
---

# TTS Synthesis — Pluggable Audio Pipeline

transcript.txt를 per-slide MP3 + full.mp3로 합성한다. **OpenAI `gpt-4o-mini-tts` + `nova` + speed 1.3**가 기본. edge-tts는 offline/무료 대안.

## 왜 이 스킬이 존재하는가
원래 하네스의 Non-Goal이었으나 Phase 7에서 확장. TTS 합성은 (1) transcript 마커 파싱, (2) 엔진별 API 호출, (3) pause 무음 삽입 + concat, (4) retry가 모두 얽혀있어 스크립트화하지 않으면 재사용이 어렵다.

## 실행

### 표준 호출
```bash
python3 scripts/synthesize-tts.py \
  course/sections/<sec>/classes/<cls>/transcript.txt \
  course/sections/<sec>/classes/<cls>/audio
```
위는 기본값 (openai + nova + speed 1.3 + default 친근 ko instructions)을 사용.

### 래퍼 (pipefail 보장)
```bash
bash .claude/skills/tts-synthesis/scripts/run.sh \
  <transcript.txt> <out_dir> [추가 플래그]
```
래퍼가 `set -o pipefail` + `tee`의 실제 exit 전파 + `.env` 로딩을 책임진다.

### 엔진 전환
```bash
# edge-tts로 (오프라인, rate limit 있음)
--engine edge --voice ko-KR-SunHiNeural

# OpenAI 다른 voice/모델
--voice shimmer
--model tts-1-hd   # 고음질, 비용 2배
--speed 1.0        # 원속도
```

## 입력 마커 규격
- `[slide N]` (줄 단독, N=1..) — TTS 후처리용 오디오 구간 분할 기준
- `[pause:Xms]` — 무음 삽입 (기본 300~800). **speed 파라미터에 영향받지 않음** (원본 유지, 사용자 확인된 선호)
- `[emph]...[/emph]` — SSML 변환 시 `<emphasis>` (OpenAI는 instructions로 대체)

## 출력 구조
```
<out_dir>/
  slide_01.mp3  ~  slide_NN.mp3   # 슬라이드별
  full.mp3                          # 전체 concat
```

## 에이전트/오케스트레이터 연결

현재는 오케스트레이터 Phase 5(asset-builder) 직후 사용자가 수동 호출. Phase 7 이후 **Phase 5.5**로 편입 후보:
```
... → Phase 5 (asset-builder: bundle.zip)
    → Phase 5.5 (tts-synthesis: per-class audio)
    → manifest 갱신 + 재빌드
```

편입 조건:
- `coherence_report.overall == "pass"` (slide↔script cue 정합 확인)
- `OPENAI_API_KEY` 존재 (없으면 edge로 자동 폴백)

## 품질 규칙

### Retry
transient 실패(edge-tts rate limit, OpenAI 429/5xx)는 **4회 exponential backoff**로 자동 복구.

### Idempotency
동일 transcript + 같은 파라미터 재실행 시 결과 파일 크기는 ±2% 내 일치 (TTS 자체의 미세 변동). `audio/` 디렉토리 통째로 삭제 후 재실행을 기본 전략으로.

### Speaker affect 주입 (Phase 7 확장)
`--beats <beats.json>`을 주면 slide별로 beat의 `speaker_affect`(hook=호기심, teach=차분, example=흥분, practice=질문, recap=확신)를 기본 instructions에 덧씌워 slide마다 다른 뉘앙스로 합성.

## 체크리스트
- [ ] transcript.txt에 `[slide N]` cue 존재, 순서 1부터 연속
- [ ] OPENAI_API_KEY 로딩됨 (engine=openai)
- [ ] out_dir 존재 또는 생성 가능
- [ ] 합성 후 slide_NN.mp3 개수 == transcript [slide N] 개수
- [ ] full.mp3 duration ≈ Σ(slide_NN.mp3) (±1%)
- [ ] retry 로그에 경고 있었는지 점검

## 참고
- 원본 스크립트: `scripts/synthesize-tts.py` (canonical, 이 스킬이 호출)
- 실측 char/sec rate: `skills/script-writing/SKILL.md` §"길이 계산"
- pause 보존 정책은 사용자 확정 (memory/feedback_tts_config.md)
