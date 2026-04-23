# Roadmap & Durable Project State — AI Course Builder

> **Scope of this file.** Forward-looking roadmap, locked-in decisions, and known traps.
> Per-session handoff snapshots live under `.claude/reports/handoff/` (gitignored) and
> are consumed by the `toby-essentials:catchup` skill at session start.

---

## 1. Environment state

### Tools verified working
- `marp` (Marp CLI) — used by build-bundle.sh for HTML + PNG render
- `ffmpeg` — silence + concat for TTS pipeline
- `edge-tts` 7.2.8 — fallback TTS
- Python 3.10.18 (pyenv)
- `openai` 2.32.0 Python SDK
- GitHub CLI at `/opt/homebrew/bin/gh` (authenticated as `tobyilee`)
- `jq`, `xmllint`, `zip`

### Security status
- OpenAI API key stored in `.env` (gitignored, not tracked) — format uses `export OPENAI_API_KEY=<key>` (shell-source friendly).
- Key was rotated 2026-04-23; old key `sk-proj-NC2aMjOB...KG8b20A` revoked in OpenAI dashboard.

### Shell gotchas observed
- Bash tool's `cd` doesn't persist across tool calls — use absolute paths.
- `python3 ... | tee log` returns tee's exit code, not python's — use `set -o pipefail` + `PIPESTATUS[0]` (already addressed in `tts-synthesis/scripts/run.sh`).
- Long-running background jobs in Claude Code shell can be killed by session lifecycle events — prefer parallel short-lived jobs over single long serial job (already addressed by smart TTS caching).
- `find` order on macOS is not alphabetical — `synthesize-tts.py` does slide-order mapping internally, but don't assume find-order == section order.

---

## 2. Next steps — prioritized

### Priority 1 (do before anything else) — ✅ DONE 2026-04-23
- [x] **Rotate OpenAI API key** — old key revoked in dashboard.
- [x] Update `.env` with new key (paste artifact `- ` cleaned).
- [x] Verify: `source .env` + OpenAI `models.list` live call succeeded (128 models, `gpt-4o-mini-tts` accessible).

### Priority 2 (Phase 7 evolution)
- [x] **localStorage resume** — DONE session 2 (commit `196eba9`). Per-class state (page pathname as key), 30d expiry, 3s throttle.
- [x] **Multilingual** (ko/en) — DONE session 2 (commits `50f43c6`, `06bfca9`, `2494607`). Full pipeline: agents, TTS engine, player chrome, quiz.html, index.html landing. End-to-end smoke test passed on a Git-rebase 10min English course.
- [x] **Playback-speed button** — DONE session 2 (commit `2494607`). Cycle button 0.75× → 2×, localStorage-persisted, preservesPitch.
- [x] **slide-author emits `beat_id` in Marp frontmatter** — DONE session 3 (commit `629a4f3`, T2). Per-slide `<!-- beat: bN -->` HTML comment; `synthesize-tts.py` parses via `_parse_beat_ids_from_slides` and falls back to proportional heuristic when absent. 100% affect-injection accuracy on new decks; existing decks unchanged.
- [~] **Subtitle sync** — session 3 shipped char-proportional **line-level** MVP (commit `eccab20`, T4). `generate-player.py` embeds per-line `{start,end}` derived from slide MP3 duration split by character-weight; timeupdate listener toggles `.active` + scrollIntoView. Word-accurate timing via Whisper-align **still deferred** — SKILL.md reserves a `audio/slide_NN.timing.json` sidecar format for that future upgrade.
- [x] **Duration feedback loop** — DONE session 3 (commit `c9831df`, T3). `synth-manifest.py` now records per-class `actual_audio_duration_sec`; `script-writer` reads previous run's `course_prev_*/manifest.json`; `script-writing/SKILL.md` has the calibration formula (clamped to `[0.7, 1.4]`).
- [x] **🐛 Coherence-reviewer JSON emission** — DONE session 3 (commit `3087860`, T1). Root cause was actually **JSON↔MD verdict divergence** (JSON=pass, MD=REVISE left behind after revise loop), not missing JSON. Fix: reviewer agent + SKILL now require atomic dual-write and same-verdict emit; `build-bundle.sh` logs WARN on mismatch.

### Priority 3 (polish)
- [x] **`.env.example`** — DONE session 2 (commit `bfe1e6e`).
- [x] **LICENSE** — DONE session 2 (commit `bfe1e6e`).
- [x] **Screenshot for README** — DONE session 2 (commit `bfe1e6e`). Dark-theme Chrome headless.
- [ ] **CI recipe** — GitHub Action that runs the non-generative asset pipeline (marp + ffmpeg + coherence gate + manifest + player) against a pre-built canary fixture with `SKIP_TTS=1`. Does NOT need Anthropic API key — Claude agents are not invoked in CI. **Draft built in session 3 then deferred** (user chose to defer; `gh` OAuth token also lacked `workflow` scope to push). Draft preserved: reflog commit **`bba03db`** contains `.github/workflows/build-canary.yml` + `.github/fixtures/canary/` (108 KB source-only fixture) + `.gitignore` anchoring fix + README badge. Resurrect with `git cherry-pick bba03db` when ready; ensure `gh auth refresh -s workflow` first.

### Priority 4 (larger scope)
- [ ] **Longer course scale test** — 60min, 4-5 sections. Surfaces unseen issues (section-level dependency graph, cross-section LO drift, larger Bloom spread).
- [~] **Partial re-run testing** — session 3 shipped the **contract** (commit `3171b61`, T6); session 4 **end-to-end exercised** it on the Git-rebase fixture. Two scopes ran green: `S1.quiz` (quiz-master polish pass, 7/7 item ids preserved, Bloom delta=0) and `S1` with LO addition (architect appended LO-1.5, lines 1-24 of LOs file **byte-identical** via Edit-not-Write). **3 real edge cases surfaced + 1 methodological win** — all landed as T7 contract patches (commit `4b932f7`). Still untested: multi-section partial re-run, `S1.C2.tone=formal` (blocked by per-class-tone storage gap — needs schema decision: `tone_override` on beats / `class_overrides` dict / ephemeral-only), revise-loop in regression mode.
- [ ] **Non-code domain** — try a marketing/leadership topic to verify the harness works without code-heavy content (tests whether slide-author still produces meaningful visuals without code blocks).

### Priority 5 (vision)
- [ ] **SCORM/xAPI export** — LMS integration. Today explicit Non-Goal; could be added as a post-build step reading `manifest.json`.
- [ ] **Image generation** — optional hero PNG per class via DALL-E / SDXL.
- [ ] **Quiz grading via LLM** — `short_answer` items currently rely on rubric self-grading; could auto-grade with a rubric-prompted API call.

---

## 3. Decisions made (don't relitigate without reason)

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
| Partial re-run uses `Edit` (not `Write`) for byte-identity preservation | `Write` with re-serialized JSON drifts on quote style, whitespace, Unicode form, key order — breaks LO id stability | Session 4 T7 (commit `4b932f7`) |
| Coherence verdict JSON↔MD match is case-insensitive | `build-bundle.sh:L48` already normalizes via `tr lowercase`; docs now agree | Session 4 T7 (commit `4b932f7`) |
| Per-session handoffs live in `.claude/reports/handoff/` (gitignored); roadmap + decisions live in this file | Handoff is session snapshot (hypothesis); roadmap is durable project state. Different lifecycles, different files | Session 5 split |

---

## 4. Known ugly corners

- `scripts/generate-player.py` grew from ~720 to ~860 lines in session 2 (i18n + resume + speed). Still heavy string formatting. Refactor candidate: split into template files + a small orchestrator. Low priority.
- `scripts/synthesize-tts.py` line 153 `from openai import OpenAI` is lazy-imported; Pyright warns it can't resolve. Real import works; warning is noise.
- `_workspace/99_coherence_report.md` isn't hand-tuned for readability; it's a machine-friendly dump. If you want a nicer report surface, that's a standalone polish.
- `synth-manifest.py` writes `meta/audience.md` only if missing — never updates on re-run. If audience changes in spec, old meta/ lingers. Minor.
- **Coherence JSON/MD mismatch legacy artifact** — session 3 (T1) locked down the atomic dual-write + verdict-sync contract on the reviewer side and added a non-fatal WARN on the build gate. Any historical divergent `_workspace/99_coherence_report.md` left as-is on purpose (proves T1's WARN fires). Next revise-loop run should overwrite both files with matching verdicts.
- `generate-player.py:678` Pyright warning about unused `current_cls_slug` parameter in `make_toc_html` — pre-existing, leave as-is (dead param kept for signature stability).
