---
marp: true
theme: default
paginate: true
footer: "LO-S7.2"
---

<!-- beat: b1 -->

# TasksProvider + 커스텀 훅으로 응집하기

## 그리고 다중 도메인으로 확장

- C1의 3단계 wiring은 **App.js를 어수선하게** 만든다
- state 로직이 UI 트리에 섞이면 재사용·테스트 어려움
- 오늘: 한 파일로 응집 + `use…` API + 도메인 확장 + 도구 선택

---

<!-- beat: b2 -->
<!-- _footer: "LO-S7.2" -->

## Provider 컴포넌트 패턴

- 모든 state 관리 로직을 **한 컴포넌트에 캡슐화**
- 내부: `useReducer`, 두 Context Provider, `tasksReducer`, `initialTasks`
- 외부 표면: `children` prop을 감싸는 컴포넌트 하나
- App.js는 UI 조립에만 집중 → 관심사 분리 완성

---

<!-- beat: b3 -->
<!-- _footer: "LO-S7.2" -->

## TasksContext.js — 단일 파일 응집

```jsx
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
```

- 두 context는 **module-private** — export 하지 않음
- 외부 노출: `TasksProvider`, `useTasks`, `useTasksDispatch` 셋뿐

---

<!-- beat: b4 -->
<!-- _footer: "LO-S7.2" -->

## 커스텀 훅으로 소비자 API 다듬기

```js
export function useTasks() {
  return useContext(TasksContext);
}
export function useTasksDispatch() {
  return useContext(TasksDispatchContext);
}

// 소비자
const tasks = useTasks();
const dispatch = useTasksDispatch();
```

- 의미론적 이름 + 셀렉터/devtools 추가에도 소비자 코드 그대로

---

<!-- beat: b5 -->
<!-- _footer: "LO-S7.3" -->

## 다중 도메인 확장 — 같은 패턴 복제

```jsx
<ThemeProvider>
  <AuthProvider>
    <TasksProvider>
      <App />
    </TasksProvider>
  </AuthProvider>
</ThemeProvider>
```

- 도메인 경계 기준: **함께 변하는가? 같은 액션에 반응하는가?**
- 의존성 방향에 맞춰 중첩 (Theme → Auth → Tasks)

---

<!-- beat: b6 -->
<!-- _footer: "LO-S7.4" -->

## 언제 외부 라이브러리로?

| 신호 | 추천 |
|---|---|
| 도메인 5~10개 이내, 미들웨어·devtools 불필요 | **reducer + context** |
| 보일러플레이트 줄이고 점진적 마이그레이션 | **Zustand** |
| 대규모·여러 팀, time-travel·thunk·셀렉터 메모 | **Redux Toolkit** |

> 통증이 명확해질 때 도입 — 미리 도입하지 말 것

---

<!-- beat: b7 -->
<!-- _footer: "LO-S7.3" -->

## 자문자답 — 내 프로젝트에 적용

- 내 앱의 도메인을 Provider로 어떻게 자를까? (User / Cart / Toast …)
- 두 context를 export 하지 않는 이유를 한 문장으로?
- 지금 Redux/Zustand가 정말 필요한가? 없다면 그 근거는?

---

<!-- beat: b8 -->
<!-- _footer: "LO-S7.2" -->

## Recap — S7 마무리

- **응집**: TasksProvider + `useTasks` / `useTasksDispatch`
- **확장**: 같은 패턴을 Auth/Theme로 복제, '함께 변하는가'로 경계 결정
- **평가**: 외부 라이브러리는 통증이 명확할 때만

> 다음: S8 캡스톤에서 mini Kanban으로 모든 패턴 통합
