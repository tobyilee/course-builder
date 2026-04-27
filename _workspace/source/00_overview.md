# Source: react.dev/learn/escape-hatches — Chapter Overview

## Framing
"Escape Hatches" — React의 일반 흐름(선언형 / 순수 렌더 / 단방향 props) 을 **벗어나** 외부 시스템과 동기화해야 할 때 쓰는 도구들. 대부분의 앱 로직은 이 챕터의 기능에 의존해서는 안 된다. 이들은 **마지막 수단** 이다 — 브라우저 API, 비-React 컴포넌트, 원격 서버 같은 React가 통제하지 못하는 시스템과 연결해야 할 때만 쓴다.

## 8-chapter structure (sub-pages)

| # | Slug | 한국어 제목 | 핵심 |
|---|---|---|---|
| 1 | referencing-values-with-refs | Ref로 값 참조하기 | useRef. 재렌더 트리거 없이 값을 "기억". timeout/interval ID, 비-렌더 데이터 보관. state vs ref 비교. |
| 2 | manipulating-the-dom-with-refs | Ref로 DOM 조작하기 | ref={myRef} 패턴. focus/scroll/measure/play. flushSync로 동기 DOM 업데이트. forwardRef + useImperativeHandle로 노출 통제. |
| 3 | synchronizing-with-effects | Effect로 동기화하기 | useEffect = "외부 시스템과의 동기화" (라이프사이클 X). 의존성 배열, cleanup, Strict Mode 더블 호출. |
| 4 | you-might-not-need-an-effect | Effect 안 써도 되는 경우 | 12가지 안티패턴: derived state, 캐싱, 리셋, 핸들러로 옮길 로직, chains, fetching race condition, useSyncExternalStore. |
| 5 | lifecycle-of-reactive-effects | 반응형 Effect의 라이프사이클 | Effect는 "동기화 시작/중지" 사이클. reactive vs non-reactive 값. ESLint exhaustive-deps. roomId 채팅 재연결 예. |
| 6 | separating-events-from-effects | Event vs Effect 분리 | useEffectEvent (실험적). non-reactive 로직을 Effect 안에서 추출. theme 변경 시 채팅 재연결 방지. |
| 7 | removing-effect-dependencies | Effect 의존성 줄이기 | 6가지 전략: 정적 값을 컴포넌트 밖으로, 객체/함수를 Effect 안으로, updater 함수, useEffectEvent, Effect 분리, 원시값 추출. |
| 8 | reusing-logic-with-custom-hooks | Custom Hook으로 로직 재사용 | "use" 접두사. stateful 로직 공유 (state는 공유 X — 각 호출 독립). useOnlineStatus, useChatRoom, useFormInput. composition. |

## 핵심 take-aways
- **Ref ≠ State**: ref는 재렌더 트리거 없이 값을 보관 (timeout ID 같은 비-렌더 데이터). 렌더 중 ref.current 읽기/쓰기 금지.
- **DOM ref**: focus/scroll/measure/play 같은 React가 대체 못 하는 작업에만. React가 관리하는 DOM은 직접 조작 금지.
- **Effect = 외부 시스템 동기화**: 라이프사이클 훅이 아님. Effect는 "**시작/중지**"의 관점으로 생각.
- **You Might Not Need an Effect**: derived value는 render 중 계산. 이벤트로 발생한 일은 핸들러에. 부모 통지/연결 체인 모두 안티패턴.
- **반응형 라이프사이클**: 각 render는 자신만의 Effect closure. 의존성 배열은 React가 비교(Object.is)해 재동기화 결정.
- **Events vs Effects**: useEffectEvent로 non-reactive 부분 추출 → 불필요한 재연결 방지.
- **Removing deps**: linter 절대 무시 금지. 코드를 바꿔서 의존성을 자연스럽게 줄여라.
- **Custom Hooks**: stateful 로직 재사용 (state 공유 X). use 접두사 + 다른 Hook 호출 시에만. 단일 사용처에는 추출 금지.
