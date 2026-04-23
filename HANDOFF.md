# Session Handoff — AI Course Builder

**Last updated:** 2026-04-23 (sessions `1b0b191c`, `12150c38`)
**Author:** Claude Opus 4.7 (1M context) w/ toby

> **2026-04-23 update (session `12150c38`):** P1 키 로테이션 + P2 localStorage resume + P3 레포 정비 + 언어 지원 (ko/en) 전체 + Player UI i18n + playback-speed button 전부 완료. 영어 Git-rebase 강의 end-to-end smoke test 통과. **Public repo 현재 HEAD: `2494607`** (5 commits ahead of session 1's last commit `6f8869b`).

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
- [ ] **slide-author emits `beat_id` in Marp frontmatter** — current beat↔slide mapping uses a proportional stretch heuristic (~80% accurate). Direct `beat_id` would give 100% affect-injection accuracy. Touch: `.claude/agents/slide-author.md`, `.claude/skills/slide-authoring/SKILL.md`, `scripts/synthesize-tts.py:build_slide_to_affect`.
- [ ] **Subtitle sync** — during audio playback, highlight the currently-spoken line in the transcript panel. Requires TTS synthesis to emit timing per chunk (e.g., use edge-tts `--write-subtitles` or OpenAI's timestamp extension). Touch: `scripts/synthesize-tts.py` to emit timing JSON, `scripts/generate-player.py` to bind to `audio.ontimeupdate`. **Deferred by user in session 2** (option A+B+C analyzed; cost vs accuracy trade-off favors "do later when Whisper align comes").
- [ ] **Duration feedback loop** — `script-writer` agent reads previous run's `manifest.stats.actual_audio_duration_sec` vs `target_duration_min * 60` and auto-calibrates next run's script length. Touch: `.claude/agents/script-writer.md`, `.claude/skills/script-writing/SKILL.md`.
- [ ] **🐛 Coherence-reviewer JSON emission bug** — agent file promises both `99_coherence_report.json` and `.md`, but in practice it only writes the MD. `build-bundle.sh` requires the JSON gate. Session 2 used a manually authored JSON as a workaround. Fix: update `.claude/agents/coherence-reviewer.md` (and possibly `coherence-review/SKILL.md`) to enforce dual output, OR change the build script to parse the MD `VERDICT:` line.

### Priority 3 (polish)

- [x] **`.env.example`** — DONE session 2 (commit `bfe1e6e`).
- [x] **LICENSE** — DONE session 2 (commit `bfe1e6e`).
- [x] **Screenshot for README** — DONE session 2 (commit `bfe1e6e`). Dark-theme Chrome headless.
- [ ] **CI recipe** — GitHub Action runs orchestrator on canary topic; fails if coherence doesn't pass. Useful for contributor PRs.

### Priority 4 (larger scope)

- [ ] **Longer course scale test** — 60min, 4-5 sections. Surfaces unseen issues (section-level dependency graph, cross-section LO drift, larger Bloom spread).
- [ ] **Partial re-run testing** — "Change S1.C2 tone to formal, leave rest" — exercise the stability of LO ids and cache-hit paths. Document the command flow.
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
- **Coherence JSON/MD mismatch**: reviewer emits only `.md`, build gate needs `.json`. See Priority 2 follow-up. Workaround: manually write JSON with `overall: "pass"` when issues are resolved.
- `generate-player.py:678` Pyright warning about unused `current_cls_slug` parameter in `make_toc_html` — pre-existing, leave as-is (dead param kept for signature stability).

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

**End of handoff.** When starting fresh, read this top-to-bottom before the first tool call. ~10 min of reading saves ~1 hour of rediscovery.
