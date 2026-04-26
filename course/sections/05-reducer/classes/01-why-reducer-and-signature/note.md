# 왜 Reducer인가 — useReducer 시그니처와 도입 동기

> LOs: LO-S5.1

## 개요
프라하 여행 일정을 짜는 Tasks 앱을 떠올려 봅시다. 할 일을 추가하고, 텍스트를 수정하고, 체크하고, 삭제하는 핸들러 네 개. 각 핸들러마다 `setTasks` 호출이 흩어져 있고, 갱신 로직은 미묘하게 다릅니다. 어느 날 "체크가 풀린다"는 버그가 들어왔을 때, 우리는 네 군데를 모두 열어 보며 30분을 태웁니다 [slide 2]. 오늘 만날 `useReducer`는 이 흩어진 갱신 로직을 한 곳으로 모아, 코드를 진단 가능한 모양으로 다시 짜는 도구입니다.

## 핵심 개념
**Reducer**는 `(state, action) => nextState` 형태의 **순수 함수**입니다 [slide 3]. 세 가지 속성이 본질을 이룹니다.

1. **분리된 위치** — 컴포넌트 외부에 정의되므로 props/state 클로저에 묶이지 않고, 인자만으로 동작합니다. 그래서 단위 테스트가 쉽습니다.
2. **무엇 vs 어떻게** — `action`은 "무엇이 일어났는가"를 묘사하는 평범한 객체(`{ type: 'added', ... }`), reducer는 "그래서 다음 state는 무엇인가"만 답합니다. 핸들러는 의도만 외치면 됩니다.
3. **누적기 모델** — 이름은 `Array.prototype.reduce`에서 왔습니다. `[1,2,3].reduce((acc, x) => acc + x, 0)`에서 `acc`가 state, `x`가 action에 해당합니다. 시간 축을 따라 action이 흘러 들어오면 reducer가 누적기를 갱신해 가는 그림을 머릿속에 그려두세요.

이 분리가 왜 중요할까요? 디버깅 시 모든 state 전이가 reducer 한 곳을 지나가므로 `console.log(action)` 한 줄이면 사용자가 무엇을 했는지 시간순으로 보입니다 [slide 4]. 핸들러를 뒤지지 않아도 됩니다.

## 예시
`useReducer`의 시그니처는 `useState`와 쌍둥이처럼 닮았습니다.

```js
const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
```

반환값은 `[현재 state, dispatch 함수]` 두 개. `dispatch(action)`을 호출하면 React가 내부적으로 `tasksReducer(현재tasks, action)`을 실행해 다음 state로 교체합니다. 핸들러 비교를 보면 가치가 분명해집니다 [slide 5].

```js
// useState 버전 — 갱신 '방법'이 핸들러에 박힘
function handleAddTask(text) {
  setTasks([...tasks, { id: nextId++, text, done: false }]);
}

// useReducer 버전 — '무엇이 일어났는가'만 외침
function handleAddTask(text) {
  dispatch({ type: 'added', id: nextId++, text });
}
```

핸들러는 사건의 이름표만 붙여 dispatch에 던지고, 새 배열을 만드는 책임은 reducer로 이동합니다.

## 흔한 실수
- **`dispatch`를 setter처럼 쓰는 오해**: `dispatch(newTasks)`처럼 다음 state를 직접 넘기지 않습니다. dispatch에는 항상 **action 객체**를 전달하고, 다음 state 계산은 reducer가 합니다.
- **action.type을 명사형으로 짓기**: `'task'`, `'newTask'`처럼 명사로 쓰면 "무엇을 하는가"가 사라집니다. `'added'`, `'changed'`처럼 동사 과거형으로 — 자세한 컨벤션은 [S5.C3]에서 진단합니다.

## 복습
Reducer는 `(state, action) => nextState` 순수 함수, `useReducer(reducer, initialState)`는 `[state, dispatch]`를 돌려준다는 두 문장만 입에 붙여 두세요. 다음 시간 [S5.C2]에서는 이 시그니처를 실제 Tasks 앱에 끼워 넣는 3단계 마이그레이션을 손으로 따라가 봅니다.
