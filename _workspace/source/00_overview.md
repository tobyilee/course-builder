# Source: react.dev/learn/managing-state — Chapter Overview

## Framing
React 상태 관리 챕터는 **앱이 커질수록 의도적인 state 조직과 데이터 흐름이 중요해진다**는 문제 의식에서 출발한다. 중복/모순 state, 동기화 누락, prop drilling 같은 흔한 결함을 패턴으로 해결한다.

## 7-chapter structure (sub-pages)

| # | Slug | 한국어 제목 | 핵심 |
|---|---|---|---|
| 1 | reacting-to-input-with-state | 입력에 state로 반응하기 | 명령형(imperative) vs 선언형(declarative). 시각적 상태 열거 → 트리거 식별 → state 모델링 → 비핵심 state 제거 → 핸들러 연결. |
| 2 | choosing-the-state-structure | state 구조 선택 | 관련 state 묶기 / 모순 회피 / 중복(redundant) 제거 / duplication 제거 / 깊은 중첩 평탄화. |
| 3 | sharing-state-between-components | 컴포넌트 간 state 공유 | lifting state up. controlled vs uncontrolled. single source of truth. |
| 4 | preserving-and-resetting-state | state 보존과 리셋 | state는 트리 위치에 묶인다. 같은 위치 같은 컴포넌트 = 보존. 다른 위치/타입/key = 리셋. nested component definition 금지. |
| 5 | extracting-state-logic-into-a-reducer | reducer로 state 로직 추출 | useReducer 시그니처. dispatch action. action.type 컨벤션. reducer purity. useState↔useReducer 트레이드오프. Immer 옵션. |
| 6 | passing-data-deeply-with-context | context로 깊이 데이터 전달 | createContext / useContext / Provider. prop drilling 대안. context 남용 회피(컴포지션 우선). |
| 7 | scaling-up-with-reducer-and-context | reducer + context 조합 | 두 context(state/dispatch) 분리. 단일 파일 응집(Provider + 커스텀 훅 useTasks/useTasksDispatch). 대규모 앱 패턴. |

## 핵심 take-aways
- State-driven UI: DOM 직접 조작 대신 "상태 → UI 자동 반영"
- Redundant state 제거 = 동기화 버그 원천 차단
- Lifting up = 형제 컴포넌트 협조의 정석
- `key` prop = state 리셋의 유일한 직관적 수단
- useReducer = 복잡한 상태 전이 로직 분리·테스트
- Context = prop drilling 해소, 단 남용 주의
- Reducer + Context = 대규모 분산 상태 패턴
