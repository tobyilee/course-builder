# 3단계 마이그레이션 — useState에서 useReducer로

> LOs: LO-S5.2

## 개요
지난 시간 [S5.C1]에서 `useReducer`의 시그니처는 외웠지만, 막상 `setTasks`가 네 군데 흩어진 기존 컴포넌트를 펼쳐 놓으면 "어디부터 손대지?" 하고 멈칫하게 됩니다. 오늘은 프라하 Tasks 앱을 함께 라이브 리팩터링하면서, 겁먹을 필요 없는 **기계적인 3단계 변환**을 손에 익혀 봅시다 [slide 2]. 이 절차가 끝나면 어떤 컴포넌트든 동일한 리듬으로 reducer로 옮길 수 있습니다.

## 핵심 개념
3단계 로드맵은 다음과 같습니다 [slide 3].

- **Step 1 — `setTasks(...)` → `dispatch({ type, ...payload })`**: 핸들러 안의 setState 호출을 dispatch로 바꿉니다. 이때 우리가 정하는 것은 "이 사건의 이름이 무엇인가" — 즉 **action 어휘**입니다.
- **Step 2 — `tasksReducer` 함수를 컴포넌트 밖에 작성**: `switch (action.type)`로 분기해 각 case가 새 배열/객체를 반환하게 합니다.
- **Step 3 — `useState`를 `useReducer`로 한 줄 교체**: `import` 한 줄과 훅 호출 한 줄만 바꿉니다.

순서가 중요한 이유: Step 1이 action 어휘를 먼저 확정해야 Step 2의 reducer가 그 어휘로 분기할 수 있습니다. 어휘 → 구현, 그 다음 연결입니다 [slide 3].

## 예시

**Step 1 — 핸들러를 dispatch로 변환** [slide 4]

```js
function handleAddTask(text) {
  dispatch({ type: 'added', id: nextId++, text });
}
function handleChangeTask(task) {
  dispatch({ type: 'changed', task });
}
function handleDeleteTask(taskId) {
  dispatch({ type: 'deleted', id: taskId });
}
```

이 시점에서 코드는 일시적으로 깨집니다 — reducer가 아직 없으니까요. 정상입니다. 우리는 먼저 어휘만 확정한 것입니다.

**Step 2 — reducer 작성** [slide 5]

```js
function tasksReducer(tasks, action) {
  switch (action.type) {
    case 'added':
      return [...tasks, { id: action.id, text: action.text, done: false }];
    case 'changed':
      return tasks.map(t => t.id === action.task.id ? action.task : t);
    case 'deleted':
      return tasks.filter(t => t.id !== action.id);
    default:
      throw Error('Unknown action: ' + action.type);
  }
}
```

핵심 두 가지: 절대 `tasks`를 mutate하지 않고 항상 새 배열을 반환할 것, 그리고 `default`에 `throw`를 두어 오타가 나면 즉시 폭발하게 할 것. 컴포넌트 외부 함수이므로 props/state 클로저에 의존할 수 없고, 오직 인자 두 개로만 다음 state를 만듭니다.

**Step 3 — 한 줄 교체** [slide 6]

```js
import { useReducer } from 'react';
const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
```

나머지 컴포넌트 코드 — `tasks`를 읽거나 자식에 props로 넘기는 부분 — 는 단 한 줄도 바꿀 필요가 없습니다. 저장하고 새로고침했을 때 UI 동작이 이전과 100% 같으면 성공입니다. 다르다면 어디선가 mutation이 새어들었다는 신호입니다.

## 흔한 실수
- **reducer 안에서 mutation**: `case 'added': tasks.push(newTask); return tasks;` — 같은 참조를 반환하면 React가 변화를 감지하지 못해 리렌더가 누락되거나 들쑥날쑥해집니다. 항상 `[...tasks, ...]` 또는 `tasks.map/filter`로 새 참조를 만드세요.
- **한 action에 여러 사건 묶기**: `dispatch({ type: 'added_and_selected', ... })`처럼 두 사건을 한 type에 묶으면 reducer 분기가 비대해지고 디버그 로그도 의미를 잃습니다. 한 사용자 행동 = 한 action을 지키세요 — 자세한 진단은 [S5.C3]에서 다룹니다.

## 복습
3단계: dispatch로 변환 → reducer 작성 → 훅 한 줄 교체. 동작이 같지 않다면 mutation을 의심하세요. 다음 시간 [S5.C3]에서는 action 어휘를 어떻게 잘 짓는지, 그리고 reducer 순수성이 깨진 코드를 어떻게 진단하는지 봅니다.
