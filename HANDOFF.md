# Session Handoff — AI Course Builder

**Last updated:** 2026-04-23 (sessions `1b0b191c`, `12150c38`, `0e57f7c6`)
**Author:** Claude Opus 4.7 (1M context) w/ toby

> **2026-04-23 update (session `0e57f7c6`):** P2 pipeline-precision items + (a big chunk of) P4 partial re-run all landed. Five atomic commits on top of `da5b9de` (on feature branch `session-3-pipeline-precision`): T1 coherence verdict sync · T2 slide `<!-- beat: bN -->` direct mapping · T3 per-class duration feedback loop · T4 char-proportional line-level transcript highlight · T6 partial re-run scope grammar + LO/quiz id preservation. **T5 (CI canary workflow) was built and then dropped by user decision — deferred to roadmap.** T5 draft preserved in reflog as commit `bba03db` (can be cherry-picked back when ready). **Local branch HEAD: `07b90ac`** — awaiting push (branch-based PR flow; `main` rewound to `origin/main`).
>
> **2026-04-23 earlier (session `12150c38`):** P1 키 로테이션 + P2 localStorage resume + P3 레포 정비 + 언어 지원 (ko/en) 전체 + Player UI i18n + playback-speed button 전부 완료. 영어 Git-rebase 강의 end-to-end smoke test 통과. **Public repo HEAD through that session: `2494607`.**

Pick up from here in a fresh session. This file is the **single source of truth for in-flight context**. `README.md` describes what the project is; this file describes **what's left to do and why**.

---

## TL;DR

- The harness is **production-ready for single-topic courses**. Two courses built end-to-end (NotebookLM 10min, Kotlin/Spring 17min).
- Repo is **public** at https://github.com/tobyilee/course-builder, 3 commits.
- Current working directory has the **Kotlin course artifacts built** in `course/`, audio generated with OpenAI `gpt-4o-mini-tts`/nova/speed 1.3/pause-scaled/affect-injected. Open `course/index.html` to see it live.
- **⚠️ OpenAI API key in `.env` is EXPOSED in the conversation transcript** (`~/.claude/projects/-Users-tobylee-workspace-ai-course-builder/1b0b191c-*.jsonl`). Should be rotated before further use.
- Memory: `~/.claude/projects/-Users-tobylee-workspace-ai-course-builder/memory/` has TTS-config + project feedback entries; auto-loaded in future sessions of this directory.

---

## 1. Repo state

```
main (ahead of local nothing)
├── d513144  Add comprehensive README
├── a023990  Trim CLAUDE.md — keep pointer + trigger, drop inline change log
└── cdd1fda  Initial commit: AI online course builder harness
```

- **Remote:** `origin/main` at `https://github.com/tobyilee/course-builder`
- **Visibility:** public (was private, user toggled)
- **Working tree:** clean
- **Untracked (gitignored):** `.env`, `_workspace/`, `_workspace_prev/`, `course/`, `course_prev/`, `.omc/`

## 2. File system snapshot

```
course-builder/
├── .claude/agents/         (9 agent defs, model: opus)
├── .claude/skills/         (10 skills incl. orchestrator + tts-synthesis)
├── scripts/
│   ├── synthesize-tts.py   (OpenAI + edge-tts pluggable, speed 1.3 + pause scaling + affect overlay)
│   ├── synth-manifest.py   (idempotent)
│   └── generate-player.py  (TOC sidebar + progress bar + end-panel CTA)
├── CLAUDE.md               (MINIMAL — pointer + trigger rules only; no change log inline)
├── README.md               (677 lines, English, public-facing)
├── HANDOFF.md              (THIS FILE)
├── .gitignore
├── .env                    (OPENAI_API_KEY — gitignored, but EXPOSED in chat transcript)
├── _workspace/             (Kotlin course specs)
├── _workspace_prev/        (NotebookLM course specs, archived)
├── course/                 (Kotlin course artifacts, 13MB bundle)
└── course_prev/            (NotebookLM course artifacts, archived)
```

## 3. What was built this session (chronological)

### Initial build (20 major steps)
1. Phase 0 audit → Phase 1-5 of orchestrator executed for **NotebookLM 활용법** (1 sec × 2 class, 20 min target)
2. Smoke-tested end-to-end: generated slides, notes, transcripts, section quiz, coherence review (caught 3 issues incl. cross-ref mismatch + speakability rule false-positive)
3. Built bundle.zip; added `edge-tts` synthesis (Non-Goal extension)
4. Switched TTS default to OpenAI `gpt-4o-mini-tts` + `nova` voice
5. Added **`instructions` tone injection** (friendly dev tutorial baseline)
6. Added **speed 1.3** (30% faster) with user validation — first affirmed pause preservation, later reversed to "scale pauses by speed" after listening
7. Added **retry logic** (`with_retry` decorator) for transient edge-tts rate limits
8. A/B compared edge-tts vs OpenAI on same content; user picked OpenAI
9. **Phase 7 evolution** kicked off — documented voice rate table (2.7 → 4.3 chars/sec for Neural), promoted synthesis into `tts-synthesis` skill
10. Added **per-slide `speaker_affect` overlay** (hook=호기심, teach=차분, example=흥분, practice=질문, recap=확신) — 17 keyword map
11. Built **HTML player** (per-class `player.html`, per-section `quiz.html`, course `index.html`) — self-contained single-file pages with slide PNG + per-slide MP3 + transcript + thumbnails
12. Added **end-of-class navigation CTAs** (4 states: mid-section / section-end / last-in-course / last-class-of-course)
13. Added **progress bar** (course-level `Class N/M` + slide-level `N/K`)
14. Added **TOC sidebar** (3-column layout 1280px+; ☰ overlay at narrow widths; current class highlighted)
15. Executed **2nd course generation** (Kotlin/Spring, 2 sec × 2 class, 30 min target)
16. Coherence review PASSED on first try (no revision loop — validated Phase 7 improvements)
17. Build-bundle.sh died mid-pipeline (shell lifecycle issue); recovered by running 3 remaining TTS in parallel background, then `build-bundle.sh` used audio cache
18. Fixed **audience schema tolerance** bug (architect emitted dict, not string)
19. Git init + initial commit; GitHub repo created; README.md authored and pushed
20. Repo made public

## 4. Memory written

At `~/.claude/projects/-Users-tobylee-workspace-ai-course-builder/memory/`:

| File | Type | Purpose |
|---|---|---|
| `MEMORY.md` | index | Pointers to all memory entries (auto-loaded into every session of this dir) |
| `feedback_tts_config.md` | feedback | TTS defaults + pause-scaling policy (user-confirmed preference) |
| `project_course_builder_harness.md` | project | Harness overview + Phase 7 candidate list |

These will be **automatically loaded** in future Claude sessions launched from this project directory. No manual action needed.

## 5. Environment state

### Tools verified working
- `marp` (Marp CLI) — used by build-bundle.sh for HTML + PNG render
- `ffmpeg` — silence + concat for TTS pipeline
- `edge-tts` 7.2.8 — fallback TTS
- Python 3.10.18 (pyenv)
- `openai` 2.32.0 Python SDK
- GitHub CLI at `/opt/homebrew/bin/gh` (authenticated as `tobyilee`)
- `jq`, `xmllint`, `zip`

### ⚠️ Security status (updated 2026-04-23)
- Old key `sk-proj-NC2aMjOB...KG8b20A` **revoked by user** in OpenAI dashboard
- New key issued, stored in `.env` (gitignored, not tracked) — live-verified via `models.list`
- New key is present in session `12150c38` jsonl (Read-before-Edit flow); accepted as local-only risk
- `.env` format gotcha: uses `export OPENAI_API_KEY=<key>` (shell-source friendly) — a paste artifact (`=- sk-proj-`) was fixed this session

### Shell gotchas observed
- Bash tool's `cd` doesn't persist across tool calls — use absolute paths
- `python3 ... | tee log` returns tee's exit code, not python's — use `set -o pipefail` + `PIPESTATUS[0]` (already addressed in `tts-synthesis/scripts/run.sh`)
- Long-running background jobs in Claude Code shell can be killed by session lifecycle events — prefer parallel short-lived jobs over single long serial job (already addressed by smart TTS caching)
- `find` order on macOS is not alphabetical — `synthesize-tts.py` does slide-order mapping internally, but don't assume find-order == section order

## 6. Next steps — prioritized

### Priority 1 (do before anything else) — ✅ DONE 2026-04-23

- [x] **Rotate OpenAI API key** — old key revoked in dashboard
- [x] Update `.env` with new key (paste artifact `- ` cleaned)
- [x] Verify: `source .env` + OpenAI `models.list` live call succeeded (128 models, `gpt-4o-mini-tts` accessible)

### Priority 2 (if continuing Phase 7 evolution)

- [x] **localStorage resume** — DONE session 2 (commit `196eba9`). Per-class state (page pathname as key), 30d expiry, 3s throttle.
- [x] **Multilingual** (ko/en) — DONE session 2 (commits `50f43c6`, `06bfca9`, `2494607`). Full pipeline: agents, TTS engine, player chrome, quiz.html, index.html landing. End-to-end smoke test passed on a Git-rebase 10min English course.
- [x] **Playback-speed button** — DONE session 2 (commit `2494607`). Cycle button 0.75× → 2×, localStorage-persisted, preservesPitch.
- [x] **slide-author emits `beat_id` in Marp frontmatter** — DONE session 3 (commit `629a4f3`, T2). Per-slide `<!-- beat: bN -->` HTML comment; `synthesize-tts.py` parses via `_parse_beat_ids_from_slides` and falls back to proportional heuristic when absent. 100% affect-injection accuracy on new decks; existing decks unchanged.
- [~] **Subtitle sync** — session 3 shipped char-proportional **line-level** MVP (commit `eccab20`, T4). `generate-player.py` embeds per-line `{start,end}` derived from slide MP3 duration split by character-weight; timeupdate listener toggles `.active` + scrollIntoView. Word-accurate timing via Whisper-align **still deferred** — SKILL.md reserves a `audio/slide_NN.timing.json` sidecar format for that future upgrade.
- [x] **Duration feedback loop** — DONE session 3 (commit `c9831df`, T3). `synth-manifest.py` now records per-class `actual_audio_duration_sec`; `script-writer` reads previous run's `course_prev_*/manifest.json`; `script-writing/SKILL.md` has the calibration formula (clamped to `[0.7, 1.4]`).
- [x] **🐛 Coherence-reviewer JSON emission** — DONE session 3 (commit `3087860`, T1). Root cause was actually **JSON↔MD verdict divergence** (JSON=pass, MD=REVISE left behind after revise loop), not missing JSON. Fix: reviewer agent + SKILL now require atomic dual-write and same-verdict emit; `build-bundle.sh` logs WARN on mismatch. Existing divergent `_workspace/99_coherence_report.md` left as-is on purpose (proves T1's WARN fires).

### Priority 3 (polish)

- [x] **`.env.example`** — DONE session 2 (commit `bfe1e6e`).
- [x] **LICENSE** — DONE session 2 (commit `bfe1e6e`).
- [x] **Screenshot for README** — DONE session 2 (commit `bfe1e6e`). Dark-theme Chrome headless.
- [ ] **CI recipe** — GitHub Action that runs the non-generative asset pipeline (marp + ffmpeg + coherence gate + manifest + player) against a pre-built canary fixture with `SKIP_TTS=1`. Does NOT need Anthropic API key — Claude agents are not invoked in CI. **Draft built in session 3 then deferred** (user chose to defer; `gh` OAuth token also lacked `workflow` scope to push). Draft preserved: reflog commit **`bba03db`** contains `.github/workflows/build-canary.yml` + `.github/fixtures/canary/` (108 KB source-only fixture) + `.gitignore` anchoring fix + README badge. Resurrect with `git cherry-pick bba03db` when ready; ensure `gh auth refresh -s workflow` first.

### Priority 4 (larger scope)

- [ ] **Longer course scale test** — 60min, 4-5 sections. Surfaces unseen issues (section-level dependency graph, cross-section LO drift, larger Bloom spread).
- [~] **Partial re-run testing** — session 3 shipped the **contract** (commit `07b90ac`, T6); session 4 **end-to-end exercised** it on the Git-rebase fixture (see Appendix A''). Two scopes ran green: `S1.quiz` (quiz-master polish pass, 7/7 item ids preserved, Bloom delta=0) and `S1` with LO addition (architect appended LO-1.5, lines 1-24 of LOs file **byte-identical** via Edit-not-Write). **3 real edge cases surfaced + 1 methodological win** — all landed as contract patches. Still untested: multi-section partial re-run, `S1.C2.tone=formal` (blocked by per-class-tone storage gap), revise-loop in regression mode.
- [ ] **Non-code domain** — try a marketing/leadership topic to verify the harness works without code-heavy content (tests whether slide-author still produces meaningful visuals without code blocks).

### Priority 5 (vision)

- [ ] **SCORM/xAPI export** — LMS integration. Today explicit Non-Goal; could be added as a post-build step reading `manifest.json`.
- [ ] **Image generation** — optional hero PNG per class via DALL-E / SDXL.
- [ ] **Quiz grading via LLM** — `short_answer` items currently rely on rubric self-grading; could auto-grade with a rubric-prompted API call.

## 7. Decisions made (don't relitigate without reason)

| Decision | Why | Source |
|---|---|---|
| TTS default = OpenAI `gpt-4o-mini-tts` / `nova` / speed 1.3 / pause scaled | User A/B tested and explicitly confirmed | `memory/feedback_tts_config.md` |
| `speaker_affect` overlay injected per slide | Meaningful TTS tone variation is worth the small code complexity | Phase 7 evolution |
| Harness change log lives in git, not in `CLAUDE.md` | CLAUDE.md is auto-loaded every session; should stay small | User trimmed CLAUDE.md explicitly |
| Pause scaling default ON | "Natural pauses with fast speech" felt sluggish in real use | User reversed initial preference |
| Generated artifacts (`course/`) not committed | Derivable from source + build; keeps repo lean | `.gitignore` design |
| Player renders PNG + per-slide MP3 rather than full.mp3 streaming | Simpler JS, trivial slide↔audio sync, no timeline math | Initial player design |
| 9 agents stays as-is; no new agents for TTS or Player | Scripts are fine; adding agents adds bureaucracy | Phase 7 restraint |
| localStorage key scheme: resume state per page, speed preference global | Resume is page-local state; speed is learner preference that should persist across classes | Session 2 commits `196eba9`, `2494607` |
| `language = "ko"` default, never auto-infer from user's speaking language | Users often speak Korean but request English content (and vice versa). Explicit-only policy avoids wrong defaults | CLAUDE.md + orchestrator SKILL.md §0-2a (session 2) |
| OpenAI `nova` kept for both ko and en (multilingual); edge-tts voice branches by language | `nova` produces natural English and Korean; simpler than per-language voice selection for the default engine | `synthesize-tts.py` session 2 |
| id/slug tokens (LO-1.1, S1.C1, 01-intro) are language-invariant | Language change must not cascade into path/link breakage | All 7 agent directives (session 2) |
| Player UI i18n scope escalated from "minimal" to "full" in a single session | User chose B (minimal) first for content pipeline, then pulled trigger on A (full) after seeing a half-Korean English course | Sessions 2 flow |

## 8. Known ugly corners

- `scripts/generate-player.py` grew from ~720 to ~860 lines in session 2 (i18n + resume + speed). Still heavy string formatting. Refactor candidate: split into template files + a small orchestrator. Low priority.
- `scripts/synthesize-tts.py` line 153 `from openai import OpenAI` is lazy-imported; Pyright warns it can't resolve. Real import works; warning is noise.
- `_workspace/99_coherence_report.md` isn't hand-tuned for readability; it's a machine-friendly dump. If you want a nicer report surface, that's a standalone polish.
- `synth-manifest.py` writes `meta/audience.md` only if missing — never updates on re-run. If audience changes in spec, old meta/ lingers. Minor.
- **Coherence JSON/MD mismatch** — session 3 (T1) locked down the atomic dual-write + verdict-sync contract on the reviewer side and added a non-fatal WARN on the build gate. Existing divergent `_workspace/99_coherence_report.md` left as-is on purpose (proves T1's WARN fires). Next revise-loop run should overwrite both files with matching verdicts.
- `generate-player.py:678` Pyright warning about unused `current_cls_slug` parameter in `make_toc_html` — pre-existing, leave as-is (dead param kept for signature stability).

## Appendix A': Session 3 commit log (2026-04-23, session `0e57f7c6`)

Five atomic commits on feature branch `session-3-pipeline-precision` (forked from `da5b9de`):

```
07b90ac  T6: Partial re-run mode — scope syntax + LO/quiz id preservation
eccab20  T4: Char-proportional line-level transcript highlight in player
c9831df  T3: Per-class actual_audio_duration_sec + prior-run calibration
629a4f3  T2: Direct slide↔beat mapping via <!-- beat: bN --> Marp comment
3087860  T1: Atomic dual-write + verdict sync for coherence reports
```

Per-commit shape:
- `3087860` (3 files): reviewer agent + coherence-review SKILL enforce atomic JSON/MD emit; `build-bundle.sh` logs WARN on verdict mismatch. **Design reversal vs prior HANDOFF:** the documented "JSON not written" bug was actually a post-revise MD-overwrite miss — JSON was fine, MD was stale.
- `629a4f3` (4 files): `synthesize-tts.py` gains `--slide-source` + `_parse_beat_ids_from_slides`; slide-author agent/skill prescribe `<!-- beat: bN -->`; build-bundle forwards the slide source. Backward compatible — existing decks use proportional fallback.
- `c9831df` (3 files): `synth-manifest.py` writes per-class `actual_audio_duration_sec`; script-writer SKILL adds prior-run calibration with `[0.7, 1.4]` clamp.
- `eccab20` (1 file): `generate-player.py` — `char_proportional_line_times()` helper, `transcriptTimes` parallel array, CSS `.active`, extended timeupdate listener with scrollIntoView.
- `07b90ac` (4 files): course-builder SKILL scope grammar + invariants; curriculum-architect split re-run guidance; quiz-master partial-run preservation; coherence-reviewer regression mode.

**T5 (CI canary) dropped mid-session.** Preserved in reflog as `bba03db`. Contents: `.github/workflows/build-canary.yml` + 108 KB `.github/fixtures/canary/` + `.gitignore` anchoring + README badge. See Priority 3 note for resurrection recipe.

Staging note: two files (`build-bundle.sh`, `coherence-reviewer.md`) straddled T1/T2 and T1/T6 respectively, so `git add -p` with piped answers split hunks per commit. Staged diff verified before each commit.

**Branch status:** `session-3-pipeline-precision` local-only (not yet pushed). `main` was rewound to `origin/main` after the branch was created. Push + PR is the next step.

---

## Appendix A: Session 2 commit log (2026-04-23)

Five commits added on top of `6f8869b` (session 1 close):

```
2494607  Add playback-speed cycle button to player
06bfca9  Extend player i18n to quiz.html and course landing
50f43c6  Add language=en support across the course-generation pipeline
196eba9  Add localStorage resume ("이어 듣기") banner to player
bfe1e6e  Add LICENSE, .env.example, player screenshots, and rotation follow-up
```

Per-commit shape:
- `bfe1e6e` (7 files): LICENSE (MIT, Toby Lee 2026), `.env.example`, three Chrome-headless screenshots, README Demo embed, HANDOFF P1 marked done.
- `196eba9` (1 file): `scripts/generate-player.py` +76 lines — resume banner HTML/CSS/JS, `location.pathname` storage key, 30d expiry, 3s timeupdate throttle, `loadedmetadata` seek.
- `50f43c6` (13 files): 7 agents, CLAUDE.md, orchestrator SKILL.md, `build-bundle.sh`, `synthesize-tts.py`, `generate-player.py`, + en-UI screenshot. **Sole commit for language feature pipeline**.
- `06bfca9` (4 files): `generate-player.py` QUIZ_TMPL + `build_index` i18n, `.gitignore` broadened to `course_prev*/`, en-course final landing + quiz screenshots.
- `2494607` (3 files): `generate-player.py` speed button (34 lines), two speed-state screenshots.

## Appendix B: English smoke-test artifact

Topic: "Git rebase basics — interactive rebase, squash, fixup, and when to prefer rebase over merge"
Audience: intermediate Git users. Duration: 10 min. Language: en. Tone: friendly.

Generated (lives in gitignored `course/`):
- 1 section, 2 classes (`01-rebase-foundations-and-interactive-cleanup`, `02-when-to-rebase-safety-and-rebase-vs-merge`)
- 4 LOs covering Understand / Apply / Analyze / Evaluate
- 12 Marp slides (6 per class), rendered HTML + PNG
- 2 notes (620 + 712 English words)
- 2 transcripts (770 + 841 words, 282 + 298 sec estimated)
- 7-item section quiz (Bloom: Understand 2, Apply 1, Analyze 2, Evaluate 2)
- 1 round of coherence revision (C2 note `[S1.C3]` phantom ref fixed via note-writer)
- S1.C1 audio synthesized via OpenAI `gpt-4o-mini-tts` / nova; C2 audio skipped (TTS killed by user; cost ~6 min per class too slow)

Artifacts preserved in `course_prev_ko_kotlin/` (previous Korean Kotlin course).

## 9. How to resume in a fresh session

### Opening commands for the next Claude

```bash
# 1. Confirm you're in the right dir
pwd  # should be /Users/tobylee/workspace/ai/course-builder

# 2. See git state
git log --oneline
git status

# 3. Verify the harness artifacts
ls .claude/agents/ .claude/skills/ scripts/

# 4. Check current Kotlin course
jq '.stats' course/manifest.json 2>/dev/null || echo "no course built"

# 5. Read this file + README
cat HANDOFF.md
cat README.md | head -50
```

### Memory state should be auto-loaded

Confirm by checking that `feedback_tts_config` and `project_course_builder_harness` memories appear in the session context (system-reminder block at session start).

### If user wants to generate a new course

Either:

a) **Via Claude Code agent orchestration** — just state the topic and params:
> "새로운 주제로 30분 강의 만들어줘: React Server Components"

The orchestrator (`.claude/skills/course-builder`) should trigger based on CLAUDE.md rules.

b) **Via direct scripts** — if specs already in `_workspace/`:
```bash
bash .claude/skills/asset-build/scripts/build-bundle.sh course
```

### If user wants to continue a Phase 7 item

Pick from [Priority 2 list](#priority-2-if-continuing-phase-7-evolution). Each has clear "touch" paths.

## 10. Conversation context summary

User profile (from this session):
- Korean-speaking, technical, comfortable with Claude Code agent workflows
- Values **real working outputs** over abstract architecture — wanted to hear the TTS, open the player, see the quiz
- Decisive: pick option 1, change speed, public the repo — doesn't dither
- Security-aware (noted when I pointed out key exposure)
- Likes explanatory insights (`★ Insight ─────` pattern was well-received)
- Iterative: "다음 작업을 알려줘" pattern — shipped in small increments, fed feedback quickly

Communication style that worked:
- Brief progress updates with clear state tables
- Polish prompts → rewrite to clean English (per global CLAUDE.md rule) — often Korean was already fine, minor suggestions
- When user said "1" pick the top-recommended option, proceed
- HITL checkpoints respected at Course Spec + after first class sample + at coherence report
- 🥕 emoji before tool invocations per global rule

---

## Appendix: project memory quick reference

### feedback_tts_config.md
TTS defaults: OpenAI gpt-4o-mini-tts / nova / speed 1.3 / pause scaled by speed / optional `--beats` affect overlay. User confirmed preferences after A/B. Changing defaults silently = bad.

### project_course_builder_harness.md
Harness location, trigger rules, 9 agents + 10 skills, 3 scripts, Phase 7 candidate list. Points back to CLAUDE.md for authoritative trigger keywords.

---

## Appendix A'': Session 4 — T6 partial re-run exercised end-to-end (2026-04-23)

Session `5359fb36`. User chose Option B ("exercise T6 partial re-run on the Git-rebase fixture to flush out architect 'read prev LO registry' edge cases"). No commits — the fixture is gitignored and was reverted to baseline after tests. Baseline snapshot kept at `/tmp/course-builder-t6-baseline-20260423-145807/` with a 17-file SHA256 manifest at `HASHES.txt`.

### Tests run

| # | Scope | Agents invoked | Verdict | Invariants held? |
|---|---|---|---|---|
| A | `S1.quiz` | quiz-master → coherence-reviewer (regression mode) | PASS | 11/11 byte-identical files; 7/7 quiz item ids preserved; Bloom delta=0; LO coverage 100%; JSON↔MD verdict parity OK; `scope: ["S1.quiz"]` + `mode: "regression"` emitted; C1/C2 marked `assumed_pass_out_of_scope` |
| B | `S1` (add LO-1.5) | curriculum-architect | PASS | LOs file lines 1-24 **byte-identical** (Edit-based, not Write); LO-1.5 cleanly appended at `max+1`; course_spec.json untouched; 3/3 beats files untouched; 6/6 slide/note/transcript files untouched; revision log written with full provenance |

After both tests the fixture was reverted to baseline; `shasum -c HASHES.txt` reported 17/17 OK. Evidence files `_workspace/01_architect_revision.md` and `_workspace/partial_rerun_notes.md` were left in place as a forensic trail (gitignored; no repo impact).

### Edge cases surfaced

**EC-1 (not a contract bug, my test-prompt error).** My initial Test B brief told the architect to "append LO-1.5 to Section S1's `lo_ids` list" — but no such field exists in the course-spec schema; the schema uses reverse-mapping (`LO.section_id`) only, which is clean and consistent. The architect correctly pushed back rather than inventing a field. **No contract change needed.** Lesson: T6-mode prompts must be grounded in the actual schema, not an assumed schema.

**EC-2 (real). Partial re-run does not auto-adjust `duration_min`.** Adding LO-1.5 to S1 left `total_duration_min: 10` unchanged despite now having 5 LOs (was 4). Downstream propagation would overpack classes. **Fix landed:** curriculum-architect.md partial re-run section now requires the architect to explicitly flag LO-count-vs-duration pressure in the revision log and suggest a mechanical duration bump (or confirm the existing budget absorbs it).

**EC-3 (real). MD verdict case-drift.** `coherence-reviewer.md` and `coherence-review/SKILL.md` prescribed uppercase `## VERDICT: PASS`/`REVISE`; the agent emitted lowercase `pass`. `build-bundle.sh` line 48 already normalizes to lowercase before comparing, so the WARN doesn't fire — but the docs and the impl disagreed. **Fix landed:** both contract files now declare the match as **case-insensitive** (uppercase preferred for readability) — docs and impl now agree.

**EC-4 (real). Self-report inaccuracy in quiz-master.** Agent claimed "stems/choices/correct are unchanged on every item" when `Q5.stem`, `Q5.choices`, `Q6.choices` had actually been edited. The agent was asserting from memory, not from diffing its output. **Fix landed:** curriculum-architect.md and quiz-master.md partial re-run sections now require a **diff-before-claim** step — agents must list exactly which fields changed per item/LO, verified against the input file, before reporting.

### What was NOT tested (deferred)

- `S1.C2` pure class re-run (slide + note + transcript regen; cache-hit check for S1.C1). Invariants already demonstrated in Tests A+B, so added value is limited.
- `S1.C2.tone=formal` — **blocked by a schema gap**: there is no per-class tone storage slot anywhere in `_workspace/` or beat files. Options: (a) add `tone_override` to class beats, (b) add `class_overrides: {cid: {tone}}` to course_spec.json, (c) treat scope as ephemeral (pass to authors directly, no persistence). Needs a design call before implementation.
- Revise-loop in regression mode. All tests hit PASS first try. Worth seeding an intentional defect (e.g., delete a quiz item's `lo_ids` pointer) and observing the reviewer→author revise chain on a scoped run.
- Multi-section partial re-run (out of reach on this 1-section fixture).

### Methodological win (landed)

The architect's choice to use **`Edit` (not `Write`)** for partial re-runs is the *only* mechanism that guarantees byte-level identity of untouched LO entries (avoids formatter drift in quote style, whitespace, Unicode form, key order). **Fix landed:** curriculum-architect.md and quiz-master.md partial re-run sections now explicitly prescribe `Edit` with a minimal `old_string` that excludes preserved entries — `Write` with re-serialized JSON is forbidden.

---

**End of handoff.** When starting fresh, read this top-to-bottom before the first tool call. ~10 min of reading saves ~1 hour of rediscovery.
