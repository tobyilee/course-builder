# Session Handoff — AI Course Builder

**Last updated:** 2026-04-23 (session `1b0b191c`)
**Author:** Claude Opus 4.7 (1M context) w/ toby

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

### ⚠️ Security status
- `.env` file in repo root contains real OpenAI API key: `sk-proj-NC2aMjOB...KG8b20A`
- Key was pasted in conversation transcript on ~2026-04-22 — **reachable in session jsonl file**
- Key has **not been confirmed revoked** by user
- **Highest-priority next action: rotate the key**

### Shell gotchas observed
- Bash tool's `cd` doesn't persist across tool calls — use absolute paths
- `python3 ... | tee log` returns tee's exit code, not python's — use `set -o pipefail` + `PIPESTATUS[0]` (already addressed in `tts-synthesis/scripts/run.sh`)
- Long-running background jobs in Claude Code shell can be killed by session lifecycle events — prefer parallel short-lived jobs over single long serial job (already addressed by smart TTS caching)
- `find` order on macOS is not alphabetical — `synthesize-tts.py` does slide-order mapping internally, but don't assume find-order == section order

## 6. Next steps — prioritized

### Priority 1 (do before anything else)

- [ ] **Rotate OpenAI API key** — https://platform.openai.com/api-keys; revoke `sk-proj-NC2aMjOB...KG8b20A`
- [ ] Update `.env` with new key
- [ ] Verify: `source .env && echo $OPENAI_API_KEY | head -c 12` shows new prefix

### Priority 2 (if continuing Phase 7 evolution)

- [ ] **slide-author emits `beat_id` in Marp frontmatter** — current beat↔slide mapping uses a proportional stretch heuristic (~80% accurate). Direct `beat_id` would give 100% affect-injection accuracy. Touch: `.claude/agents/slide-author.md`, `.claude/skills/slide-authoring/SKILL.md`, `scripts/synthesize-tts.py:build_slide_to_affect`.
- [ ] **Subtitle sync** — during audio playback, highlight the currently-spoken line in the transcript panel. Requires TTS synthesis to emit timing per chunk (e.g., use edge-tts `--write-subtitles` or OpenAI's timestamp extension). Touch: `scripts/synthesize-tts.py` to emit timing JSON, `scripts/generate-player.py` to bind to `audio.ontimeupdate`.
- [ ] **localStorage resume** — remember last-played `{class_id, slide_idx, audio.currentTime}`. On player load, prompt "이어 듣기?". Touch: player JS in `generate-player.py`.
- [ ] **Duration feedback loop** — `script-writer` agent reads previous run's `manifest.stats.actual_audio_duration_sec` vs `target_duration_min * 60` and auto-calibrates next run's script length. Touch: `.claude/agents/script-writer.md`, `.claude/skills/script-writing/SKILL.md`.

### Priority 3 (polish)

- [ ] **`.env.example`** — placeholder template, committed, so others can clone and configure
- [ ] **LICENSE** — README says MIT but no LICENSE file in repo. Add one.
- [ ] **CI recipe** — GitHub Action runs orchestrator on canary topic; fails if coherence doesn't pass. Useful for contributor PRs.
- [ ] **Screenshot for README** — use Playwright or `puppeteer-screenshot-cli` to capture `player.html` in dark theme, add to README banner section.

### Priority 4 (larger scope)

- [ ] **Longer course scale test** — 60min, 4-5 sections. Surfaces unseen issues (section-level dependency graph, cross-section LO drift, larger Bloom spread).
- [ ] **Partial re-run testing** — "Change S1.C2 tone to formal, leave rest" — exercise the stability of LO ids and cache-hit paths. Document the command flow.
- [ ] **Non-code domain** — try a marketing/leadership topic to verify the hardness works without code-heavy content (tests whether slide-author still produces meaningful visuals without code blocks).
- [ ] **Multilingual** — run same topic in English, verify tone/voice/Bloom all adapt.

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

## 8. Known ugly corners

- `scripts/generate-player.py` is ~720 lines, heavy string formatting. Refactor candidate: split into template files + a small orchestrator. Low priority.
- `scripts/synthesize-tts.py` line 153 `from openai import OpenAI` is lazy-imported; Pyright warns it can't resolve. Real import works; warning is noise.
- `_workspace/99_coherence_report.md` isn't hand-tuned for readability; it's a machine-friendly dump. If you want a nicer report surface, that's a standalone polish.
- `synth-manifest.py` writes `meta/audience.md` only if missing — never updates on re-run. If audience changes in spec, old meta/ lingers. Minor.

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
