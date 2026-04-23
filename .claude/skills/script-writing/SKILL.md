---
name: script-writing
description: Write TTS-ready transcripts with [slide N] cues, [pause:ms] markers, and optional SSML. Convert raw code/URLs/long numbers to speakable forms. Use when turning slides+beats into a narrator script. Triggered by the script-writer agent.
---

# Script Writing — Speakable Transcript

transcript는 **귀로 듣는 콘텐츠**다. note를 그대로 낭독하면 부자연스럽다. 문장 길이, 리듬, 호흡, 강조를 음성 기준으로 재설계.

## 구조 (plain text)

```
[slide 1]
첫 문장. 리듬을 위한 짧은 문장.
[pause:400]
두 번째 문장은 조금 더 길어도 괜찮지만 25 단어를 넘지 않도록 합니다.
[pause:600]
핵심 강조 전에는 조금 더 쉬어줍니다.

[slide 2]
새 슬라이드로 넘어갑니다.
...
```

## 규칙

### 문장 길이
- 영어 ≤25 단어, 한국어 ≤20 어절
- 한 호흡에 읽을 수 있는 길이

### 축약·구어체 허용
- "그래서 이게 뭐냐면", "이게 꽤 중요합니다"
- 너무 문어적 표현 지양 ("기인한다" → "때문입니다")

### Cue와 Marker

| 태그 | 용도 | 예 |
|------|------|-----|
| `[slide N]` | TTS 후처리 시 오디오 구간 분할 | `[slide 3]` |
| `[pause:ms]` | 문장 사이 호흡 | `[pause:400]` |
| `[emph]...[/emph]` | 강조 (SSML 변환 시 emphasis) | `[emph]중요[/emph]` |

pause 권장값:
- 문장 사이: 300~400ms
- 문단 전환: 600~800ms
- 강조/질문 후: 800~1200ms
- 슬라이드 전환 후 첫 문장 앞: 500ms

## Unspeakable 변환 (핵심)

### Raw code literal → 설명형
- ❌ `const x = () => { return 1; }`
- ✅ "const 키워드로 x를 선언하고, 화살표 함수로 1을 반환합니다"

### 긴 숫자 → 구어
- ❌ "3.14159265358979"
- ✅ "파이, 약 3.14"
- ❌ "403,825개"
- ✅ "약 40만 개"

### URL → 이름
- ❌ "https://react.dev/learn/server-components"
- ✅ "React 공식 문서의 서버 컴포넌트 페이지"

### 심볼·이모지 → 설명 또는 제거
- ❌ "Use 👉 this"
- ✅ "이것을 사용하세요"

## 길이 계산

문자/분 속도는 **voice와 TTS 엔진, speed 설정에 따라 달라진다**. 아래 실측 표 기반:

### Voice별 발화 속도 (char/sec, speed=1.0 기준)

| 엔진 | Voice | ko 실측 | en 실측 |
|------|-------|---------|---------|
| OpenAI `gpt-4o-mini-tts` | `nova` | ≈4.3 | ≈3.8 (est.) |
| OpenAI `tts-1` / `tts-1-hd` | 기본값 | ≈4.2 | ≈3.7 (est.) |
| edge-tts | `ko-KR-SunHiNeural` | ≈4.3 | — |
| edge-tts | `en-US-*Neural` | — | ≈3.5 |

> 2026-04-22 실측 — 13~14 슬라이드 단위 표본 기반. 추가 voice/언어는 실행 시 보강.

### Script 길이 공식 (Bloom/affect에 관계없이 duration 목표 역산)

```
# 변수: rate_cps = 위 표의 char/sec, speed = TTS speed 파라미터 (기본 1.0)
script_length_chars ≈ target_duration_sec × rate_cps × speed

# 예: ko nova speed=1.3, 10분 class 목표
= 600 × 4.3 × 1.3 ≈ 3354자
```

pause 구간은 ±5~15% 추가로 차지하니 텍스트 목표는 97%~85%로 보수적으로.

### 이전 공식과의 차이
v1의 단일 공식(2.7 chars/sec)은 **Neural voice의 실제 속도(≈4.3)를 크게 과소평가** — 스크립트가 target보다 60% 길어지는 경향 있었음. 하네스 초기 실행에서 estimate 1,127s vs 실측 713s의 36% 갭으로 확인.

### Prior-run calibration (자동 보정, 권장)

같은 주제·언어로 재실행할 때는 정적 `rate_cps` 테이블 대신 **이전 run의 실측값**을 사용해 per-class로 보정한다.

입력: `course_prev_*/manifest.json` 의 `sections[].classes[].actual_audio_duration_sec` (synth-manifest.py 가 기록) + 해당 class의 `duration_min` target.

```
if prior_manifest exists and class_id matches:
    prev_actual_sec = prev_class.actual_audio_duration_sec
    prev_target_sec = prev_class.duration_min * 60
    calib = prev_actual_sec / prev_target_sec    # 1.08 = 8% over, 0.92 = 8% under
    calib = max(0.7, min(1.4, calib))            # safety clamp — 극단값 무시
    adjusted_char_budget = (target_duration_sec × rate_cps × speed) / calib
else:
    adjusted_char_budget = target_duration_sec × rate_cps × speed
```

동작 원리:
- 이전 run이 target보다 **길었으면** (calib > 1) 다음 run은 char budget을 **줄인다**.
- 짧았으면 늘린다.
- clamp `[0.7, 1.4]` 는 rate_cps 테이블 자체가 크게 틀린 초기 run에서 과보정 폭주 방지용.

### 보정 실패 대응 (fallback)
prior_manifest가 없거나 class_id 매칭 실패 시, 또는 calib 적용 후에도 실제 duration이 target ±10% 벗어나면:
- 너무 짧음: beat의 `key_points`에 구체 예시 1개 추가
- 너무 김: 중복 부연 제거, teach beat를 2개로 분할한 뒤 각 분량 축소

±10% 이내 맞춤.

## [slide N] 매핑

slide.source.md의 슬라이드 번호 순서와 정확히 일치해야 한다.
- 슬라이드 1 = 제목 슬라이드 (언급하고 넘어감, 20~30s)
- 슬라이드 N = recap (강조하며 마무리)

coherence-reviewer는 이 매핑을 검증한다.

## SSML 변형

사용자가 요청하거나 `language != ko`일 때 `transcript.ssml` 추가 생성.

```xml
<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="ko-KR">
  <p>
    <s>첫 문장입니다.</s>
    <break time="400ms"/>
    <s>다음 문장은 조금 <emphasis level="moderate">강조</emphasis>합니다.</s>
  </p>
</speak>
```

- `<speak>` 루트, `xml:lang` 필수
- `[pause:X]` → `<break time="Xms"/>`
- `[emph]X[/emph]` → `<emphasis level="moderate">X</emphasis>`
- `[slide N]` → SSML에서는 `<mark name="slide_N"/>`로 변환

`scripts/validate-ssml.sh`로 W3C SSML 1.1 스키마 검증.

## Speaker affect 반영
class-planner의 `speaker_affect` 필드를 문체·속도에 반영:
- `호기심`: 질문 끝 억양, 짧은 문장
- `단호`: 명사형 종결, 중간 pause 최소
- `친근`: 축약 적극, 감탄사 OK
- `엄숙`: 장문, 수식어 절제

## 재실행 규칙
- slide 수 변경되면 [slide N] 전체 재매핑
- 톤 변경은 전체 재작성 (부분 교체하면 위화감)

## 체크리스트
- [ ] 모든 문장 ≤25 단어 (한국어 ≤20 어절)
- [ ] raw code/긴 숫자/URL 없음
- [ ] `[slide N]` cue 수 == slide.source.md 슬라이드 수
- [ ] 추정 duration이 beats 총합 ±10% 이내
- [ ] tone 파라미터 일관 유지
- [ ] SSML 생성 시 xsd 검증 통과
