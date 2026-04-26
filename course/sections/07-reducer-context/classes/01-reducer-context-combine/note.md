# Reducer와 Context를 결합하기 — 두 context 분리 전략

> LOs: LO-S7.1

## 개요

`useReducer`만 단독으로 쓰면 `tasks`와 `dispatch`는 최상위 컴포넌트(예: `TaskApp`)에만 존재합니다. 그래서 깊이 박힌 버튼 하나가 `dispatch`를 부르려면 `TaskApp → TaskList → Task → 버튼`처럼 4단계에 걸쳐 prop을 내려보내야 하죠. 자기는 쓰지도 않으면서 그저 통과시키기만 하는 컴포넌트가 늘어나는, 이른바 **prop drilling 지옥**입니다 [slide 1]. 이번 시간에는 **state context와 dispatch context를 두 개로 쪼개** 어디서나 직접 read·dispatch 하도록 만드는 전략을 익힙니다. S5의 reducer와 S6의 context가 마침내 합류하는 지점입니다 [S5.C1, S6.C1].

## 핵심 개념

여기서 가장 중요한 결정은 **왜 context를 하나가 아니라 둘로 나누는가** 입니다 [slide 2].

- **재렌더 분리**: `{ tasks, dispatch }`를 한 객체로 묶어 단일 context에 넣으면, `tasks`가 바뀔 때마다 그 context를 구독하는 모든 자식이 재렌더됩니다. `dispatch`만 호출하는 `AddTask` 같은 컴포넌트도 덩달아 다시 그려지죠.
- **관심사 분리**: 값(state)과 명령(action 보내는 통로)은 의미가 다릅니다. 분리하면 "이 컴포넌트는 읽기만 하나, 쓰기만 하나, 둘 다인가"가 코드만 봐도 드러납니다.
- **dispatch는 본래 안정적**: `useReducer`가 돌려주는 `dispatch`는 컴포넌트 생애주기 동안 동일 참조를 유지합니다. 따라서 `TasksDispatchContext`의 value는 사실상 변하지 않고, dispatch만 구독하는 자식은 거의 재렌더되지 않습니다.

빌드는 **3단계**로 진행합니다 [slide 3]: ① `createContext`로 두 개의 context를 만들고 ② `Provider` 안에서 `useReducer`를 호출해 두 value를 흘려보내고 ③ 자식에서 `useContext`로 필요한 쪽만 구독합니다.

## 예시

**Step 1 — context 두 개 생성** [slide 4]. 초기값을 `null`로 두는 건 Provider 밖에서 실수로 소비될 때 빠르게 드러내기 위한 관습입니다.

```js
// TasksContext.js
export const TasksContext = createContext(null);
export const TasksDispatchContext = createContext(null);
```

**Step 2 — Provider 안에서 useReducer** [slide 5]. React 19+의 Provider 단축 문법(`.Provider` 생략)을 그대로 씁니다.

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

**Step 3 — 자식에서 useContext로 필요한 것만 구독** [slide 6]. 기존에 props로 줄줄이 내려보내던 `onAddTask`, `onChangeTask`, `onDeleteTask` 콜백이 한꺼번에 사라집니다.

```js
// AddTask: 쓰기 전용
const dispatch = useContext(TasksDispatchContext);
dispatch({ type: 'added', id: nextId++, text });

// TaskList: 읽기 전용
const tasks = useContext(TasksContext);
```

## 흔한 실수

- **state와 dispatch를 하나로 묶는다**: `value={{ tasks, dispatch }}`처럼 단일 context로 합치는 패턴은 직관적이지만, `tasks`가 바뀔 때마다 dispatch만 쓰는 컴포넌트까지 전부 재렌더됩니다. 분리만 해도 큰 트리에서 체감 성능이 달라집니다.
- **Provider value에 inline 객체를 그대로 전달**: `value={{ tasks, dispatch }}`는 매 렌더마다 새 객체 참조가 됩니다. 객체 정체성이 바뀌므로 구독 컴포넌트가 항상 다시 그려집니다. 두 context로 분리하거나 `useMemo`로 안정화해야 합니다.
- **`createContext()`의 초기값 의미 오해**: 초기값 `null`은 "기본값"이 아니라 "Provider 밖에서 호출됐을 때만 보이는 fallback"입니다. 이 사실을 모르면 `null`이 보일 때 디버깅이 한참 헤맵니다.

## 복습

- prop drilling은 reducer 단독으로 풀리지 않는다 — context와 결합해야 한다.
- state context와 dispatch context는 **재렌더 분리·관심사 분리** 두 가지 이유로 나눈다.
- 3단계 빌드: `createContext × 2` → Provider 안에서 `useReducer` → 자식에서 `useContext × 2`.
- 다음 시간 [S7.C2]에는 이 wiring을 `TasksProvider` + 커스텀 훅으로 응집해 App.js를 깨끗이 만듭니다.
