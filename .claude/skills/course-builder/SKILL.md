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
    → full re-run (기존 _workspace/ → _workspace_prev/로 이동 후 Phase 1)
elif _workspace/ 존재 AND 사용자가 scope 지정 부분 수정:
    → partial re-run (scope에 속한 자산만 재생성, 나머지는 보존)
else:
    → 사용자에게 의도 확인
```

### 0-1a. Scope 문법 (partial re-run)
부분 재실행은 **명시적 scope**를 받는다. 사용자가 "S1.C2만", "S2 section만 다시", "C3 tone만 formal로" 라고 하면 다음 토큰으로 환원:

| Scope | 의미 | 영향 |
|---|---|---|
| `S<n>` | 섹션 전체 | 해당 섹션의 모든 class + section quiz |
| `S<n>.C<m>` | 단일 class | 해당 class의 slide/note/transcript(+audio) |
| `S<n>.C<m>.tone=X` | 속성 override | tone만 교체 후 3종 자산 재생성 |
| `S<n>.quiz` | quiz만 | 섹션 quiz.json만 교체 |

여러 scope은 공백·쉼표로 연결: `--scope "S1.C2,S2.C1"`.

### 0-1b. Partial re-run 원칙
1. **LO id 보존 절대원칙** — architect가 `_workspace_prev/` 또는 `_workspace/`의 기존 `01_architect_learning_objectives.json` 을 input으로 받아 LO id/text를 **reuse**. scope에 속한 섹션의 LO만 변경, 나머지는 byte-for-byte 동일.
2. **자산 cache-hit** — scope 밖 class의 `course/sections/.../{slide.source.md, note.md, transcript.txt, audio/}` 는 그대로 유지. build-bundle.sh는 이미 `audio/full.mp3` 존재 시 TTS skip (`FORCE_TTS=1` 로만 override).
3. **Quiz cross-ref 안정성** — quiz-master는 `course/sections/<sec>/quiz.json` 기존 파일을 input으로 받아 scope에 속한 class의 item만 교체. 나머지 item은 **id 보존**.
4. **Coherence regression mode** — reviewer는 scope + 그 dependency(해당 섹션 quiz, cross-ref된 note 등)만 재검증. 모든 자산 재검사 금지.

부분 재실행은 `_workspace/` 를 `_workspace_prev/` 로 이동하지 **않는다**. 원본을 in-place로 부분 업데이트.

### 0-2. 입력 파라미터 수집
필수: `topic`. 누락 시 사용자에게 질문.
선택(기본값):
- `audience = "intermediate developers"`
- `depth = "standard"` (intro | standard | deep)
- `target_duration_min = 120`
- `language = "ko"` (ko | en)
- `tone = "friendly"` (formal | friendly | socratic)

### 0-2a. 언어 판별 (language resolution)
1. 사용자가 명시: "영어로", "in English", "English course", "영문으로" → `language = "en"`.
2. 사용자가 "한국어로", "한글로", "국문으로" → `language = "ko"`.
3. 명시 없음 → `"ko"` 기본. **사용자 발화 언어만으로 자동 추론하지 않는다**(영어로 질문했다고 영어 강의라고 가정 금지).

`language`는 Course Spec `01_architect_course_spec.json`에 저장되어 하류 에이전트 전체가 참조한다. 한 번 확정 후 재실행 전까지 변경 금지 — 중간에 바꾸면 artifact 불일치 발생.

### 0-3. HITL 플래그
사용자가 "자동으로 끝까지"라고 하면 `hitl=false`, "중간에 확인하고 싶어"라면 `hitl=true`. 기본값은 `hitl=true`.

### 0-4. HITL 체크포인트 메커니즘 (표준)

`hitl=true` 일 때 Phase 1(#1), Phase 2(#2), Phase 4(#3) 마지막 산출물 시점에 사용자 동의를 받는다. 메커니즘은 다음 4단계로 표준화한다:

1. **요약 제시** — 핵심 산출물의 **사람이 읽을 수 있는** 요약을 사용자에게 출력. 형식:
   - 체크포인트 #1 (Course Spec): 섹션 목록(id, title, duration), LO 총수, Bloom 분포
   - 체크포인트 #2 (첫 class 3종 자산): slide.source.md 발췌 + note.md 첫 200자 + transcript.txt 첫 200자
   - 체크포인트 #3 (Coherence Report): `99_coherence_report.md` 의 `## VERDICT:` 섹션 + 상위 5개 이슈
2. **결정 질문** — 다음 3지선다로만 묻는다 (자유 응답이면 의도 추정 안전):
   - `yes` (또는 "진행", "go") → 다음 Phase 진행
   - `edit: <자유 텍스트 수정 지침>` → 해당 Phase 의 1차 책임 에이전트(architect / 첫 class 의 3저자 / coherence-reviewer) 에 수정 지시 메시지 전달 후 같은 체크포인트 재집행
   - `regen` → 같은 입력으로 해당 Phase 전체 재실행 (random seed 가 다르면 결과 변동 기대)
3. **응답 기록** — 사용자 응답을 `_workspace/97_hitl_log.md` 에 append 한다. 형식:
   ```
   ## checkpoint #N · <iso8601>
   verdict: yes | edit | regen
   instructions: <사용자 자유 텍스트 또는 빈 줄>
   acted_on: <변경된 파일 목록 또는 "none">
   ```
4. **타임아웃 정책** — 사용자 미응답 시 자동 진행 금지. 명시 응답 받을 때까지 대기. (사용자가 처음에 `hitl=false` 로 시작했으면 이 단계 자체를 건너뜀.)

`hitl=false` 일 때는 위 4단계 모두 건너뛰고 자동 진행하되, 각 Phase 종료 시점에 1줄 진행 보고만 출력한다 (사용자가 진행 상황 추적용).

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

## Phase 5: Build (asset-builder 가 조율, tts-synthesizer 위임)

**실행 모드:** 하이브리드
- 메인: `Agent(subagent_type="asset-builder", model="opus")` 가 `build-bundle.sh` 를 호출해 빌드 파이프라인을 조율
- 위임: TTS 단계는 `asset-builder` 가 빌드 스크립트 안에서 `tts-synthesizer` 가 책임지는 `tts-synthesis/scripts/run.sh` 를 호출 — TTS 실패는 `tts-synthesizer` 가 보고하고 `asset-builder` 가 manifest.asset_errors 로 집계

### 5-1. 빌드 단계 (build-bundle.sh 의 7 step과 동기화)

| Step | 책임자 | 작업 | 실패 모드 |
|---|---|---|---|
| 1 | asset-builder | gate: `coherence_report.overall == "pass"` 확인 (실패 시 `BUILD_REFUSED`) | hard fail |
| 2 | asset-builder | Marp HTML 재렌더 (모든 `slide.source.md` → `slide.html`) | per-class soft fail (`asset_errors`) |
| 3 | asset-builder | Marp PNG 렌더 (player 용) — `SKIP_PLAYER=1` 또는 player 미사용 시 skip 가능 | per-class soft fail |
| 4 | **tts-synthesizer** (위임) | per-class TTS 합성 — `OPENAI_API_KEY` 있고 `SKIP_TTS!=1`일 때만. audio/full.mp3 캐시 hit 시 skip | per-class soft fail (보고 `TTS_FAILED <cls>`) |
| 5 | asset-builder | Manifest 합성 (`scripts/synth-manifest.py`) | hard fail |
| 6 | asset-builder | Player HTML 생성 (`scripts/generate-player.py`) — `SKIP_PLAYER=1`이면 skip | warn only |
| 7 | asset-builder | SSML 검증 (있을 때) | warn only |
| 8 | asset-builder | `course/build/bundle.zip` 패키징 | hard fail |

- 입력 조건: `coherence_report.overall == "pass"`
- 출력: `course/manifest.json`, `course/index.html` (learner entry), `course/build/bundle.zip`

### 5-2. 선택적 환경변수
| 변수 | 효과 | 의존 도구 우회 |
|---|---|---|
| `SKIP_TTS=1` | TTS step 4 생략 (슬라이드/노트/트랜스크립트만) | `OPENAI_API_KEY` 불요 |
| `FORCE_TTS=1` | 기존 audio 무시하고 재합성 | — |
| `SKIP_PLAYER=1` | step 3(PNG) + step 6(player HTML) 동시 생략 — slides-only 사용 사례 | ffmpeg 의존 일부 우회 |

### 5-3. TTS 위임 호출 규약
`asset-builder` 는 빌드 중 각 class 의 transcript.txt 를 발견할 때마다 `tts-synthesizer` 의 표준 호출을 트리거한다. 표준 인자:
- transcript path, audio out_dir
- `--language <ko|en>` (course_spec 에서 추출)
- `--beats <path>` (있을 때) — speaker affect overlay
- `--slide-source <path>` (beats 가 있을 때 동반) — 정확 매핑

전체 위임 흐름·재시도·분류 책임은 `tts-synthesizer.md` 와 `tts-synthesis/SKILL.md` 가 단일 진실원.

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
