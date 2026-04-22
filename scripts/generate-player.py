#!/usr/bin/env python3
"""
Generate a self-contained HTML player for the course.

Produces:
  course/index.html                                    — course home, TOC
  course/sections/<sec>/quiz.html                      — interactive quiz per section
  course/sections/<sec>/classes/<cls>/player.html      — slide+audio+transcript player

Inputs: course/manifest.json + per-class assets (slides_png/, audio/, transcript.txt).
Idempotent — overwrites existing player/quiz/index HTML.
"""
import argparse
import html
import json
import re
import subprocess
from pathlib import Path

SLIDE_RE = re.compile(r'^\s*\[slide\s+(\d+)\]\s*$')
PAUSE_RE = re.compile(r'\[pause:(\d+)\]')


# ── i18n strings for player chrome (slide-deck UI) ──────────────────────────
# Scope: player.html only. quiz.html chrome and course index.html landing
# remain in Korean; their i18n is follow-up work.
_PLAYER_STRINGS = {
    "ko": {
        "menu_title": "목차 열기/닫기",
        "home": "홈",
        "slide_label": "슬라이드",
        "slide_unit": "장",
        "min_unit": "분",
        "prev": "이전",
        "play": "재생",
        "pause": "일시정지",
        "next": "다음",
        "transcript_h2": "발화 스크립트",
        "end_title": "수업을 완료했어요!",
        "end_sub": "다음으로 이동하거나 배운 내용을 점검해보세요.",
        "resume_prefix": "이전 위치",
        "resume_yes": "이어 듣기",
        "resume_no": "처음부터",
        "quiz_cta_footer": "섹션 퀴즈 풀기",
        "back_to_toc": "목차로",
        "cta_this_section": "이 섹션",
        "cta_final_quiz": "마지막 퀴즈 풀기",
        "cta_done": "완료",
        "cta_course_toc": "코스 목차로",
        "cta_check_section": "이 섹션 점검",
        "cta_section_quiz": "섹션 퀴즈 풀기",
        "cta_next_section": "다음 섹션",
        "cta_next_class": "다음 수업",
        "cta_check_first": "먼저 점검",
        "cta_section_quiz_short": "섹션 퀴즈",
        "cta_continue": "계속 학습",
        "toc_quiz_tpl": "섹션 퀴즈 ({n}문항)",
    },
    "en": {
        "menu_title": "Toggle TOC",
        "home": "Home",
        "slide_label": "Slide",
        "slide_unit": " slides",
        "min_unit": " min",
        "prev": "Prev",
        "play": "Play",
        "pause": "Pause",
        "next": "Next",
        "transcript_h2": "Transcript",
        "end_title": "You finished the class!",
        "end_sub": "Move on to the next step, or review what you just learned.",
        "resume_prefix": "Previous position",
        "resume_yes": "Resume",
        "resume_no": "Start over",
        "quiz_cta_footer": "Take section quiz",
        "back_to_toc": "Back to TOC",
        "cta_this_section": "This section",
        "cta_final_quiz": "Take the final quiz",
        "cta_done": "Done",
        "cta_course_toc": "Back to course TOC",
        "cta_check_section": "Review this section",
        "cta_section_quiz": "Take section quiz",
        "cta_next_section": "Next section",
        "cta_next_class": "Next class",
        "cta_check_first": "Check first",
        "cta_section_quiz_short": "Section quiz",
        "cta_continue": "Continue",
        "toc_quiz_tpl": "Section quiz ({n} items)",
    },
}


def _tx(lang: str) -> dict:
    return _PLAYER_STRINGS.get(lang, _PLAYER_STRINGS["ko"])


def parse_transcript_by_slide(text: str) -> dict:
    """Return {slide_no: [line, ...]} with [pause:N] stripped."""
    out = {}
    current = None
    for line in text.splitlines():
        m = SLIDE_RE.match(line)
        if m:
            current = int(m.group(1))
            out[current] = []
            continue
        if current is None:
            continue
        cleaned = PAUSE_RE.sub("", line).strip()
        if cleaned:
            out[current].append(cleaned)
    return out


def mp3_duration(path: Path) -> float:
    if not path.exists():
        return 0.0
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


PLAYER_TMPL = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Pretendard",sans-serif;background:#0f1115;color:#e8eaed;line-height:1.55}}
  a{{color:#7cb7ff;text-decoration:none}}a:hover{{text-decoration:underline}}
  header{{padding:12px 20px;border-bottom:1px solid #1f2430;display:flex;gap:16px;align-items:baseline;flex-wrap:wrap}}
  header h1{{font-size:18px;margin:0;font-weight:600}}
  .meta{{color:#8b95a7;font-size:13px}}
  button.menu-toggle{{background:transparent;border:1px solid #2a3345;color:#e8eaed;border-radius:6px;padding:6px 10px;font-size:14px;cursor:pointer}}
  button.menu-toggle:hover{{background:#222a3a}}
  /* Progress bar */
  #progress{{padding:10px 20px;background:#12151c;border-bottom:1px solid #1f2430;display:flex;gap:14px;align-items:center;font-size:13px;color:#8b95a7}}
  #progress .bar{{flex:1;height:4px;background:#1f2430;border-radius:2px;overflow:hidden}}
  #progress .bar .fill{{height:100%;background:linear-gradient(90deg,#2d6cdf,#5ea0ff);border-radius:2px;transition:width .3s ease}}
  #progress .label{{white-space:nowrap}}
  #progress strong{{color:#e8eaed;font-weight:600}}
  /* Sidebar */
  aside#toc{{background:#12151c;border-right:1px solid #1f2430;padding:16px 14px;overflow-y:auto;max-height:calc(100vh - 130px);position:sticky;top:0}}
  aside#toc h3{{font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:#8b95a7;margin:14px 0 6px 0;font-weight:500}}
  aside#toc h3:first-child{{margin-top:0}}
  aside#toc ul{{list-style:none;padding:0;margin:0 0 12px 0}}
  aside#toc li{{padding:6px 8px;border-radius:6px;margin-bottom:2px;font-size:13px}}
  aside#toc a{{color:#c4cad6;text-decoration:none;display:block}}
  aside#toc a:hover{{color:#fff}}
  aside#toc li:hover{{background:#1a1f29}}
  aside#toc li.current{{background:#1a2e4a;border-left:3px solid #2d6cdf}}
  aside#toc li.current a{{color:#fff;font-weight:600}}
  aside#toc li.quiz a{{color:#3a8a4f}}
  main{{display:grid;grid-template-columns:220px 1fr 320px;gap:16px;padding:16px;max-width:1700px;margin:0 auto;align-items:start}}
  @media(max-width:1280px){{main{{grid-template-columns:1fr 320px}} aside#toc{{display:none}} aside#toc.open{{display:block;position:fixed;top:0;left:0;width:260px;height:100vh;z-index:100;box-shadow:4px 0 20px rgba(0,0,0,.4);max-height:100vh}}}}
  @media(max-width:980px){{main{{grid-template-columns:1fr}}}}
  #stage{{background:#181c26;border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:10px}}
  #slide-wrap{{aspect-ratio:16/9;background:#000;border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center}}
  #slide{{max-width:100%;max-height:100%;display:block}}
  #controls{{display:flex;gap:8px;align-items:center;padding:6px 2px}}
  button{{background:#222a3a;color:#e8eaed;border:1px solid #2a3345;border-radius:6px;padding:8px 14px;font-size:14px;cursor:pointer}}
  button:hover{{background:#2a3547}}
  button:disabled{{opacity:.4;cursor:not-allowed}}
  button.play{{background:#2d6cdf;border-color:#2d6cdf;font-weight:600;min-width:100px}}
  button.play:hover{{background:#3578e5}}
  #pos{{color:#8b95a7;font-size:13px;margin-left:auto}}
  audio{{width:100%}}
  aside#transcript{{background:#181c26;border-radius:12px;padding:16px;max-height:calc(100vh - 200px);overflow-y:auto}}
  aside#transcript h2{{margin:0 0 10px 0;font-size:14px;color:#8b95a7;font-weight:500;text-transform:uppercase;letter-spacing:.5px}}
  #tx-body p{{margin:0 0 8px 0}}
  #thumbs{{display:flex;gap:8px;padding:12px 16px;overflow-x:auto;border-top:1px solid #1f2430;background:#12151c}}
  .thumb{{flex:0 0 120px;aspect-ratio:16/9;border-radius:4px;overflow:hidden;cursor:pointer;border:2px solid transparent;position:relative}}
  .thumb.current{{border-color:#2d6cdf}}
  .thumb img{{width:100%;height:100%;object-fit:cover}}
  .thumb span{{position:absolute;bottom:2px;right:4px;background:rgba(0,0,0,.7);color:#fff;font-size:10px;padding:1px 4px;border-radius:2px}}
  #end-panel{{margin:24px auto;max-width:900px;padding:28px 24px;background:linear-gradient(135deg,#1a2e4a,#162138);border:1px solid #2d6cdf;border-radius:14px;text-align:center;display:none}}
  #end-panel.active{{display:block;animation:slideIn .4s ease-out}}
  @keyframes slideIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
  #end-panel h2{{margin:0 0 6px 0;font-size:22px;color:#fff}}
  #end-panel .sub{{color:#8fb3e8;margin-bottom:20px;font-size:14px}}
  .end-actions{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
  .btn-cta{{display:inline-flex;align-items:center;gap:8px;padding:12px 22px;border-radius:8px;font-size:15px;font-weight:600;text-decoration:none;transition:transform .1s,background .15s}}
  .btn-cta.primary{{background:#2d6cdf;color:#fff;border:1px solid #2d6cdf}}
  .btn-cta.primary:hover{{background:#3578e5;transform:translateY(-1px)}}
  .btn-cta.secondary{{background:#222a3a;color:#e8eaed;border:1px solid #2a3345}}
  .btn-cta.secondary:hover{{background:#2a3547}}
  .btn-cta .label{{font-size:12px;opacity:.75;font-weight:400;display:block;margin-bottom:1px}}
  .btn-cta .title{{display:block}}
  footer{{padding:14px 20px;text-align:center;border-top:1px solid #1f2430;color:#8b95a7;font-size:13px}}
  footer a{{margin:0 10px}}
  /* Resume banner */
  #resume-banner{{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#1a2e4a;border:1px solid #2d6cdf;border-radius:10px;padding:10px 14px;display:none;gap:12px;align-items:center;z-index:60;box-shadow:0 6px 24px rgba(0,0,0,.5);max-width:92%;flex-wrap:wrap}}
  #resume-banner.show{{display:flex}}
  #resume-banner .text{{font-size:13px;color:#c4cad6}}
  #resume-banner .text strong{{color:#fff}}
  #resume-banner button{{padding:6px 12px;font-size:13px;margin:0}}
  #resume-banner button.primary{{background:#2d6cdf;border-color:#2d6cdf;color:#fff;font-weight:600}}
</style>
</head>
<body>
<header>
  <button class="menu-toggle" id="menu-toggle" title="{tx_menu_title}">☰</button>
  <a href="{back_href}">← {tx_home}</a>
  <h1>{title}</h1>
  <span class="meta">LOs: {lo_ids} · {slide_count}{tx_slide_unit} · {duration_min}{tx_min_unit}</span>
</header>

<div id="progress">
  <span class="label"><strong>Class {class_number}</strong> / {total_classes}</span>
  <div class="bar"><div class="fill" id="course-fill" style="width:{course_progress_pct}%"></div></div>
  <span class="label">{tx_slide_label} <strong id="slide-num">1</strong> / {slide_count}</span>
  <div class="bar"><div class="fill" id="slide-fill"></div></div>
</div>

<main>
  <aside id="toc">
{toc_html}  </aside>
  <div id="stage">
    <div id="slide-wrap"><img id="slide" alt="slide"/></div>
    <div id="controls">
      <button id="prev">◀ {tx_prev}</button>
      <button id="play" class="play">▶ {tx_play}</button>
      <button id="next">{tx_next} ▶</button>
      <span id="pos">1 / {slide_count}</span>
    </div>
    <audio id="audio" preload="auto"></audio>
  </div>
  <aside id="transcript">
    <h2>{tx_transcript_h2}</h2>
    <div id="tx-body"></div>
  </aside>
</main>

<section id="thumbs"></section>

<section id="end-panel">
  <h2>🎉 {tx_end_title}</h2>
  <p class="sub">{tx_end_sub}</p>
  <div class="end-actions">{end_actions_html}</div>
</section>

<div id="resume-banner" role="dialog" aria-live="polite">
  <span class="text">🎧 {tx_resume_prefix}: <strong id="resume-pos">—</strong></span>
  <button id="resume-yes" class="primary">{tx_resume_yes}</button>
  <button id="resume-no">{tx_resume_no}</button>
</div>

<footer>
  <a href="{quiz_href}">📝 {tx_quiz_cta_footer}</a>
  <a href="{back_href}">{tx_back_to_toc}</a>
</footer>

<script>
const SLIDES = {slides_json};
let current = 0;
const img = document.getElementById('slide');
const audio = document.getElementById('audio');
const txBody = document.getElementById('tx-body');
const pos = document.getElementById('pos');
const thumbs = document.getElementById('thumbs');
const btnPrev = document.getElementById('prev');
const btnPlay = document.getElementById('play');
const btnNext = document.getElementById('next');

SLIDES.forEach((s, i) => {{
  const t = document.createElement('div');
  t.className = 'thumb';
  t.dataset.i = i;
  t.innerHTML = '<img src="' + s.png + '"/><span>' + (i+1) + '</span>';
  t.onclick = () => loadSlide(i, true);
  thumbs.appendChild(t);
}});

function loadSlide(i, autoplay, resumeTime) {{
  current = Math.max(0, Math.min(SLIDES.length - 1, i));
  const s = SLIDES[current];
  img.src = s.png;
  audio.src = s.mp3;
  if (resumeTime && resumeTime > 1) {{
    audio.addEventListener('loadedmetadata', () => {{
      const dur = audio.duration;
      if (isFinite(dur)) audio.currentTime = Math.min(resumeTime, Math.max(0, dur - 1));
    }}, {{ once: true }});
  }}
  pos.textContent = (current + 1) + ' / ' + SLIDES.length;
  btnPrev.disabled = current === 0;
  btnNext.disabled = current === SLIDES.length - 1;

  txBody.innerHTML = '';
  s.transcript.forEach(line => {{
    const p = document.createElement('p');
    p.textContent = line;
    txBody.appendChild(p);
  }});

  document.querySelectorAll('.thumb').forEach((t, idx) => t.classList.toggle('current', idx === current));
  const cur = document.querySelector('.thumb.current');
  if (cur) cur.scrollIntoView({{block:'nearest', inline:'center'}});

  maybeShowEnd();
  saveState();

  if (autoplay) audio.play().catch(() => {{}});
}}

// localStorage resume — key = page path so each class gets its own slot
const STORAGE_KEY = 'course-builder:' + location.pathname;
const STATE_MAX_AGE_MS = 30 * 86400 * 1000;
let lastSaveTs = 0;

function saveState() {{
  try {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify({{
      slide: current,
      time: audio.currentTime || 0,
      ts: Date.now()
    }}));
  }} catch(e) {{}}
}}
function loadResumeState() {{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (Date.now() - s.ts > STATE_MAX_AGE_MS) return null;
    if (typeof s.slide !== 'number' || s.slide < 0 || s.slide >= SLIDES.length) return null;
    // Don't bother prompting if they barely started
    if (s.slide === 0 && (s.time || 0) < 3) return null;
    return s;
  }} catch(e) {{ return null; }}
}}
function clearState() {{
  try {{ localStorage.removeItem(STORAGE_KEY); }} catch(e) {{}}
}}
function fmtTime(t) {{
  const sec = Math.max(0, Math.floor(t || 0));
  return Math.floor(sec/60) + ':' + String(sec%60).padStart(2,'0');
}}

audio.addEventListener('timeupdate', () => {{
  const now = Date.now();
  if (now - lastSaveTs > 3000) {{ saveState(); lastSaveTs = now; }}
}});

const endPanel = document.getElementById('end-panel');
const slideFill = document.getElementById('slide-fill');
const slideNumEl = document.getElementById('slide-num');
const toc = document.getElementById('toc');
const menuToggle = document.getElementById('menu-toggle');
menuToggle.addEventListener('click', () => toc.classList.toggle('open'));

function maybeShowEnd() {{
  if (current === SLIDES.length - 1) {{
    endPanel.classList.add('active');
  }} else {{
    endPanel.classList.remove('active');
  }}
  // Update progress bar
  const pct = ((current + 1) / SLIDES.length) * 100;
  slideFill.style.width = pct + '%';
  slideNumEl.textContent = current + 1;
}}

btnPrev.onclick = () => loadSlide(current - 1, true);
btnNext.onclick = () => loadSlide(current + 1, true);
btnPlay.onclick = () => audio.paused ? audio.play() : audio.pause();

audio.addEventListener('play', () => btnPlay.textContent = '⏸ {tx_pause}');
audio.addEventListener('pause', () => btnPlay.textContent = '▶ {tx_play}');
audio.addEventListener('ended', () => {{
  if (current < SLIDES.length - 1) {{
    loadSlide(current + 1, true);
  }} else {{
    maybeShowEnd();
    endPanel.scrollIntoView({{behavior:'smooth', block:'nearest'}});
  }}
}});

document.addEventListener('keydown', (e) => {{
  if (['INPUT','TEXTAREA'].includes(e.target.tagName)) return;
  if (e.key === ' ') {{ e.preventDefault(); btnPlay.click(); }}
  else if (e.key === 'ArrowRight') btnNext.click();
  else if (e.key === 'ArrowLeft') btnPrev.click();
}});

// Initial load — show resume banner if prior state exists, otherwise start at slide 0
const resumeState = loadResumeState();
loadSlide(0, false);
if (resumeState) {{
  document.getElementById('resume-pos').textContent =
    '{tx_slide_label} ' + (resumeState.slide + 1) + ' · ' + fmtTime(resumeState.time);
  const banner = document.getElementById('resume-banner');
  banner.classList.add('show');
  document.getElementById('resume-yes').onclick = () => {{
    banner.classList.remove('show');
    loadSlide(resumeState.slide, true, resumeState.time);
  }};
  document.getElementById('resume-no').onclick = () => {{
    banner.classList.remove('show');
    clearState();
  }};
}}
</script>
</body>
</html>
"""


QUIZ_TMPL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{section_title} · 퀴즈</title>
<style>
  body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;background:#0f1115;color:#e8eaed;line-height:1.6}}
  .wrap{{max-width:760px;margin:0 auto;padding:24px 20px 80px}}
  a{{color:#7cb7ff;text-decoration:none}}a:hover{{text-decoration:underline}}
  h1{{font-size:24px;margin:0 0 4px 0}}
  .meta{{color:#8b95a7;margin-bottom:24px;font-size:14px}}
  .q{{background:#181c26;border-radius:12px;padding:20px;margin-bottom:16px}}
  .q .tag{{display:inline-block;background:#2a3345;color:#9fb0cc;padding:2px 8px;border-radius:4px;font-size:11px;margin-right:6px}}
  .q h3{{margin:6px 0 14px 0;font-size:16px;line-height:1.5}}
  .choice{{display:flex;gap:10px;padding:10px 12px;border:1px solid #2a3345;border-radius:6px;margin-bottom:6px;cursor:pointer;align-items:flex-start}}
  .choice:hover{{background:#202635}}
  .choice input{{margin-top:4px}}
  .choice.correct{{border-color:#3a8a4f;background:#1a2a1e}}
  .choice.wrong{{border-color:#aa4141;background:#2a1a1a}}
  textarea{{width:100%;background:#0f1115;color:#e8eaed;border:1px solid #2a3345;border-radius:6px;padding:10px;font-family:inherit;font-size:14px;min-height:80px}}
  .submit{{background:#2d6cdf;border:none;color:#fff;padding:12px 28px;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer;margin-top:10px}}
  .submit:hover{{background:#3578e5}}
  .explain{{background:#12151c;border-left:3px solid #2d6cdf;padding:10px 14px;margin-top:10px;border-radius:4px;font-size:14px;display:none}}
  .explain.show{{display:block}}
  .score{{position:sticky;top:0;background:#0f1115;padding:12px 0;border-bottom:1px solid #1f2430;font-size:15px;z-index:10}}
  .nav{{margin-bottom:16px}}
  ul{{margin:6px 0 0 18px;padding:0}}li{{margin:4px 0}}
</style>
</head>
<body>
<div class="wrap">
  <div class="nav"><a href="{back_href}">← 목차</a></div>
  <h1>{section_title} · 퀴즈</h1>
  <p class="meta">{n_items}문항 · Bloom: {bloom_summary}</p>
  <div class="score" id="score" style="display:none"></div>
  <form id="quiz">
{items_html}
    <button type="button" class="submit" id="submit-btn">제출하고 채점하기</button>
  </form>
  <div id="next-step" style="display:none;margin-top:24px;text-align:center"></div>
</div>
<script>
const ITEMS = {items_json};
const NEXT_HREF = {next_href_json};
const NEXT_TITLE = {next_title_json};
const BACK_HREF = {back_href_json};
const scoreEl = document.getElementById('score');

document.getElementById('submit-btn').onclick = () => {{
  let correct = 0;
  ITEMS.forEach((item, idx) => {{
    const q = document.getElementById('q' + idx);
    const exp = q.querySelector('.explain');
    if (['mcq_single','mcq_multi','true_false'].includes(item.type)) {{
      const picked = [...q.querySelectorAll('input:checked')].map(i => i.value).sort();
      const ans = [...item.correct].sort();
      const ok = JSON.stringify(picked) === JSON.stringify(ans);
      if (ok) correct++;
      q.querySelectorAll('.choice').forEach(c => {{
        const v = c.querySelector('input').value;
        if (ans.includes(v)) c.classList.add('correct');
        else if (picked.includes(v)) c.classList.add('wrong');
      }});
    }}
    exp.classList.add('show');
  }});
  const gradable = ITEMS.filter(i => i.type !== 'short_answer').length;
  scoreEl.style.display = 'block';
  scoreEl.innerHTML = '<strong>' + correct + ' / ' + gradable + '</strong> 맞혔습니다.' +
    (gradable < ITEMS.length ? ' (서술형 ' + (ITEMS.length - gradable) + '문항은 rubric 자가채점)' : '');

  const nextStep = document.getElementById('next-step');
  let html = '';
  if (NEXT_HREF) {{
    html = '<a href="' + NEXT_HREF + '" style="display:inline-block;padding:12px 24px;background:#2d6cdf;color:#fff;border-radius:8px;font-weight:600;text-decoration:none;margin-right:10px">▶ 다음: ' + NEXT_TITLE + '</a>';
  }}
  html += '<a href="' + BACK_HREF + '" style="display:inline-block;padding:12px 24px;background:#222a3a;color:#e8eaed;border:1px solid #2a3345;border-radius:8px;text-decoration:none">목차로</a>';
  nextStep.innerHTML = html;
  nextStep.style.display = 'block';

  window.scrollTo({{top:0, behavior:'smooth'}});
}};
</script>
</body>
</html>
"""


def render_quiz_item_html(item: dict, idx: int) -> str:
    stem = html.escape(item["stem"])
    bloom = html.escape(item.get("bloom", ""))
    itype = item["type"]
    parts = [
        f'<div class="q" id="q{idx}">',
        f'  <span class="tag">Q{idx+1}</span>',
        f'  <span class="tag">{bloom}</span>',
        f'  <span class="tag">{itype}</span>',
        f'  <h3>{stem}</h3>',
    ]
    if itype in ("mcq_single", "mcq_multi"):
        input_type = "radio" if itype == "mcq_single" else "checkbox"
        for i, choice in enumerate(item["choices"]):
            letter = chr(ord("A") + i)
            parts.append(
                f'  <label class="choice"><input type="{input_type}" name="q{idx}" value="{letter}">'
                f'<span><strong>{letter}.</strong> {html.escape(str(choice))}</span></label>'
            )
    elif itype == "true_false":
        for letter, text in [("T", "참 (True)"), ("F", "거짓 (False)")]:
            parts.append(
                f'  <label class="choice"><input type="radio" name="q{idx}" value="{letter}">'
                f'<span>{text}</span></label>'
            )
    elif itype == "short_answer":
        parts.append('  <textarea placeholder="답변을 입력하세요..."></textarea>')

    exp = html.escape(item.get("explanation", ""))
    rubric = item.get("rubric", [])
    rubric_html = ""
    if rubric:
        rubric_html = "<strong>채점 기준:</strong><ul>" + \
            "".join(f"<li>{html.escape(r)}</li>" for r in rubric) + "</ul>"
    dr = item.get("distractor_rationales", {})
    dr_html = ""
    if dr:
        dr_html = "<br><strong>오답 해설:</strong><ul>" + \
            "".join(f"<li><strong>{k}.</strong> {html.escape(v)}</li>" for k, v in dr.items()) + "</ul>"
    correct_txt = ", ".join(item.get("correct", []))
    parts.append(
        f'  <div class="explain">'
        + (f"<strong>정답: {correct_txt}</strong><br>" if correct_txt else "")
        + f'{exp}{dr_html}{rubric_html}</div>'
    )
    parts.append('</div>')
    return "\n".join(parts)


def make_end_actions_html(next_cls_title: str | None,
                          next_cls_href: str | None,
                          is_last_in_section: bool,
                          is_last_in_course: bool,
                          quiz_href: str,
                          back_href: str,
                          lang: str = "ko") -> str:
    t = _tx(lang)
    fallback_title = t["cta_continue"]
    parts = []
    if is_last_in_course:
        # Final class → quiz + back to index
        parts.append(
            f'<a class="btn-cta primary" href="{quiz_href}">'
            f'<span><span class="label">{t["cta_this_section"]}</span>'
            f'<span class="title">📝 {t["cta_final_quiz"]}</span></span></a>'
        )
        parts.append(
            f'<a class="btn-cta secondary" href="{back_href}">'
            f'<span><span class="label">{t["cta_done"]}</span>'
            f'<span class="title">🎉 {t["cta_course_toc"]}</span></span></a>'
        )
    elif is_last_in_section:
        # End of section → quiz is primary, first class of next section is secondary
        parts.append(
            f'<a class="btn-cta primary" href="{quiz_href}">'
            f'<span><span class="label">{t["cta_check_section"]}</span>'
            f'<span class="title">📝 {t["cta_section_quiz"]}</span></span></a>'
        )
        if next_cls_href:
            parts.append(
                f'<a class="btn-cta secondary" href="{next_cls_href}">'
                f'<span><span class="label">{t["cta_next_section"]}</span>'
                f'<span class="title">▶ {html.escape(next_cls_title or fallback_title)}</span></span></a>'
            )
    else:
        # Next class in the same section
        if next_cls_href:
            parts.append(
                f'<a class="btn-cta primary" href="{next_cls_href}">'
                f'<span><span class="label">{t["cta_next_class"]}</span>'
                f'<span class="title">▶ {html.escape(next_cls_title or fallback_title)}</span></span></a>'
            )
        parts.append(
            f'<a class="btn-cta secondary" href="{quiz_href}">'
            f'<span><span class="label">{t["cta_check_first"]}</span>'
            f'<span class="title">📝 {t["cta_section_quiz_short"]}</span></span></a>'
        )
    return "\n    ".join(parts)


def make_toc_html(manifest: dict, current_cls_id: str, current_sec_slug: str,
                  current_cls_slug: str, quiz_counts: dict, lang: str = "ko") -> str:
    """Render sidebar TOC with relative hrefs from current class dir."""
    t = _tx(lang)
    def class_href(sec_slug: str, cls_slug: str) -> str:
        if sec_slug == current_sec_slug:
            return f"../{cls_slug}/player.html"
        return f"../../../{sec_slug}/classes/{cls_slug}/player.html"

    def quiz_href(sec_slug: str) -> str:
        if sec_slug == current_sec_slug:
            return "../../quiz.html"
        return f"../../../{sec_slug}/quiz.html"

    lines = []
    for sec in manifest["sections"]:
        lines.append(f'    <h3>{html.escape(sec["title"])}</h3>')
        lines.append("    <ul>")
        for cls in sec["classes"]:
            cur_cls = "current" if cls["id"] == current_cls_id else ""
            lines.append(
                f'      <li class="{cur_cls}"><a href="{class_href(sec["slug"], cls["slug"])}">'
                f'{html.escape(cls["title"])}</a></li>'
            )
        if quiz_counts.get(sec["id"]):
            quiz_label = t["toc_quiz_tpl"].format(n=quiz_counts[sec["id"]])
            lines.append(
                f'      <li class="quiz"><a href="{quiz_href(sec["slug"])}">'
                f'📝 {quiz_label}</a></li>'
            )
        lines.append("    </ul>")
    return "\n".join(lines) + "\n"


def build_class_player(cls: dict, root: Path, back_href: str, quiz_href: str,
                       next_cls_title: str | None = None,
                       next_cls_href: str | None = None,
                       is_last_in_section: bool = False,
                       is_last_in_course: bool = False,
                       class_number: int = 1,
                       total_classes: int = 1,
                       toc_html: str = "",
                       lang: str = "ko"):
    cls_rel_dir = Path(cls["assets"]["slide_source"]).parent
    cls_dir = root / cls_rel_dir

    transcript_path = cls_dir / "transcript.txt"
    slide_by = parse_transcript_by_slide(transcript_path.read_text(encoding="utf-8")) \
        if transcript_path.exists() else {}

    png_dir = cls_dir / "slides_png"
    pngs = sorted(png_dir.glob("slide.*.png")) if png_dir.exists() else []

    slides = []
    total_dur = 0.0
    for i, png in enumerate(pngs):
        n = i + 1
        mp3_file = cls_dir / "audio" / f"slide_{n:02d}.mp3"
        mp3_rel = f"audio/slide_{n:02d}.mp3" if mp3_file.exists() else ""
        total_dur += mp3_duration(mp3_file)
        slides.append({
            "png": f"slides_png/{png.name}",
            "mp3": mp3_rel,
            "transcript": slide_by.get(n, []),
        })

    duration_min = round(total_dur / 60.0, 1)
    lo_ids = ", ".join(cls.get("lo_ids", []))
    end_actions_html = make_end_actions_html(
        next_cls_title, next_cls_href, is_last_in_section, is_last_in_course,
        quiz_href, back_href, lang=lang,
    )
    course_progress_pct = round(class_number / total_classes * 100, 1)
    t = _tx(lang)
    tx_kwargs = {f"tx_{k}": v for k, v in t.items()}
    html_out = PLAYER_TMPL.format(
        title=html.escape(cls["title"]),
        lo_ids=html.escape(lo_ids),
        slide_count=len(slides),
        duration_min=duration_min,
        back_href=back_href,
        quiz_href=quiz_href,
        slides_json=json.dumps(slides, ensure_ascii=False),
        end_actions_html=end_actions_html,
        class_number=class_number,
        total_classes=total_classes,
        course_progress_pct=course_progress_pct,
        toc_html=toc_html,
        lang=lang,
        **tx_kwargs,
    )
    (cls_dir / "player.html").write_text(html_out, encoding="utf-8")
    return {"slides": len(slides), "duration_min": duration_min, "lo_ids": lo_ids,
            "rel": str(cls_rel_dir)}


def build_section_quiz(sec: dict, root: Path,
                       next_sec_first_class: dict | None = None,
                       next_sec: dict | None = None) -> int:
    quiz_path_rel = sec.get("quiz_path") or f"sections/{sec['slug']}/quiz.json"
    quiz_json_path = root / quiz_path_rel
    if not quiz_json_path.exists():
        return 0
    qdata = json.loads(quiz_json_path.read_text(encoding="utf-8"))
    items = qdata["items"]
    items_html = "\n".join(render_quiz_item_html(it, i) for i, it in enumerate(items))
    bloom = qdata.get("bloom_distribution", {})
    bloom_summary = ", ".join(f"{k}:{v}" for k, v in bloom.items())
    # After-quiz navigation: to next section's first class player
    if next_sec and next_sec_first_class:
        next_href = f"../{next_sec['slug']}/classes/{next_sec_first_class['slug']}/player.html"
        next_title = next_sec_first_class.get("title", "다음 수업")
    else:
        next_href = None
        next_title = None
    out = QUIZ_TMPL.format(
        section_title=html.escape(sec["title"]),
        n_items=len(items),
        bloom_summary=html.escape(bloom_summary),
        back_href="../../index.html",
        items_html=items_html,
        items_json=json.dumps(items, ensure_ascii=False),
        next_href_json=json.dumps(next_href),
        next_title_json=json.dumps(next_title, ensure_ascii=False),
        back_href_json=json.dumps("../../index.html"),
    )
    (quiz_json_path.parent / "quiz.html").write_text(out, encoding="utf-8")
    return len(items)


INDEX_STYLE = """body{font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
max-width:760px;margin:0 auto;padding:24px 20px;background:#0f1115;color:#e8eaed;line-height:1.6}
a{color:#7cb7ff;text-decoration:none}a:hover{text-decoration:underline}
h1{font-size:28px;margin:0 0 8px 0}h2{font-size:18px;margin:32px 0 8px 0;
padding-bottom:6px;border-bottom:1px solid #2a3345}
ul{list-style:none;padding:0;margin:0}li{padding:10px 0;border-bottom:1px solid #1a1f29}
.los{color:#8b95a7;font-size:13px;margin-left:8px}
.quiz-link{color:#3a8a4f;font-weight:500}
.meta{color:#8b95a7;margin-bottom:24px}"""


def audience_to_str(aud) -> str:
    """Coerce audience field (string or dict) into a short display string."""
    if isinstance(aud, str):
        return aud
    if isinstance(aud, dict):
        parts = []
        if aud.get("profile"):
            parts.append(str(aud["profile"]))
        if aud.get("level"):
            parts.append(f"({aud['level']})")
        return " ".join(parts) if parts else json.dumps(aud, ensure_ascii=False)[:80]
    return str(aud)


def build_index(manifest: dict, per_class_info: list, quiz_counts: dict, root: Path):
    topic = manifest["course"]["topic"]
    audience = audience_to_str(manifest["course"].get("audience", ""))
    lines = [
        '<!DOCTYPE html><html lang="ko"><head>',
        '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{html.escape(topic)}</title>',
        f'<style>{INDEX_STYLE}</style>',
        '</head><body>',
        f'<h1>{html.escape(topic)}</h1>',
        f'<p class="meta">{html.escape(audience)} · '
        f'{manifest["course"]["language"]} · '
        f'총 {manifest["stats"]["classes"]}개 class · '
        f'{manifest["stats"]["lo_count"]}개 학습 목표 · '
        f'{manifest["stats"].get("actual_audio_duration_sec", 0)/60:.1f}분</p>',
    ]
    for sec in manifest["sections"]:
        lines.append(f'<h2>{html.escape(sec["title"])}</h2><ul>')
        for cls in sec["classes"]:
            info = next(pc for pc in per_class_info if pc["rel"] == str(Path(cls["assets"]["slide_source"]).parent))
            lines.append(
                f'<li><a href="{info["rel"]}/player.html">🎬 {html.escape(cls["title"])}</a>'
                f'<span class="los">{info["slides"]}장 · {info["duration_min"]}분 · LO {html.escape(info["lo_ids"])}</span></li>'
            )
        if sec["id"] in quiz_counts:
            lines.append(
                f'<li><a href="sections/{sec["slug"]}/quiz.html" class="quiz-link">'
                f'📝 섹션 퀴즈 ({quiz_counts[sec["id"]]}문항)</a></li>'
            )
        lines.append('</ul>')
    lines.append('</body></html>')
    (root / "index.html").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("course_root", type=Path)
    args = ap.parse_args()
    root = args.course_root
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    lang = (manifest.get("course", {}) or {}).get("language", "ko")
    if lang not in _PLAYER_STRINGS:
        lang = "ko"

    per_class_info = []
    quiz_counts = {}

    # Flatten class traversal to compute next-class pointers
    flat = []
    for sec_idx, sec in enumerate(manifest["sections"]):
        for cls_idx, cls in enumerate(sec["classes"]):
            flat.append({
                "sec": sec,
                "sec_idx": sec_idx,
                "cls": cls,
                "cls_idx": cls_idx,
                "is_last_in_section": cls_idx == len(sec["classes"]) - 1,
            })
    for i, entry in enumerate(flat):
        entry["is_last_in_course"] = (i == len(flat) - 1)
        entry["next"] = flat[i + 1] if i + 1 < len(flat) else None

    def path_to_next(entry) -> tuple[str | None, str | None]:
        nxt = entry["next"]
        if not nxt:
            return (None, None)
        # Current class dir: sections/<sec>/classes/<cls>/
        # Next class dir:    sections/<nxt_sec>/classes/<nxt_cls>/
        # Relative from current to next:
        if nxt["sec"]["id"] == entry["sec"]["id"]:
            rel = f"../{nxt['cls']['slug']}/player.html"
        else:
            rel = f"../../../{nxt['sec']['slug']}/classes/{nxt['cls']['slug']}/player.html"
        return (nxt["cls"]["title"], rel)

    # Count quiz items per section first (TOC sidebar needs them)
    for sec in manifest["sections"]:
        qp = root / (sec.get("quiz_path") or f"sections/{sec['slug']}/quiz.json")
        if qp.exists():
            try:
                quiz_counts[sec["id"]] = len(json.loads(qp.read_text(encoding="utf-8")).get("items", []))
            except Exception:
                pass

    total_classes = len(flat)
    for idx, entry in enumerate(flat, start=1):
        nxt_title, nxt_href = path_to_next(entry)
        toc_html = make_toc_html(
            manifest,
            current_cls_id=entry["cls"]["id"],
            current_sec_slug=entry["sec"]["slug"],
            current_cls_slug=entry["cls"]["slug"],
            quiz_counts=quiz_counts,
            lang=lang,
        )
        info = build_class_player(
            entry["cls"], root,
            back_href="../../../index.html",
            quiz_href="../../quiz.html",
            next_cls_title=nxt_title,
            next_cls_href=nxt_href,
            is_last_in_section=entry["is_last_in_section"],
            is_last_in_course=entry["is_last_in_course"],
            class_number=idx,
            total_classes=total_classes,
            toc_html=toc_html,
            lang=lang,
        )
        per_class_info.append(info)

    # Render section quiz HTML
    sections = manifest["sections"]
    for i, sec in enumerate(sections):
        next_sec = sections[i + 1] if i + 1 < len(sections) else None
        next_first = next_sec["classes"][0] if (next_sec and next_sec.get("classes")) else None
        build_section_quiz(sec, root, next_sec_first_class=next_first, next_sec=next_sec)

    build_index(manifest, per_class_info, quiz_counts, root)
    print(f"✓ Generated index.html + {len(per_class_info)} player.html + {len(quiz_counts)} quiz.html")


if __name__ == "__main__":
    main()
