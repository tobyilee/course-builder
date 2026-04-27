# React Escape Hatches 심화 — Refs · Effects · Custom Hooks

> **선언형 React의 안전지대 밖에서, React의 규칙을 의도적으로 벗어나는 도구를 정확히 이해하고 다루는 중급-중상급 코스.**
> `react.dev/learn/escape-hatches` 8개 sub-chapter를 깊이 있게 재구성한 약 6시간 분량의 한국어 강의.

---

## 누구를 위한 강의인가

다음을 이미 알고 계신 분에게 가장 큰 효과가 있습니다.

- TypeScript / JavaScript / React 함수형 컴포넌트 개발에 능숙하다.
- `useState`, `useReducer`, props/state lifting, `key` prop, Context 같은 **상태 관리 도구를 자유롭게** 쓴다 (전작 [Managing State 코스](../course-builder-47m.pages.dev) 수준).
- 다만 다음 영역에서는 "어떨 때 써야 옳고, 어떨 때 쓰지 않는 게 옳은가"가 흔들린다:
  - `useRef` — 값 보관 / DOM 조작 / `flushSync` / `forwardRef` / `useImperativeHandle`
  - `useEffect` — 동기화 모델 / cleanup / Strict Mode 더블 호출 / 12가지 안티패턴
  - 반응형 라이프사이클 — reactive vs non-reactive / `Object.is` 비교 / `exhaustive-deps`
  - `useEffectEvent` (실험적) — non-reactive 로직 추출
  - Custom Hook — 추출 시점 / `state` 공유는 안 된다는 핵심 / composition

이 코스는 API 설명을 넘어 **"왜 이 도구를 쓰지 않는 게 기본인가"**, **"쓸 때의 의사결정 기준"**, **"잘못 썼을 때의 리스크"** 같은 **판단 레벨**을 다룹니다.

## 핵심 메시지

> **Escape hatch는 마지막 수단이다.**
>
> React는 "선언형 + 순수 렌더 + 단방향 데이터 흐름"이라는 안전지대를 제공합니다. `useRef`/`useEffect`/`useEffectEvent`/Custom Hook 같은 도구는 그 안전지대를 의도적으로 **벗어나** 외부 시스템과 동기화해야 할 때만 정당화됩니다. 이 코스는 그 경계선을 또렷하게 긋는 데 모든 시간을 씁니다.

## 무엇을 배우는가 (10개 섹션, 31개 클래스, 약 360분)

| # | 섹션 | 핵심 질문 | 시간 |
|---|---|---|---|
| **S0** | 오리엔테이션 — Escape Hatch 멘탈모델 | 왜 이 챕터들이 한 묶음인가? "기본은 안 쓰는 것"인 이유는? | 20m |
| **S1** | Ref로 값 참조하기 | state는 언제, ref는 언제? 렌더 중 `ref.current` 읽기는 왜 금지인가? | 30m |
| **S2** | Ref로 DOM 조작하기 | focus·scroll·measure는 왜 ref인가? React 19의 `ref-as-prop`은 무엇이 달라졌나? | 35m |
| **S3** | Effect로 동기화하기 | Effect는 라이프사이클이 아니다. Strict Mode 더블 호출은 왜 의도된 것인가? | 40m |
| **S4** | Effect 안 써도 되는 경우 — 12 안티패턴 | 가장 중요한 섹션. derived state, fetch race, 앱 init… 12가지를 진단한다. | 55m |
| **S5** | 반응형 Effect의 라이프사이클 | reactive vs non-reactive 분류, `Object.is` 비교, `exhaustive-deps` 3가지 해법. | 40m |
| **S6** | Event vs Effect 분리 — `useEffectEvent` | "왜 실행되어야 하는가?"라는 결정 질문, 실험적 API의 한계. | 35m |
| **S7** | Effect 의존성 줄이기 — 6 전략 | linter suppress 금지. 6가지 전략 매핑표로 의사결정. | 45m |
| **S8** | Custom Hook으로 로직 재사용 | `use` 접두사 규칙. **state 공유는 안 된다**는 핵심 오해 풀기. | 35m |
| **S9** | 종합 — 안티패턴 진단 + 통합 케이스 스터디 | 안티패턴 6개 진단 클리닉 → 검색 채팅방 앱 빌드 + PR 리뷰 톤 정당화. | 25m |

총 **45개 학습 목표**(LO), **72개 퀴즈 문항**, **6단계 Bloom Taxonomy 중 5단계 커버**(Understand/Apply/Analyze/Evaluate/Create — Remember는 의도적 생략).

## 학습 흐름

각 클래스는 다음 5부 구조로 동일하게 구성됩니다.

1. **Hook** — 한 컷의 문제 상황. "왜 이게 중요한가"
2. **Teach** — 핵심 개념을 코드와 함께
3. **Example** — 실제 코드 Before/After
4. **Practice** — 자문자답형 미니 연습
5. **Recap** — 다음 클래스로의 다리

각 클래스마다 **슬라이드 (HTML + PNG)**, **노트 (Markdown 학습 자료)**, **TTS 음성 트랜스크립트**, 섹션 끝에는 **퀴즈 5–9문항**이 제공됩니다.

## 추천 학습 순서

처음 보는 분이라면 **S0 → S1 → S3 → S5 → S6 → S7 → S2 → S4 → S8 → S9** 순서가 의외로 좋습니다(Effect 라인을 먼저 끝내고 ref/안티패턴/Custom Hook으로). 다만 코스의 기본 순서(S0 → S9)는 의존성 순으로 안전한 길이고, 시간이 짧다면 **S0, S4, S5, S7만 골라 들어도** 의사결정 능력의 80%를 얻을 수 있습니다.

## 사전 코스

이 코스는 [**React 상태 관리 심화 (Managing State)**](../course-builder-47m.pages.dev) 직후를 가정합니다. 사전 코스에서 다룬 다음 도구들은 **다시 설명하지 않습니다** — 필요하면 노트에서 `[managing-state S?.C?]`로 짧게 참조합니다.

- `useState` 기본
- state shape 설계 5원칙
- Lifting State Up
- `key` prop으로 state 리셋
- `useReducer`
- Context, Reducer + Context 결합

## 학습 결과

코스를 마치면 다음을 할 수 있게 됩니다.

- 임의의 React 코드를 보고 **어느 도구가 적절한가/잘못 쓰였나**를 30초 안에 진단한다.
- Effect의 의존성 경고가 나왔을 때 **suppress 대신 6가지 전략 중 어느 것**으로 풀지 선택한다.
- Custom Hook 추출 결정을 **단일 사용처 / lifecycle wrapper / Hook 호출 없는 함수** 같은 안티패턴과 구분해 정당화한다.
- 작은 통합 앱(예: 검색 가능한 채팅방)을 처음부터 끝까지 코스의 결정 트리대로 빌드하고, 모든 escape hatch 사용처에 PR 코멘트로 정당화 한 줄을 붙인다.

## 강의 사양

- **언어**: 한국어 (코드 주석·기술 용어는 원어 보존)
- **톤**: 친근하지만 기술적으로 정밀
- **음성**: OpenAI gpt-4o-mini-tts (voice=nova, speed=1.3x)
- **포맷**: HTML 슬라이드 + PNG + MP3 + Markdown 노트 + 인터랙티브 퀴즈 HTML
- **재생기**: 자체 SPA 플레이어 (TOC, 자막 동기, 재생 속도 조절, 이전 위치 이어듣기)

## 시작하기

```bash
# 로컬 미리보기
open course/index.html

# 또는 Cloudflare Pages 배포
bash scripts/deploy-cloudflare.sh escape-hatches
```

좋은 학습 되시길 바랍니다.
