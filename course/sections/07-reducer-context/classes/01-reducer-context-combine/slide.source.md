---
marp: true
theme: default
paginate: true
footer: "LO-S7.1"
---

<!-- beat: b1 -->

# Reducer + Context로 prop drilling 끝내기

## 두 context 분리 전략

- useReducer만 쓰면 **state·dispatch가 최상위에만**
- 중간 컴포넌트가 안 쓰는 props까지 4단계 내려보내는 지옥
- 오늘 목표: state context와 dispatch context 두 개로 쪼개기

---

<!-- beat: b2 -->
<!-- _footer: "LO-S7.1" -->

## 왜 두 개로 나누나?

- 하나로 묶으면 **dispatch만 쓰는 컴포넌트도** state 변경 때마다 재렌더
- `TasksContext` (값) / `TasksDispatchContext` (함수) — 관심사 + 재렌더 분리
- dispatch는 동일 참조 유지 → dispatch context는 안정적
- S5(reducer) + S6(context) 지식이 합쳐지는 지점

---

<!-- beat: b3 -->
<!-- _footer: "LO-S7.1" -->

## 3단계 빌드 로드맵

1. **createContext × 2** — 값/디스패처용 context 두 개 생성
2. **Provider 안에서 useReducer** — state와 dispatch 만들고 두 Provider로 감싸기
3. **useContext × 2** — 자식이 필요한 것만 골라 read/dispatch

> 다음 클래스(C2)에서 이 wiring을 Provider + 커스텀 훅으로 응집시킴

---

<!-- beat: b4 -->
<!-- _footer: "LO-S7.1" -->

## Step 1 — 두 context 생성

```js
// TasksContext.js
import { createContext } from 'react';

export const TasksContext = createContext(null);
export const TasksDispatchContext = createContext(null);
```

- 초기값 `null`: Provider 밖에서 사용 시 의도치 않은 동작 방지
- 이름 컨벤션: 값은 도메인 그대로, 디스패처는 `…DispatchContext`

---

<!-- beat: b5 -->
<!-- _footer: "LO-S7.1" -->

## Step 2 — Provider 트리 구성

```jsx
function TaskApp() {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
  return (
    <TasksContext value={tasks}>
      <TasksDispatchContext value={dispatch}>
        <AddTask />
        <TaskList />
      </TasksDispatchContext>
    </TasksContext>
  );
}
```

- React 19+ 단축 문법 (`.Provider` 생략)

---

<!-- beat: b6 -->
<!-- _footer: "LO-S7.1" -->

## Step 3 — 자식에서 useContext

```js
// AddTask — dispatch만 구독
const dispatch = useContext(TasksDispatchContext);
dispatch({ type: 'added', id: nextId++, text });

// TaskList — tasks만 구독
const tasks = useContext(TasksContext);
```

- 필요한 것만 구독 → 재렌더 범위 최소화
- `onAddTask`, `onChangeTask`, `onDeleteTask` 콜백 전부 사라짐

---

<!-- beat: b7 -->
<!-- _footer: "LO-S7.1" -->

## 자문자답 — 스스로 그려 보기

- `{ tasks, dispatch }`를 한 객체로 묶어 단일 context에 넣었다면?
  - 힌트: dispatch만 쓰는 AddTask는 어떻게 될까
- `createContext(null)`의 초기값 `null`은 언제 쓰일까?
  - Provider 밖에서 useContext 호출 시

---

<!-- beat: b8 -->
<!-- _footer: "LO-S7.1" -->

## Recap & 다음 시간 예고

- reducer + context = 분산된 자식이 직접 read/dispatch
- **state / dispatch context 분리** = 재렌더 분리 + 관심사 분리
- 3단계: createContext × 2 → Provider + useReducer → useContext × 2

> 다음 시간: TasksProvider + 커스텀 훅으로 응집
