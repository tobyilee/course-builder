# Source: Extracting State Logic into a Reducer

## 정의
Reducer = `(state, action) => nextState` 형태의 **순수 함수**. state 갱신 로직을 컴포넌트 외부로 분리.

## useState → useReducer 3단계

### 1. setState 호출 → dispatch action
```js
// before
function handleAddTask(text) {
  setTasks([...tasks, { id: nextId++, text, done: false }]);
}
// after
function handleAddTask(text) {
  dispatch({ type: 'added', id: nextId++, text });
}
```

### 2. reducer 함수 작성
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

### 3. useReducer 훅 사용
```js
import { useReducer } from 'react';
const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
```

## Action 객체 컨벤션
- `type` 문자열 (필수, 동사 과거형 권장: `'added'`, `'changed'`, `'deleted'`)
- 그 외 필요한 데이터 필드

```js
dispatch({ type: 'added', id: 3, text: 'New task' });
dispatch({ type: 'changed', task: updatedTask });
dispatch({ type: 'deleted', id: 1 });
```

## useState vs useReducer

| 측면 | useState | useReducer |
|---|---|---|
| 코드량 | 적음 | 많음 (보일러플레이트) |
| 가독성 | 단순 갱신엔 좋음 | 복잡 로직 정리에 우월 |
| 디버깅 | 어디서 잘못 set 했는지 추적 어려움 | reducer 안에 console.log 한 줄로 모든 전이 관찰 |
| 테스트 | 컴포넌트 단위 | 순수 함수, 단위 테스트 쉬움 |
| 추천 시점 | 단순 state | 여러 핸들러가 같은 state를 다양하게 갱신할 때 |

한 컴포넌트 안에서 useState와 useReducer 혼용 가능.

## Reducer 규칙

### 1. 순수해야 한다
- 같은 입력 → 같은 출력
- 네트워크 요청, setTimeout 같은 side effect 금지
- 객체/배열 mutation 금지 (불변 갱신)

### 2. 한 action = 하나의 사용자 상호작용
```js
// ❌ 폼 리셋을 필드별 dispatch로
dispatch({ type: 'set_field', field: 'name', value: '' });
dispatch({ type: 'set_field', field: 'email', value: '' });
// ✅ 단일 action
dispatch({ type: 'reset_form' });
```

## Immer 옵션 — useImmerReducer
```js
function tasksReducer(draft, action) {
  switch (action.type) {
    case 'added': draft.push({ id: action.id, text: action.text, done: false }); break;
    case 'changed':
      const i = draft.findIndex(t => t.id === action.task.id);
      draft[i] = action.task; break;
    case 'deleted':
      return draft.filter(t => t.id !== action.id);
  }
}
const [tasks, dispatch] = useImmerReducer(tasksReducer, initialTasks);
```

## "Reducer" 이름의 유래
`Array.prototype.reduce`와 같은 패턴 — 누적기(accumulator)에 새 입력을 적용해 다음 누적기를 만든다. React의 reducer는 `(stateSoFar, action) => nextState`.

## DIY 구현
```js
function useReducer(reducer, initialState) {
  const [state, setState] = useState(initialState);
  function dispatch(action) {
    setState(s => reducer(s, action));
  }
  return [state, dispatch];
}
```

## Recap
- 3단계: dispatch action → reducer 작성 → useReducer 훅
- action.type은 동사형 문자열, 한 상호작용 = 한 action
- reducer는 순수, mutation 금지
- 디버깅·테스트 우월, 단순 state엔 useState로 충분
- Immer로 mutation 스타일 가능
