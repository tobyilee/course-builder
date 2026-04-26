# React 상태 관리 심화 — Course Summary (auto-generated)

> Source: `react.dev/learn/managing-state` (7 chapters, fully covered)
> Audience: 중급 React 개발자 (TypeScript / JavaScript / 컴포넌트 능숙, state 영역 약함)
> Language: ko · Tone: friendly · Total: ~300 min (5h)

## Pipeline phases (executed)

| # | Phase | Status | Output |
|---|---|---|---|
| 1 | Curriculum design | ✅ | 9 sections, 26 classes, 35 LOs (6 Bloom levels) |
| 2 | Content authoring | ✅ | 26 slide decks (Marp), 26 notes, 26 transcripts |
| 3 | Section quizzes | ✅ | 9 quizzes, 67 items, 100% LO test coverage |
| 4 | Coherence review | ✅ | PASS (after 6 errors patched in-place) |
| 5 | Build | ✅ | Marp HTML+PNG, TTS (11,758s = 196 min), manifest, 26 player HTMLs + 9 quiz HTMLs + index.html, **bundle.zip 143MB** |

## Section map (300 min total)

| id | slug | title | min | classes |
|---|---|---|---|---|
| S0 | 00-orientation | 오리엔테이션 — 왜 state 설계가 따로 필요한가 | 20 | 2 |
| S1 | 01-declarative-thinking | 선언형 UI와 visual states로 반응하기 | 35 | 3 |
| S2 | 02-state-structure | state 구조 설계 — 5가지 원칙 | 40 | 4 |
| S3 | 03-sharing-state | 컴포넌트 간 state 공유 — Lifting State Up | 35 | 3 |
| S4 | 04-preserving-resetting-state | state 보존과 리셋 — 트리 위치와 key prop | 40 | 3 |
| S5 | 05-reducer | Reducer로 state 로직 추출하기 | 45 | 4 |
| S6 | 06-context | Context로 깊이 데이터 전달하기 | 40 | 3 |
| S7 | 07-reducer-context | Reducer + Context로 확장하기 | 30 | 2 |
| S8 | 08-capstone-antipatterns | 종합 — 안티패턴 진단과 통합 케이스 스터디 | 15 | 2 |

## Bloom distribution (35 LOs)

| Level | Count | % |
|---|---|---|
| Remember | 2 | 6% |
| Understand | 7 | 20% |
| Apply | 10 | 29% |
| Analyze | 7 | 20% |
| Evaluate | 5 | 14% |
| Create | 4 | 11% |

**Apply / Analyze / Evaluate / Create = 74%** — Bloom분포가 중급 이상 강의에 적합 (Remember ≤ 15% 충족).

## Asset volume

- Slides: 207 (avg 8 per class)
- Transcript words: 27,744 어절 (Korean)
- Notes: 102,068 chars
- Quiz items: 67
- Source pages researched: 8 (chapter overview + 7 sub-chapters)

## TTS settings

- Engine: OpenAI `gpt-4o-mini-tts`
- Voice: `nova`
- Speed: 1.3x
- Pause compression: same ratio (no expansion)

## Coherence patches applied (2026-04-27)

1. S1.C2 transcript — dropped invalid `[slide 10]` cue, merged narration into slide 9
2. S1.C3 transcript — same
3. S4.C3 transcript — rewrote `(state, action) => nextState` literal as Korean prose ("현재 state와 액션을 받아 다음 state를 돌려주는 순수 함수")
4. S8.C1 note — fixed `[S2.C5]→[S2.C4]`, `[S4.C4]→[S4.C3]`, `[S6.C4]→[S6.C3]` (×2)
5. S8.C2 note — fixed `[S2.C5]→[S2.C4]` (×2), `[S7.C3]→[S7.C2]`, `[S7.C4]→[S7.C2]`

## Build outputs (post-Phase-5)

- `course/index.html` — learner entry point with TOC
- `course/sections/<sec>/quiz.html` — interactive quiz per section
- `course/sections/<sec>/classes/<cls>/player.html` — slide+audio+transcript player
- `course/manifest.json` — full course metadata
- `course/build/bundle.zip` — deployable package
- `_workspace/98_build_log.txt` — build trace
