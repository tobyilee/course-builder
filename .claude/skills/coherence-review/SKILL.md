---
name: coherence-review
description: Cross-artifact QA for the course pipeline. Verify LO coverage, Bloom balance, slide↔script cue alignment, note↔slide consistency, tone, quiz factual validity, and transcript speakability. Use when reviewing generated course assets before build. Triggered by the coherence-reviewer agent.
---

# Coherence Review — Cross-Boundary QA

개별 자산 검증이 아니라 **자산 간 경계면** 검증이 핵심. "slide가 있는가" 보다 "slide와 transcript가 같은 이야기를 하는가"가 훨씬 중요하다.

## 검사 순서 (fail-fast)

중요도·실행비용 순으로 정렬. 상위 단계 실패 시 하위는 수행하되 리포트에 "의존 실패" 표시.

### 1. Structural presence
모든 예상 파일 존재 확인.
```
course/manifest.json OR _workspace/01_*
course/meta/learning_objectives.json
course/sections/<sec>/section.json
course/sections/<sec>/classes/<cls>/{slide.source.md,slide.html,note.md,transcript.txt}
course/sections/<sec>/quiz.json
```

### 2. LO Coverage (critical)
모든 LO는 다음 3개소에 ≥1 등장:
- slide.source.md (footer or body)
- note.md (blockquote 헤더 or 본문 언급)
- quiz.json (lo_ids 필드)

측정: LO registry를 grep으로 전수 검사.

### 3. Bloom Balance
- 섹션당 Bloom 레벨 ≥3
- Course 전체 ≥4
- Apply+Analyze quiz 합 ≥2 / 섹션

### 4. Slide ↔ Script 정합
- `slide.source.md`의 `---` 구분 슬라이드 수 N
- `transcript.txt`의 `[slide N]` cue 최대값 M
- N == M 필수

### 5. Note ↔ Slide 정합
- note.md의 `[slide K]` 모든 K가 1~N 범위
- note가 slide에 없는 새 개념 도입 시 warning (가능하지만 위험)

### 6. Tone 일관성
- course_spec의 `tone` 파라미터와 실제 자산 톤 비교
- 한 class 안에서 반말/존댓말 혼재 감지 (한국어)
- 문체 급변 감지 (정규 ML 불필요, 단순 휴리스틱으로 충분)

### 7. Quiz 사실 검증
- quiz 정답이 note/slide 내용과 모순되는지
- distractor가 실제로 오답인지 (가끔 AI가 정답을 distractor에 넣음)

### 8. Transcript Speakability
- raw code literal: `` ` ``(backtick) 포함 여부
- 긴 숫자: `\d{4,}` 정규식 **— 단, 대괄호 디렉티브 `[pause:N]`, `[slide N]`, `[emph]...[/emph]` 내부 숫자는 제외 (TTS 후처리용 마커이지 발화 대상 아님)**. 구현: 먼저 `\[(pause|slide|emph|/emph)[^\]]*\]` 패턴을 공백으로 치환한 뒤 숫자 검사.
- 생 URL: `https?://` 검출
- 문장 길이: 20 어절 초과 문장 비율

## 판정 로직

```
if (1) fails:
  overall = "revise"; 중단
if (2) 어떤 LO가 0회 등장:
  overall = "revise"
if (3) Bloom 부족:
  overall = "revise"
if (4) cue 수 불일치:
  overall = "revise"
if (5~8) any fail:
  overall = "revise"
else:
  overall = "pass"
```

## 리포트 포맷

**원칙: atomic dual-write.** JSON과 MD를 동일 라운드의 동일 verdict로 한 번에 기록. 중간 저장 후 한 쪽만 overwrite하면 machine gate(JSON)와 사람이 보는 리포트(MD)가 엇갈림 — 실제로 과거 run에서 JSON=pass / MD=REVISE 상태로 빌드가 "성공"한 사례 있음.

### `_workspace/99_coherence_report.json` (machine contract)
```json
{
  "overall": "revise" | "pass",
  "timestamp": "...",
  "course_level": {
    "lo_coverage_pct": 95,
    "bloom_levels": 4,
    "issues": [{"type":"bloom_gap","detail":"..."}]
  },
  "sections": [
    {"section_id":"S1","verdict":"pass","issues":[]}
  ],
  "classes": [
    {"class_id":"S1.C1","verdict":"revise",
     "issues":[
       {"type":"slide_script_mismatch",
        "detail":"slide has 5, script has [slide 6] cue",
        "fix_hint":"Remove [slide 6] from transcript or add slide",
        "route_to":"script-writer"}
     ]}
  ]
}
```

### `_workspace/99_coherence_report.md` (human summary)
사람이 읽는 요약, top-5 이슈를 글로. **필수 구조**:
```markdown
# Coherence Review — <scope>

**Scope:** ...
**Language spec:** ...
**Reviewer run:** <date>

## VERDICT: PASS   ← 또는 REVISE (반드시 두 번째 H2)
```

### Verdict 동기화 (필수)
JSON `.overall` 과 MD `## VERDICT:` 헤더는 **같은 verdict 를 가리켜야** 하며, 매칭은 **case-insensitive**:

| JSON `overall` | MD 헤더 (권장)       | MD 헤더 (허용)       |
|----------------|----------------------|----------------------|
| `"pass"`       | `## VERDICT: PASS`   | `## VERDICT: pass`   |
| `"revise"`     | `## VERDICT: REVISE` | `## VERDICT: revise` |

쓰기 전 마지막 체크: `jq -r '.overall' report.json` == `grep -m1 '^## VERDICT:' report.md` 의 verdict 토큰을 **소문자로 정규화** 후 비교. `build-bundle.sh` gate 도 동일 방식으로 비교 (lowercase normalize 후 일치 검사 → WARN on mismatch).

### Revise 루프 종료 처리
최종 PASS가 확정되면 **JSON/MD 모두 overwrite**. 이전 라운드 MD가 "REVISE" 상태로 남아있으면 build는 pass하지만 사람이 읽는 리포트는 거짓을 말함. 이전 라운드를 보존하려면 `99_coherence_report.round_<N>.{json,md}` 로 분리해 저장.

## 수정 라우팅 (SendMessage)

revise 판정 시 각 이슈를 담당 에이전트에 직접 전달:

| Issue type | route_to |
|-----------|----------|
| lo_gap (slide) | slide-author |
| lo_gap (note) | note-writer |
| lo_gap (quiz) | quiz-master |
| slide_script_mismatch | script-writer |
| note_slide_ref_invalid | note-writer |
| tone_drift | 해당 저자 |
| quiz_factual_error | quiz-master |
| speakability_violation | script-writer |
| bloom_gap (section) | quiz-master |
| bloom_gap (course) | curriculum-architect |

각 메시지 포맷:
```
REVISE <artifact_id> <issue_type> | detail: ... | fix_hint: ...
```

## Revision Loop 제한
- 같은 이슈 2회 revise 후에도 fail이면 오케스트레이터에 human-in-the-loop 요청
- 무한 루프 방지: 이슈 id + 수정 라운드를 리포트에 누적

## 체크리스트
- [ ] 8단계 검사 모두 수행
- [ ] LO registry 전수 검사
- [ ] slide/script cue 개수 매칭
- [ ] tone 일관성 (sampling 기반)
- [ ] quiz 사실성 (slide/note와 대조)
- [ ] speakability grep 규칙 통과
- [ ] 리포트 json + md **atomic dual-write** (동일 소스 데이터, 동일 verdict)
- [ ] **Verdict sync 검증**: JSON `overall` ↔ MD `## VERDICT:` 일치
- [ ] revise 시 수정 라우팅 메시지 발송
- [ ] revise 루프 종료 시 두 파일 모두 최종 verdict로 overwrite (이전 REVISE 잔재 제거)
