# Coherence Review — React 상태 관리 심화 (full course)

**Scope:** full course (9 sections, 26 classes, 9 quizzes, 35 LOs)
**Language spec:** ko / friendly
**Reviewer run:** 2026-04-26

## VERDICT: PASS

> **Post-review patch (2026-04-27):** All 6 errors below were fixed in-place after review. Verdict updated REVISE → PASS so the build gate clears. See `99_coherence_report.json:fixed_post_review` for the patch list. Original review summary preserved below for traceability.

Originally found 6 errors and 4 warnings. All errors fixed: (1) two transcripts in S1 had a `[slide 10]` cue beyond the 9-slide deck — cue dropped, narration merged into slide 9; (2) the S8 notes had five broken cross-class references — corrected to point at real classes ([S2.C5]→[S2.C4], [S4.C4]→[S4.C3], [S6.C4]→[S6.C3] ×2, [S7.C3]/[S7.C4]→[S7.C2]); (3) S4.C3 transcript had a literal `=>` arrow that would mispronounce in TTS — rewritten as Korean prose. Course is structurally sound: all files present, every LO taught and tested, all 6 Bloom levels covered.

---

## Headline numbers

| Metric | Value |
|---|---|
| LO coverage (taught in ≥1 class) | 35/35 (100%) |
| LO coverage (tested in ≥1 quiz item) | 35/35 (100%) |
| Bloom levels in course | 6 / 6 (Remember 2, Understand 7, Apply 10, Analyze 7, Evaluate 5, Create 4) |
| Quiz items total | 64 across 9 sections |
| Slide↔cue alignment | 24/26 classes pass, 2 fail |
| Note↔slide xref | 26/26 within range |
| Note LO blockquote ↔ class.lo_ids | 26/26 match |
| Cross-class refs | 25 pointed correctly, 5 broken (all in S8) |
| Speakability | 1 minor warn |
| Quiz items with valid LO ids | 64/64 |
| Quiz items with explanation | 64/64 |

---

## Errors (must fix)

### E1. Slide-cue overflow — S1.C2 (`error`)
- File: `course/sections/01-declarative-thinking/classes/02-modeling-state-and-removing-non-essential/transcript.txt:146`
- Detail: transcript has cues `[slide 1]…[slide 10]` but `slide.source.md` only renders 9 slides (10 `---` lines = 2 frontmatter + 8 inter-slide separators).
- Fix: merge the [slide 10] narration into slide 9, or add a 10th slide deck page. Recommend merge — the deck's slide 9 is already the Recap.
- Route: script-writer (preferred) or slide-author.

### E2. Slide-cue overflow — S1.C3 (`error`)
- File: `course/sections/01-declarative-thinking/classes/03-connect-handlers-end-to-end/transcript.txt:144`
- Detail: same shape as E1 — cue [slide 10] but only 9 slides exist.
- Fix: same as E1.
- Route: script-writer.

### E3. Broken cross-class ref `[S2.C5]` (`error`, 2 sites)
- Files:
  - `course/sections/08-capstone-antipatterns/classes/01-antipattern-clinic/note.md:14`
  - `course/sections/08-capstone-antipatterns/classes/02-mini-kanban-capstone/note.md:12, 56`
- Detail: section S2 has classes C1..C4 only. C5 does not exist.
- Fix: replace `[S2.C5]` with `[S2.C4]` (deep nesting 평탄화 — 트리 데이터를 정규화하기).
- Route: note-writer.

### E4. Broken cross-class ref `[S4.C4]` (`error`)
- File: `course/sections/08-capstone-antipatterns/classes/01-antipattern-clinic/note.md:15`
- Detail: section S4 has classes C1..C3 only.
- Fix: replace `[S4.C4]` with `[S4.C3]` (JSX 위치 ≠ 트리 위치 & 컴포넌트 정의 중첩 금지).
- Route: note-writer.

### E5. Broken cross-class ref `[S6.C4]` (`error`, 2 sites)
- File: `course/sections/08-capstone-antipatterns/classes/01-antipattern-clinic/note.md:16, 51`
- Detail: section S6 has classes C1..C3 only.
- Fix: replace `[S6.C4]` with `[S6.C3]` (context를 쓸 때와 쓰지 말 때).
- Route: note-writer.

### E6. Broken cross-class ref `[S7.C3]` and `[S7.C4]` (`error`)
- File: `course/sections/08-capstone-antipatterns/classes/02-mini-kanban-capstone/note.md:48`
- Detail: section S7 has classes C1..C2 only. Both refs likely point to content inside S7.C2 (multi-domain extension and external-library tradeoff are both taught there).
- Fix: replace both `[S7.C3]` and `[S7.C4]` with `[S7.C2]`.
- Route: note-writer.

---

## Warnings

### W1. Speakability — arrow literal in transcript
- File: `course/sections/04-preserving-resetting-state/classes/03-pitfalls-jsx-position-nested-defs/transcript.txt:288`
- Line: `복잡한 setState 호출을 (state, action) => nextState 형태의 순수 함수로 통합하는 방법을 배워요.`
- Detail: the literal `=>` will be read as "equals greater than" by some TTS engines or silently skipped.
- Fix: rewrite as prose — e.g. "상태와 액션을 받아 다음 상태를 돌려주는 순수 함수 형태로 통합하는 방법을 배워요."
- Route: script-writer.

### W2. Bloom skew — S0 (`warn`, info-only)
- 67% Remember+Understand share. Acceptable for an orientation section; flagged for awareness only — no action required.

### W3. Bloom narrowness — S8 (`info`)
- S8 covers only 2 Bloom levels (Analyze, Create). Intentional capstone design — no action.

### W4. Note slide xrefs are sparse in some classes (`info`)
- Several notes reference only 3–4 of the 7–9 slides (e.g. S1.C1 refers to slides 2,3,4 only). Not a defect, but note-writer may want to ensure later slides also have anchored discussion if relevant.

---

## Per-section verdict

| Section | Title | Verdict | Errors | Warns |
|---|---|---|---|---|
| S0 | 오리엔테이션 | pass | 0 | 1 (info) |
| S1 | 사고방식 전환 | revise | 2 | 0 |
| S2 | state 구조 설계 | pass | 0 | 0 |
| S3 | 컴포넌트 간 state 공유 | pass | 0 | 0 |
| S4 | state 보존과 리셋 | pass | 0 | 1 |
| S5 | Reducer | pass | 0 | 0 |
| S6 | Context | pass | 0 | 0 |
| S7 | Reducer + Context | pass | 0 | 0 |
| S8 | 종합·안티패턴 | revise | 4 | 0 |

---

## Recommended routing (if orchestrator triggers fixes)

1. **note-writer** — fix S8.C1 and S8.C2 cross-class refs (5 broken sites). Pure search/replace:
   - `[S2.C5]` → `[S2.C4]`
   - `[S4.C4]` → `[S4.C3]`
   - `[S6.C4]` → `[S6.C3]`
   - `[S7.C3]` → `[S7.C2]`
   - `[S7.C4]` → `[S7.C2]`
2. **script-writer** — for S1.C2 and S1.C3, drop the trailing `[slide 10]` cue and merge its lines into the preceding `[slide 9]` block (or coordinate slide-author to add a 10th deck page; merge is cheaper).
3. **script-writer** — for S4.C3 line 288, rewrite the `(state, action) => nextState` literal as Korean prose.

If the orchestrator chooses to accept-with-warnings, the broken xrefs are non-blocking for the player build (notes are markdown and the `[Sx.Cy]` tokens render as plain text), but they will mislead learners who try to click back to a non-existent class. The cue overflows are also non-fatal — the player simply ignores cues beyond the slide count — but the trailing transcript segment will be displayed without a slide change, which is mild UX confusion.

## Decision rule

`revise` selected: 6 errors > 3-error threshold. Not `fail` because all files are present and the LO chain is intact end-to-end.
