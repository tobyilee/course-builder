---
name: slide-authoring
description: Author slide decks in Marp Markdown and render to HTML. Use when turning class beats into 4-7 slides per class, applying Marp frontmatter/layout rules, preventing overflow, or rendering via the marp CLI. Triggered by the slide-author agent.
---

# Slide Authoring — Marp Markdown

slide는 Marp Markdown으로 작성한 뒤 `marp` CLI로 HTML 렌더한다. AI가 raw HTML을 직접 쓰면 레이아웃이 깨지기 쉬우므로 **반드시 Marp MD 경유**.

## Marp 프론트매터 표준

```markdown
---
marp: true
theme: default
paginate: true
footer: "LO-X.Y"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  code { font-size: 22px; }
---
```

- `paginate: true` — 우하단 페이지 번호
- `footer`는 class의 주 LO id. 슬라이드마다 다른 LO면 슬라이드 안에 `<!-- _footer: "LO-X.Z" -->` 오버라이드

## 슬라이드 개수
- class당 **4~7장** 고정
- 공식: `beats` 개수 + 1 (제목 슬라이드) + (마무리/recap 1)

## 슬라이드 레이아웃 규칙 (택1)

각 슬라이드는 다음 3가지 중 **정확히 하나**만 담는다:

### A. Bullet 슬라이드 (3~5 bullet)
```markdown
## 서버 컴포넌트란

- 서버에서 렌더링되는 React 컴포넌트
- 클라이언트 번들에 포함되지 않음
- DB/파일시스템 직접 접근 가능
- Suspense 경계로 스트리밍됨
```

### B. Code 슬라이드 (≤15줄)
```markdown
## RSC 예시

~~~jsx
// app/posts/page.js
export default async function Page() {
  const posts = await db.query(...);
  return posts.map(p => <Post {...p} />);
}
~~~
```

### C. Diagram 슬라이드 (그림/다이어그램)
Mermaid 내장 가능 (default theme 지원):
```markdown
## 요청 흐름

~~~mermaid
flowchart LR
  Browser --> Edge --> Server --> DB
~~~
```

## 제목 규칙
- h2 (`##`) 사용, h1은 제목 슬라이드에만
- ≤10 단어, 조사 제외
- 질문형/선언형 섞어서 리듬감 (`무엇이 RSC인가` → `RSC는 어디에 쓰는가` → `RSC 예시`)

## Overflow 방지
- 텍스트 총량 ≤80 단어/슬라이드 (ko 기준 160자)
- 코드 ≤15줄, 초과 시 분할 + `(이어서)` 서브타이틀
- 이미지 문법 **정확히 준수**할 것 — Marp 는 alt + dimension 을 space-separated로만 인식한다:
  - `![alt text](url)` — alt 만
  - `![w:600](url)` — dimension 만 (w:NUMBER, h:NUMBER — px 단위 없이 숫자만)
  - `![alt text w:600](url)` — alt + dimension (dimension 은 **항상 마지막**, space-separated)
  - **금지**: `![w:600 alt:"..."](url)` — `alt:` prefix 는 Marp가 인식 못해 통째로 plain text 로 렌더됨 (과거 실전 사고)
  - **금지**: `![width:600px ...](url)` — `width:` 가 아니라 `w:`, 단위는 생략
- **`data:` URI 사용 금지** — Marp 는 보안 정책상 `data:image/...` URL 을 모든 형식(`utf8,`·`base64,`)에서 통째로 거부한다 (verified with marp-cli v4.3.1: `![x](data:image/svg+xml;base64,...)` → `<img>` 태그 생성 안 됨, 원본 markdown 이 `<p>` 로 래핑되어 슬라이드에 raw text 노출). 인라인 다이어그램이 필요하면 SVG/PNG 를 `slides_png/diag-NN.svg` 같은 **실제 파일로 저장**하고 상대경로로 참조할 것:
  ```markdown
  ![다이어그램 설명 w:720](slides_png/diag-01.svg)
  ```
  Marp 는 `--allow-local-files` 플래그(build-bundle.sh 에 이미 포함)로 로컬 파일 SVG 를 PNG 렌더 시 인라인화한다.

## LO footer 표시
- 기본은 프론트매터 `footer`
- 슬라이드별 오버라이드:
  ```markdown
  <!-- _footer: "LO-1.2" -->
  ## 이 슬라이드의 제목
  ```

## Beat 태깅 (TTS affect 정확도용)
각 슬라이드에 **어떤 beat에서 유도됐는지** 표기하면 `synthesize-tts.py` 가 per-slide `speaker_affect` 오버레이를 정확히 매핑한다 (없으면 proportional-stretch 휴리스틱으로 fallback).

```markdown
---

<!-- beat: b2 -->
<!-- _footer: "LO-1.1" -->

## 슬라이드 제목
```

- `<!-- beat: bN -->` 는 plain HTML comment — Marp directive 아니라 render 영향 없음
- 값은 `_workspace/03_class_<id>_beats.json` 의 beat `id` (예: `b1`, `b2`) 그대로
- 한 beat이 여러 슬라이드를 커버하면 동일 id 반복 태깅
- 주석 생략 시 해당 슬라이드는 neutral affect 처리

## 파일 구조

```
course/sections/<sec-slug>/classes/<class-slug>/
├── slide.source.md   ← Marp 원본 (편집 대상)
└── slide.html        ← 렌더 결과 (generated, 편집 금지)
```

## 렌더 스크립트 사용
`scripts/render-marp.sh`를 호출:
```bash
bash .claude/skills/slide-authoring/scripts/render-marp.sh \
  course/sections/01-intro/classes/01-what-is-rsc
```

이 스크립트는:
1. `slide.source.md` 존재 확인
2. `marp` CLI 호출 (`--html --allow-local-files`)
3. 렌더 에러 시 stderr 캡처하여 반환 (비영점 exit)

## 에러 대응

### Marp 미설치
에러 시 사용자에게 안내: `npm install -g @marp-team/marp-cli`

### 오버플로우 감지
Marp는 런타임에 overflow 감지 불가. 대신:
- 사전 규칙 (≤80 단어, ≤15줄) 자가검사
- 렌더 후 `slide.html` 각 `section`의 텍스트 길이 측정 스크립트로 post-check

## 톤 반영
`tone=friendly`: 제목에 감탄형·질문형 혼용, bullet은 친근한 어미
`tone=formal`: 명사형 종결, 객관적 어휘
`tone=socratic`: 제목을 질문으로, bullet은 추론 유도

## 재실행 규칙
- slide 순서/개수 변경 시 script-writer에 `[slide N]` cue 재매핑 필요함을 coherence-reviewer가 감지
- 부분 수정이면 해당 슬라이드만 교체
