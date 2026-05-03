# AI Course Builder

## 하네스: AI Online Course Builder

**Version:** `1.1.0` (단일 진실원: 프로젝트 루트 [`VERSION`](VERSION) 파일. `course/manifest.json` 의 `course.harness_version` 에 자동 주입.)

**목표:** 주제 입력만으로 ADDIE + Bloom's Taxonomy 기반의 온라인 강의(Section → Class, 각 Class에 HTML slide + MD note + TTS transcript, Section 단위 quiz 5~9문항)를 자동 생성한다.

**트리거:** 강의·코스·커리큘럼 생성/설계/제작 요청 시 `course-builder` 스킬을 사용하라. "강의 만들어줘", "온라인 코스 설계", "커리큘럼 짜줘", "슬라이드+노트+스크립트", "TTS 강의", "섹션별 퀴즈 포함 강의", "이 주제로 강의 만들어", "코스 재실행", "섹션만 다시" 등이 트리거. 영어 요청도 동일 스킬 트리거: "make a course on X", "build a curriculum for X", "design a lecture for X". 단순 질문(이론 설명·정의 조사)은 직접 응답.

**언어 지정:** Course 생성 요청의 language는 기본 `ko`. 사용자가 "영어로", "in English", "English course", "영문으로 만들어줘" 등을 명시하면 `language="en"`으로 orchestrator에 전달 — slide·note·transcript·quiz·audio·player UI 전부 영어로 생성. 요청 언어로부터 자동 추정하지 말 것(예: 사용자가 영어로 물어봤다고 해서 영어 강의로 가정 금지; 명시 필요).

**작업 디렉토리:** `course/` (산출물), `_workspace/` (중간 산출물, 재실행 시 `_workspace_prev/`로 이동).

**transcript.txt 형식:** 슬라이드 내레이션을 **문장 단위로 한 줄씩** 분리해 쓰고, `[pause:NNN]`/`[slide N]` 마커는 **각자 단독 줄**에 둔다. 한 슬라이드 텍스트를 한 줄에 몰아쓰면 `generate-player.py`가 자막 추적을 못 해 한 덩어리로 렌더된다. 규칙은 `.claude/skills/script-writing/SKILL.md`의 "Line layout" 참조.

**변경 이력:**

| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-04-26 | 초기 구성 (9 에이전트, 9 도메인 스킬 + course-builder 오케스트레이터) | 전체 | - |
| 2026-04-26 | TTS 합성 통합 (Phase 7 확장) | `tts-synthesis` 스킬, `build-bundle.sh` step 3 | one-shot 빌드 사용성 |
| 2026-04-26 | Partial re-run scope 토큰 (`S<n>.C<m>`, byte-identity 보존) | `course-builder` Phase 0, `architect`/`quiz-master` 에이전트 | 부분 재생성 안정성 |
| 2026-04-26 | Coherence reviewer atomic dual-write + verdict mismatch gate | `coherence-review` 스킬, `build-bundle.sh` | JSON=pass / MD=REVISE 빌드 사고 재발 방지 |
| 2026-04-26 | Marp `data:` URI 금지 + 이미지 문법 정확화 | `slide-authoring` 스킬 | render 누락 사고 |
| 2026-04-26 | Transcript line-layout 규정 (한 줄 1 문장, 마커 단독 줄) | `script-writing` 스킬, `script-writer` 에이전트 | subtitle-sync 깨짐 방지 |
| 2026-05-04 | **버전 도입 1.1.0** — 프로젝트 루트 `VERSION` 파일을 단일 진실원으로 도입 | `VERSION`, `synth-manifest.py`, `README.md`, `CLAUDE.md` | 하네스 진화 추적성 |
| 2026-05-04 | `tts-synthesizer` 에이전트 신설 (TTS 책임 단일화) | `.claude/agents/tts-synthesizer.md`, `course-builder` Phase 5, `tts-synthesis` 스킬, `asset-builder` 에이전트 | 스킬-에이전트 짝맞춤 회복 (TTS 책임 분산 해소) |
| 2026-05-04 | `course-builder` Phase 5 명세를 `build-bundle.sh` 실제 8 step과 동기화 | `course-builder` 스킬 | 명세↔동작 drift 해소 |
| 2026-05-04 | `build-bundle.sh` ffmpeg 검사를 TTS 실행 시점으로 지연 | `asset-build/scripts/build-bundle.sh` | slides-only 빌드(`SKIP_TTS=1`) 사용 사례 회복 |
| 2026-05-04 | `section-designer`/`class-planner`/`slide-author`/`note-writer`/`script-writer` 에 partial re-run 지침 표준화 (Edit 강제, byte-identity, diff-before-claim) | 5개 에이전트 | 부분 재실행 시 자산 보존 누락 방지 |
| 2026-05-04 | HITL 체크포인트 메커니즘 표준 (요약 제시 / 3지선다 / `97_hitl_log.md` 기록) | `course-builder` Phase 0-4 | 체크포인트 실행 재현성 |

