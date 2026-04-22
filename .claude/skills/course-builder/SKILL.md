---
name: course-builder
description: Orchestrate end-to-end online course generation from a topic. Invoke when user asks to "create a course", "design a curriculum", "build online lectures", "강의 만들어", "코스 설계", "커리큘럼 짜", "섹션별 퀴즈 포함 강의", "TTS 스크립트 강의", or any request to produce structured learning material with slides + notes + scripts + quizzes. Also invoke for follow-ups — "재실행", "섹션만 다시", "업데이트", "이전 결과 개선", "코스 수정". Do NOT invoke for single-artifact requests (just a slide, just a quiz) — those should call the specific authoring skill directly.
---

# Course Builder — Orchestrator

멀티 에이전트 파이프라인으로 온라인 강의 전체를 생성한다. ADDIE + Bloom's Taxonomy를 백본으로, 9개 전문 에이전트가 파일 기반 공유 상태(`_workspace/`)와 팀 메시지로 협업한다.

## Phase 0: 컨텍스트 확인

실행 전 반드시 다음을 확인한다.

### 0-1. 실행 모드 판별
```
if _workspace/ 미존재:
    → 초기 실행 (Phase 1부터 진행)
elif _workspace/ 존재 AND 사용자가 topic 등 새 파라미터 제공:
    → 새 실행 (기존 _workspace/ → _workspace_prev/로 이동 후 Phase 1)
elif _workspace/ 존재 AND 사용자가 부분 수정 요청:
    → 부분 재실행 (영향받는 에이전트만 재호출, Phase 건너뜀)
else:
    → 사용자에게 의도 확인
```

### 0-2. 입력 파라미터 수집
필수: `topic`. 누락 시 사용자에게 질문.
선택(기본값):
- `audience = "intermediate developers"`
- `depth = "standard"` (intro | standard | deep)
- `target_duration_min = 120`
- `language = "ko"`
- `tone = "friendly"` (formal | friendly | socratic)

### 0-3. HITL 플래그
사용자가 "자동으로 끝까지"라고 하면 `hitl=false`, "중간에 확인하고 싶어"라면 `hitl=true`. 기본값은 `hitl=true`.

## Phase 1: Design (Team A — 순차 파이프라인)

**실행 모드:** 에이전트 팀 (A = `curriculum-architect` + `section-designer` + `class-planner`)

```
TeamCreate(team_name="course-design", members=[curriculum-architect, section-designer, class-planner])
```

### 1-1. Course Spec
- `curriculum-architect`에게 `TaskCreate("Plan course for topic: <topic>")`
- 출력: `_workspace/01_architect_course_spec.json`, `_workspace/01_architect_learning_objectives.json`

**[HITL 체크포인트 #1]** `hitl=true`면 사용자에게 Course Spec 요약 제시, 섹션 목록·LO 분포 확인. 수정 요청 시 architect 재호출.

### 1-2. Section Design (섹션별 fan-out)
- 각 섹션에 대해 `section-designer`에게 `TaskCreate("Design classes for section: <sid>")`
- 섹션들을 **병렬**로 처리 (의존성 없음)
- 출력: `_workspace/02_section_<sid>.json`

### 1-3. Class Planning (class별 fan-out)
- 각 class에 대해 `class-planner`에게 `TaskCreate("Plan class <cid>")`
- class 간 독립이면 전부 병렬, depends_on이 있으면 위상 정렬
- 출력: `_workspace/03_class_<cid>_beats.json`

Phase 1 완료 후 `TeamDelete("course-design")`.

## Phase 2: Content (Team B — 자산 3종 생성)

**실행 모드:** 에이전트 팀 (B = `slide-author` + `note-writer` + `script-writer`)

```
TeamCreate(team_name="content-authoring", members=[slide-author, note-writer, script-writer])
```

각 class에 대해:
1. `slide-author` ∥ `note-writer` **병렬 실행** (서로 독립)
2. 둘 다 완료되면 `script-writer` 실행 (slide 번호가 필요)

여러 class를 동시 진행할 수 있다 — 팀이 자체적으로 `SendMessage`로 "slide ready for S1.C1" 알림.

**[HITL 체크포인트 #2]** `hitl=true`이고 첫 class 완료 시점에 사용자에게 샘플 3종 자산(slide/note/script) 보여주고 톤/스타일 캘리브레이션. 수정 지침 있으면 나머지 class에 반영.

Phase 2 완료 후 `TeamDelete("content-authoring")`.

## Phase 3: Assessment (quiz-master 단독)

**실행 모드:** 서브 에이전트 (단일 실행, 팀 통신 불필요)

각 섹션에 대해 `Agent(subagent_type="quiz-master", model="opus", run_in_background=true)`.
섹션들은 독립이므로 전부 병렬. 출력: `course/sections/<sec>/quiz.json`.

## Phase 4: QA (coherence-reviewer)

**실행 모드:** 에이전트 팀 (기존 저자들 + reviewer가 수정 대화)

revise가 필요하면 reviewer가 원저자에게 `SendMessage`로 수정 지시 → 저자 재작업 → reviewer 재검토 (최대 2회 루프).

```
TeamCreate(team_name="qa-loop", members=[coherence-reviewer, slide-author, note-writer, script-writer, quiz-master])
```

- reviewer에게 `TaskCreate("Review full course")`
- 출력: `_workspace/99_coherence_report.json/.md`

**[HITL 체크포인트 #3]** `hitl=true`면 사용자에게 리포트 요약 제시. pass면 바로 진행, revise가 2회 초과하면 사용자에게 판단 위임.

Phase 4 완료 후 `TeamDelete("qa-loop")`.

## Phase 5: Build (asset-builder 단독) — one-shot 확장

**실행 모드:** 서브 에이전트

`Agent(subagent_type="asset-builder", model="opus")` 로 빌드 실행. 이 에이전트는 아래 모든 단계를 `build-bundle.sh` 하나로 수행한다:

1. Marp HTML render (기존) — 슬라이드 뷰용
2. Marp PNG render (Phase 7 추가, 1920×1080) — 플레이어 슬라이드용
3. TTS 합성 (Phase 7 추가, 조건부) — `OPENAI_API_KEY` 있고 `SKIP_TTS!=1`일 때 `tts-synthesis/scripts/run.sh` 호출. audio/full.mp3 이미 있으면 skip (`FORCE_TTS=1`로 재합성).
4. Manifest 합성 — `scripts/synth-manifest.py`가 spec + 실제 자산 스캔하여 갱신
5. Player HTML 생성 (Phase 7 추가) — `scripts/generate-player.py`로 `course/index.html` + per-class `player.html` + per-section `quiz.html`
6. SSML 검증 (기존)
7. `course/build/bundle.zip` 패키징

- 입력 조건: `coherence_report.overall == "pass"`
- 출력: `course/manifest.json`, `course/index.html` (learner entry), `course/build/bundle.zip`

### 선택적 환경변수
- `SKIP_TTS=1` — TTS 생략 (슬라이드/노트/트랜스크립트만 필요할 때)
- `FORCE_TTS=1` — 기존 audio 무시하고 재합성
- `SKIP_PLAYER=1` — 플레이어 HTML 생략 (raw 파일만)

## 데이터 전달

- **파일 기반** (주) — 모든 중간/최종 산출물
- **메시지 기반** (보조) — 팀원 간 상태 알림, reviewer의 수정 지시
- **태스크 기반** (조율) — 각 Phase의 작업 할당·진행 추적

### 파일명 컨벤션
```
_workspace/
  01_architect_course_spec.json
  01_architect_learning_objectives.json
  02_section_<sid>.json
  03_class_<cid>_beats.json
  99_coherence_report.{json,md}
  98_build_log.txt

course/
  manifest.json
  meta/audience.md
  meta/learning_objectives.json
  sections/<NN-slug>/section.json
  sections/<NN-slug>/classes/<NN-slug>/{class.json,slide.source.md,slide.html,note.md,transcript.txt,transcript.ssml?}
  sections/<NN-slug>/quiz.json
  build/bundle.zip
```

## 에러 핸들링

- **에이전트 실패 시**: 1회 재시도. 재실패 시 해당 산출물은 `_workspace/98_failures.md`에 기록하고 진행 (QA 단계에서 집계)
- **Marp 렌더 실패**: slide.source.md는 보존, coherence-reviewer가 판단
- **Coherence revise 2회 초과**: 사용자에게 판단 요청, 자동 진행 금지
- **topic 과도하게 광범위**: architect가 범위 좁힐 제안 반환 → 사용자 재입력 필요
- **상충 정보**: 삭제 금지, 양쪽 출처 병기

## 테스트 시나리오

### 정상 흐름
입력: `topic="React Server Components", audience="intermediate", duration=60`
기대 산출물: 3 section × 2 class = 6 class, 각 class에 slide/note/transcript 3종 + 3 quiz.json + bundle.zip
검증: `jq '.stats' course/manifest.json`로 sections=3, classes=6, lo_count≥9, bloom_levels≥4.

### 에러 흐름
입력: `topic="프로그래밍"` (과도하게 넓음)
기대: curriculum-architect가 제안 3개 반환 ("JS 기초", "함수형 입문", "테스트 자동화") + Phase 1에서 중단.

### 부분 재실행
`_workspace/` 존재 + 사용자 "S2의 퀴즈만 다시 만들어줘"
기대: quiz-master만 재호출, 다른 자산 유지, coherence-reviewer가 S2 재검토만.

## 크기 관리
세부 Bloom 레벨 기준, beat type 가이드, Marp 문법 치트는 각 에이전트의 전용 스킬(`curriculum-design`, `class-planning`, `slide-authoring` 등)을 참조. 이 오케스트레이터 SKILL.md는 **조율 로직**만 담는다.
