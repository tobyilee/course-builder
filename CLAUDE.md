# AI Course Builder

## 하네스: AI Online Course Builder

**목표:** 주제 입력만으로 ADDIE + Bloom's Taxonomy 기반의 온라인 강의(Section → Class, 각 Class에 HTML slide + MD note + TTS transcript, Section 단위 quiz 5~9문항)를 자동 생성한다.

**트리거:** 강의·코스·커리큘럼 생성/설계/제작 요청 시 `course-builder` 스킬을 사용하라. "강의 만들어줘", "온라인 코스 설계", "커리큘럼 짜줘", "슬라이드+노트+스크립트", "TTS 강의", "섹션별 퀴즈 포함 강의", "이 주제로 강의 만들어", "코스 재실행", "섹션만 다시" 등이 트리거. 단순 질문(이론 설명·정의 조사)은 직접 응답.

**작업 디렉토리:** `course/` (산출물), `_workspace/` (중간 산출물, 재실행 시 `_workspace_prev/`로 이동).

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-04-22 | 초기 구성 | 전체 (9 에이전트, 10 스킬) | 초기 하네스 구축 |
| 2026-04-22 | Speakability 규칙에 "대괄호 디렉티브 제외" 조항 추가 | `skills/coherence-review/SKILL.md` §8 | 스모크 테스트에서 `[pause:1000]` 마커가 "긴 숫자" 검사에 false-positive 걸리는 이슈 감지. TTS 후처리 디렉티브는 발화 대상이 아니므로 검사 제외가 맞음. |
| 2026-04-22 | build-bundle.sh의 marp 호출에 `</dev/null` 추가 | `skills/asset-build/scripts/build-bundle.sh:40` | while-read 루프와 marp가 stdin을 공유해 다중 파일 렌더 시 `1/N`만 렌더되는 버그. `</dev/null`로 stdin 격리하면 각 iteration이 독립 렌더. 실행 중 발견·수정됨. |
| 2026-04-22 | TTS 합성 스크립트 추가 (Non-Goal 확장) | `scripts/synthesize-tts.py` | edge-tts + ffmpeg으로 transcript → per-slide MP3 + full.mp3. `[slide N]` / `[pause:ms]` 파싱. 향후 `tts-synthesis` 스킬로 승격 후보. |
| 2026-04-22 | TTS 백엔드 pluggable화 (edge + openai) | `scripts/synthesize-tts.py` | 기본값을 `--engine openai --model gpt-4o-mini-tts --voice nova`로 전환. `instructions` 파라미터로 tone/speaker_affect 메타를 TTS에 직접 주입 가능 — script-writing 스킬 메타데이터 활용도 상승. edge-tts는 `--engine edge`로 유지. |
| 2026-04-22 | TTS 속도 기본값 1.3x (30% 빠름) 설정 + retry 로직 | `scripts/synthesize-tts.py` | 사용자 선호에 따라 `--speed 1.3` 기본화. 청취 템포가 자연스럽게 빨라짐. 함께 `with_retry` 데코레이터 추가 — edge/openai 모두 transient 실패를 4회 exponential backoff. |
| 2026-04-22 | Phase 7: voice별 char/sec rate 테이블 문서화 | `skills/script-writing/SKILL.md` §"길이 계산" | 단일 상수(2.7)를 voice/엔진별 표로 대체. Neural voice 실측 ≈4.3 반영. 스크립트 길이 공식이 speed 파라미터까지 고려하도록 확장. |
| 2026-04-22 | Phase 7: tts-synthesis 스킬 신규 생성 + pipefail 래퍼 | `skills/tts-synthesis/SKILL.md` + `scripts/run.sh` | 합성 파이프라인을 스킬로 승격. `scripts/synthesize-tts.py`는 canonical 유지, 스킬은 사용 규약·trigger·오케스트레이터 Phase 5.5 편입 설계 명시. 래퍼가 `.env` 로딩 + `PIPESTATUS[0]` 전파로 `tee` exit 마스킹 재발 차단. |
| 2026-04-22 | Phase 7: slide별 speaker_affect → OpenAI instructions 분기 주입 | `scripts/synthesize-tts.py` `--beats` | beat sheet의 `speaker_affect`를 slide별로 TTS에 주입. 17개 affect keyword → instruction overlay 매핑. slide-beat 비례 스트레치로 slide 수 != beat 수인 class도 커버. script-writing 메타데이터 활용도 상승. |
| 2026-04-22 | Phase 7: 통합 HTML 플레이어 생성기 추가 | `scripts/generate-player.py` | 각 class마다 `player.html` (slide PNG + per-slide MP3 + transcript + 썸네일), 섹션마다 `quiz.html` (자동 채점), 코스 루트에 `index.html` (TOC). 자산은 Marp PNG 렌더(1920×1080, scale 1.5) 추가. `course/` 열면 바로 학습자 경험. 다크 테마, 키보드 단축키(space/←/→), responsive. |
| 2026-04-22 | Pause 스케일링 정책 변경: speed와 같은 비율로 압축 | `scripts/synthesize-tts.py:192` | 이전 "pause 원본 유지" 선호를 실사용 청취 후 번복. `silence(ms/speed)`로 변환. 50ms 미만은 인지 불가 blip이라 스킵. 전체 duration 578→553s 근방, 진짜 1.3x 압축에 근접. memory/feedback_tts_config.md도 함께 갱신. |
| 2026-04-22 | Phase 7: 오케스트레이터 Phase 5 one-shot 편입 | `skills/asset-build/scripts/build-bundle.sh`, `scripts/synth-manifest.py`, `agents/asset-builder.md`, `skills/course-builder/SKILL.md` | asset-build가 이제 Marp(HTML+PNG) → TTS → manifest 합성 → player 생성 → SSML 검증 → zip을 한 커맨드로 수행. `OPENAI_API_KEY` 있으면 TTS 자동, `audio/full.mp3` 캐시로 중복 방지. `SKIP_TTS=1`/`FORCE_TTS=1`/`SKIP_PLAYER=1` 환경변수 제공. 진짜 one-shot 주제→bundle.zip 달성. |
| 2026-04-23 | Phase 7: audience 스키마 호환성 | `scripts/generate-player.py`, `scripts/synth-manifest.py` | Kotlin 코스 실행 중 architect가 audience를 structured dict(`{level, profile, assumed_knowledge}`)로 생성해 하류 스크립트가 `html.escape(dict)`에서 실패. 두 스크립트에 `audience_to_str` coercion 추가 — 문자열/dict 모두 수용. 일반 schema tolerance 패턴 — 다른 필드에도 확장 고려. |
| 2026-04-23 | Phase 7: 플레이어 end-panel 내비게이션 추가 | `scripts/generate-player.py` | class 마지막 슬라이드 도달 시 end-panel 노출(gradient+slideIn 애니메이션). 4 상태별 CTA 버튼 분기: 중간=다음수업/퀴즈, 섹션끝=퀴즈/다음섹션, 코스끝=마지막퀴즈/목차. 퀴즈 제출 후에도 NEXT_HREF로 다음 섹션 첫 class 이동 제공. 키보드 space/← /→는 기존대로 유지. |
| 2026-04-23 | Phase 7: TOC 사이드바 + 진행 progress bar | `scripts/generate-player.py` | 플레이어 레이아웃을 3-column(220 TOC · 1fr Stage · 320 Transcript)으로 확장. 상단 progress bar 2종(course-level `Class N/M` + slide-level `N/K`). TOC는 모든 섹션/class/퀴즈 나열, 현재 class `.current` 하이라이트, 좁은 화면에선 ☰ 햄버거 토글. class 간 직접 점프 가능 — 선형 재생뿐 아니라 비선형 탐색 지원. |
| 2026-04-22 | 실측 vs 추정 duration 갭 관찰 (Phase 7 후보) | `skills/script-writing/SKILL.md` §"길이 계산" | Neural voice 실측 ≈4.3 chars/sec인데 스킬 공식은 2.7. voice별 rate 테이블 필요. 아직 수정 전 — 실측 더 필요. |
| 2026-04-22 | 파이프라인 `tee` exit 마스킹 이슈 발견 (Phase 7 후보) | TTS 실행 패턴 | `python3 ... \| tee log` 구조에서 python 실패를 tee가 가려 background 알림이 거짓 exit 0 보고. 해결: `set -o pipefail` + `PIPESTATUS[0]` 체크. 향후 tts-synthesis 스킬로 승격 시 래퍼 스크립트에 내장 필요. |
