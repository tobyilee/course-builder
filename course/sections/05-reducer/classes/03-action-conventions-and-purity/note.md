# Action 컨벤션과 Reducer 순수성 — 결함 진단

> LOs: LO-S5.3

## 개요
[S5.C2]에서 마이그레이션은 끝났습니다. 그런데 한 달 뒤, 동료가 reducer를 보고 이마를 짚습니다. action.type이 `'taskAdd'`, `'UPDATE_TASK'`, `'remove'` 식으로 제각각이고, 어떤 case는 `fetch`를 호출하며, `tasks.push(...)`로 mutate하는 줄까지 보입니다 [slide 2]. 동작은 어쩌다 맞을 수 있어도 이건 reducer가 아닙니다. 오늘은 "좋은 reducer"를 가르는 두 축 — **action 컨벤션**과 **순수성** — 을 진단 도구로 손에 쥐어 봅시다.

## 핵심 개념

**축 1 — Action 컨벤션** [slide 3, 4]

- **동사 과거형**: `'added'`, `'changed'`, `'deleted'`. action.type은 reducer가 무엇을 할지가 아니라 **사용자가 무엇을 했는가**를 묘사합니다. `'set_tasks'`, `'update_state'` 같은 명령형/구현 누설 이름은 피하세요.
- **케이싱 일관성**: 팀이 `snake_case`든 `camelCase`든 한 가지로 통일합니다. 섞이면 reducer를 읽을 때마다 인지 비용이 새어 나갑니다.
- **한 상호작용 = 한 action**: 폼 리셋을 필드별로 `set_field` × 5번 dispatch하는 안티패턴 대신, 단일 `'reset_form'`으로 모읍니다. 디버그 로그가 의미 단위로 보이고, reducer가 한 번만 돌아 중간 상태가 React에 노출되지 않는 배치 효과도 얻습니다.

action.type 목록은 곧 **앱의 인터랙션 사전**입니다. reducer만 봐도 사용자가 이 화면에서 무엇을 할 수 있는지 보여야 합니다.

**축 2 — Reducer 순수성 3대 규칙** [slide 5]

1. **결정성** — 같은 입력은 같은 출력. `Math.random()`, `Date.now()`처럼 비결정적 호출 금지.
2. **무부수효과** — `fetch`, `setTimeout`, 외부 시스템에 영향을 주는 호출 금지. 그런 일은 핸들러나 `useEffect`로.
3. **불변** — `state.push`, `state.x = ...` 절대 금지. 항상 새 배열/객체를 반환.

왜 이렇게까지 엄격할까요? React는 StrictMode/동시성 모드에서 같은 state로 reducer를 두 번 호출할 수 있고, 그래도 결과가 같아야 합니다. 순수성이 깨지면 그 보장이 무너집니다.

## 예시
결함이 박힌 Tasks reducer를 진단해 봅시다 [slide 6].

```js
// 결함 코드
case 'addTask':                                  // (a) camelCase, 다른 case는 'added'
  tasks.push({ id: Date.now(), text: action.text }); // (b) mutation, (c) 비결정 id
  fetch('/api/log', { method: 'POST' });         // (d) 부수효과
  return tasks;
```

네 가지 결함을 규칙에 매핑합니다.

- (a) 컨벤션 불일치 — 다른 case는 `'added'`인데 혼자 명령형 + camelCase. → `case 'added':`로 통일.
- (b) Mutation — 같은 참조 반환. → `return [...tasks, newTask]`.
- (c) 비결정 id — `Date.now()`는 호출 시각마다 다름. → 핸들러에서 `nextId++`로 만들어 `dispatch({ type: 'added', id, text })`로 실어 보냄.
- (d) 부수효과 — 로깅은 `useEffect`로 옮기거나 핸들러에서 처리.

```js
// 수정안
case 'added':
  return [...tasks, { id: action.id, text: action.text, done: false }];
```

규칙이 진단 도구가 되면 코드 리뷰가 빨라집니다. "이 case 어느 규칙 위반?"이 공통 어휘가 되니까요.

## 흔한 실수
- **reducer 안의 `console.log` 자체도 위험**: 디버깅용이라면 괜찮지만, 그 로그가 "결정적 결과"를 좌우하는 분기에 쓰이면 부수효과 규칙을 어깁니다. 로그는 관찰만, 분기는 인자에서.
- **payload 래퍼 강박**: `action.payload.id`로 한 겹 더 감싸는 스타일은 취향 차이입니다. 평탄하게 `action.id`로 두어도 충분 — 일관성만 지키세요.

## 복습
Action은 동사 과거형, 한 상호작용 = 한 action, 케이싱 일관. Reducer는 결정적·무부수효과·불변. 셋 다 지켜야 진짜 reducer입니다. 다음 시간 [S5.C4]에서는 useState와 useReducer를 4축으로 비교하고, mutation 스타일을 가능케 하는 Immer 옵션을 봅니다.
