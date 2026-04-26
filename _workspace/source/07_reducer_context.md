# Source: Scaling Up with Reducer and Context

## 동기
useReducer만 쓰면 state/dispatch가 최상위에만 있어 중간 컴포넌트들이 prop drilling으로 받아 내려야 함. → context와 결합해서 어디서나 read/dispatch 가능하게.

## 3단계

### 1. 두 context 생성
```js
// TasksContext.js
import { createContext } from 'react';
export const TasksContext = createContext(null);
export const TasksDispatchContext = createContext(null);
```
state와 dispatch를 **분리**하는 이유: dispatch만 필요한 컴포넌트가 state 변경에 의해 재렌더되지 않도록 (성능/재렌더 분리).

### 2. Provider 트리 구성
```js
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

### 3. 자식에서 useContext로 read/dispatch
```js
// AddTask
const dispatch = useContext(TasksDispatchContext);
dispatch({ type: 'added', id: nextId++, text });

// TaskList
const tasks = useContext(TasksContext);
```

## 응집된 단일 파일 패턴
모든 wiring을 `TasksContext.js` 한 파일로:
```js
import { createContext, useContext, useReducer } from 'react';

const TasksContext = createContext(null);
const TasksDispatchContext = createContext(null);

export function TasksProvider({ children }) {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
  return (
    <TasksContext value={tasks}>
      <TasksDispatchContext value={dispatch}>
        {children}
      </TasksDispatchContext>
    </TasksContext>
  );
}

export function useTasks() { return useContext(TasksContext); }
export function useTasksDispatch() { return useContext(TasksDispatchContext); }

function tasksReducer(tasks, action) { /* ... */ }
const initialTasks = [/* ... */];
```

`App.js`는 깔끔하게:
```js
function TaskApp() {
  return (
    <TasksProvider>
      <AddTask />
      <TaskList />
    </TasksProvider>
  );
}
```

자식 컴포넌트:
```js
const tasks = useTasks();
const dispatch = useTasksDispatch();
```

## 커스텀 훅 패턴
`use…` 로 시작하는 함수는 React에서 Custom Hook으로 인식. 내부에서 다른 훅(useContext 등)을 호출 가능. 장점:
- 더 깔끔한 의미론적 API
- 추후 로직 추가(예: 셀렉터, devtools) 시 소비자 코드 변경 없음
- 타입스크립트와 결합해 강타입화 쉬움

## Provider 컴포넌트 패턴
```js
function TasksProvider({ children }) {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
  return (
    <TasksContext value={tasks}>
      <TasksDispatchContext value={dispatch}>
        {children}
      </TasksDispatchContext>
    </TasksContext>
  );
}
```
- 모든 state 관리 로직을 캡슐화
- children prop으로 어떤 JSX든 감쌀 수 있음
- 사용처는 UI에만 집중

## 다중 도메인 확장
한 앱에 `TasksProvider`, `AuthProvider`, `ThemeProvider` … 여러 reducer+context 쌍을 두는 게 일반적. 각각 독립적이라 prop drilling 없이 도메인별 분리 유지.

## Recap
- reducer + context = 분산된 컴포넌트가 직접 read/dispatch
- 3단계: context 두 개 → Provider 안에서 useReducer → 자식에서 useContext
- `TasksProvider` + 커스텀 훅 `useTasks`/`useTasksDispatch`로 응집
- 도메인별 reducer/context를 여러 개 두면 대규모 앱도 깔끔
