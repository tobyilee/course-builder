# TasksProvider + 커스텀 훅으로 응집하고 다중 도메인으로 확장하기

> LOs: LO-S7.2, LO-S7.3, LO-S7.4

## 개요

[S7.C1]에서 만든 3단계 wiring은 동작은 합니다. 그런데 `App.js`를 열어 보면 `createContext` 두 줄, `useReducer` 호출, Provider 중첩까지 전부 노출되어 있어 어수선합니다 [slide 1]. state 관리 로직이 UI 트리 안에 섞여 있는 한 재사용도, 단위 테스트도 어렵죠. 이번 시간에는 그 wiring을 **`TasksProvider` 한 컴포넌트로 응집**하고, 소비자 API를 `useTasks` / `useTasksDispatch` **커스텀 훅**으로 깔끔하게 만듭니다. 이어서 Tasks 하나를 넘어 **Auth/Theme까지 확장**하는 전략과, **외부 라이브러리(Redux, Zustand)로 갈아탈 시점**까지 균형 잡힌 시각으로 평가합니다.

## 핵심 개념

**Provider 컴포넌트 패턴** [slide 2]은 모든 state 관리 로직을 한 컴포넌트 안에 캡슐화합니다. 내부에는 `useReducer`, 두 개의 Context Provider, `tasksReducer`, `initialTasks`가 모두 들어가고, 외부에 노출되는 표면은 `children`을 받는 컴포넌트 하나뿐입니다. App은 UI 조립에만 집중하면 됩니다.

**커스텀 훅 패턴** [slide 4]은 `use`로 시작하는 함수가 React에서 자동으로 Custom Hook으로 인식된다는 규칙을 활용합니다. 내부에서 다른 훅(`useContext`)을 호출할 수 있으므로, 소비자는 context 객체 자체를 알 필요 없이 의미론적 이름의 훅 두 개만 기억하면 됩니다. 이 추상화가 주는 이점은 셋입니다.

- **의미론적 이름**: `TasksContext`가 아니라 `useTasks` — 호출부에서 의도가 즉시 읽힙니다.
- **확장 여지**: 추후 셀렉터, devtools 로깅, 메모이제이션을 추가해도 소비자 코드는 그대로입니다.
- **타입 안정성**: TypeScript와 결합하면 반환 타입을 한 곳에서 강타입화할 수 있습니다.

**다중 도메인 확장** [slide 5]은 같은 패턴을 `AuthProvider`, `ThemeProvider`로 복제해 도메인별로 독립시킵니다. 도메인 경계를 자르는 기준은 "함께 변하는가? 같은 사용자 액션에 반응하는가? 분리되어도 의미 있는가?"입니다.

## 예시

**단일 파일 응집** [slide 3] — `TasksContext.js` 하나에 비공개(context 두 개, reducer, initialTasks)와 공개(`TasksProvider`, `useTasks`, `useTasksDispatch`)를 함께 둡니다.

```jsx
const TasksContext = createContext(null);          // module-private
const TasksDispatchContext = createContext(null);  // module-private

export function TasksProvider({ children }) {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
  return (
    <TasksContext value={tasks}>
      <TasksDispatchContext value={dispatch}>{children}</TasksDispatchContext>
    </TasksContext>
  );
}

export function useTasks() { return useContext(TasksContext); }
export function useTasksDispatch() { return useContext(TasksDispatchContext); }
```

**소비자 코드** [slide 4] — context 객체는 보이지도 않습니다.

```js
const tasks = useTasks();
const dispatch = useTasksDispatch();
```

**다중 도메인 중첩** [slide 5] — 의존성 방향에 맞춰 바깥쪽부터 감쌉니다(예: Theme → Auth → Tasks).

```jsx
<ThemeProvider>
  <AuthProvider>
    <TasksProvider>
      <App />
    </TasksProvider>
  </AuthProvider>
</ThemeProvider>
```

**도입 판단** [slide 6]: reducer+context로 충분한 시점은 도메인 5~10개 이내, 미들웨어 불요, 전역 devtools가 절실하지 않을 때입니다. 반대로 ① 큰 스케일·여러 팀 협업 ② time-travel·devtools 필요 ③ thunk/saga 같은 비동기 미들웨어 필요 ④ 셀렉터 메모이제이션 필요가 겹치기 시작하면 Zustand(보일러플레이트 적고 사고 모델 유사) 또는 Redux Toolkit(검증된 대규모 패턴)을 검토합니다.

## 흔한 실수

- **두 context를 외부로 export**: 소비자가 `useContext(TasksContext)`를 직접 호출할 수 있으면 추상화 경계가 깨집니다. context는 module-private로 두고 반드시 `useTasks`만 통과하게 하세요. 그래야 나중에 내부 구현을 바꿔도 호출부가 안전합니다.
- **커스텀 훅 없이 useContext 직접 노출**: 도메인 추상화가 사라지면 셀렉터·로깅·메모이제이션을 추가할 때 모든 호출부를 손봐야 합니다. `use…` 훅 한 겹이 미래의 변경 비용을 흡수합니다.
- **통증 없이 외부 라이브러리부터 도입**: "그냥 Redux부터 쓰자"는 흔한 과잉 설계입니다. 작은 앱이라면 reducer+context로 충분하고, 라이브러리는 통증(스케일·디버깅·미들웨어)이 명확해질 때 도입하는 편이 정직합니다.

## 복습

- `TasksProvider` + `useTasks`/`useTasksDispatch`로 단일 파일 응집과 깔끔한 소비자 API를 동시에 얻는다.
- 다중 도메인은 같은 패턴을 복제, 경계 기준은 "함께 변하는가".
- 외부 라이브러리는 통증이 명확해질 때만 — 그 전엔 reducer+context로 충분.
- S7 마무리. 다음은 [S8.C1] 캡스톤에서 모든 패턴을 mini Kanban으로 통합합니다.
