# useState vs useReducer 트레이드오프와 Immer 옵션

> LOs: LO-S5.4, LO-S5.5

## 개요
Reducer를 배웠다고 모든 `useState`를 갈아엎어야 할까요? 아닙니다 [slide 2]. 프라하 Tasks 앱처럼 핸들러가 네 개 이상이면 이득이 분명하지만, 토글 하나뿐인 컴포넌트에 reducer를 도입하는 건 과잉입니다. 오늘은 "언제 갈아탈지" 판단 기준을 4축으로 세우고, mutation 스타일 작성을 가능케 하는 **Immer 옵션**까지 살펴봅니다.

## 핵심 개념

**비교 4축** [slide 3]

- **코드량**: `useState`가 적습니다. `useReducer`는 reducer 함수와 action 객체라는 보일러플레이트가 따라옵니다.
- **가독성**: 단순 갱신은 `useState`가 직관적, 여러 핸들러가 같은 state를 다양하게 갱신하는 복잡한 경우는 `useReducer`가 정리됩니다.
- **디버깅**: reducer 한 곳에 `console.log(action, nextState)` 한 줄을 박으면 모든 state 전이가 시간순으로 보입니다. `useState`는 setter 호출 지점을 일일이 추적해야 합니다 — [S5.C1]에서 짚은 진단성의 본질.
- **테스트**: reducer는 컴포넌트 마운트 없이 `tasksReducer(state, action)` 호출만으로 단위 테스트가 됩니다. `useState` 로직은 컴포넌트를 통째로 렌더해야 검증할 수 있습니다.

**갈아타기 결정 기준** [slide 4]

질문은 하나로 줄어듭니다. *"여러 핸들러가 같은 state를 다양하게 갱신하는가?"* Yes면 `useReducer`, No면 `useState`. 구체적 신호로는 `setState`가 3개 이상이고, 핸들러 사이에 갱신 로직 중복(같은 `tasks.map(...)` 패턴 반복)이 보일 때입니다. 한 컴포넌트 안에서 둘을 혼용해도 정상입니다 — Tasks는 `useReducer`, 패널 열림 토글은 `useState`.

```js
function TaskApp() {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  // ...
}
```

## 예시
**Immer — `useImmerReducer`** [slide 5]

Immer는 `draft`를 Proxy로 감싸 변경을 기록하고, 내부에서 immutable 복사본을 만들어 반환합니다. mutation처럼 보이지만 실제로는 새 객체가 만들어집니다.

```js
// 일반 reducer
case 'changed':
  return tasks.map(t => t.id === action.task.id ? action.task : t);

// Immer
case 'changed': {
  const i = draft.findIndex(t => t.id === action.task.id);
  draft[i] = action.task;
  break;
}
```

두 형태는 **의미상 동등**합니다. 깊게 중첩된 객체를 갱신할 때 spread 연쇄(`{ ...a, b: { ...a.b, c: ... } }`)가 사라지는 게 가장 큰 이득입니다. 단점은 (1) 추가 의존성, (2) 디버깅 시 Proxy 한 겹 더, (3) 팀이 "mutation처럼 보이지만 사실은 아님"을 이해해야 한다는 점. 단순 배열/객체면 일반 reducer로 충분, 깊은 중첩이면 Immer가 코드량을 절약합니다.

## 흔한 실수
- **무조건 reducer로 마이그레이션**: 토글 하나 있는 컴포넌트에 reducer를 끼우면 보일러플레이트만 늘어납니다. 결정 기준에 신호가 없으면 `useState`를 유지하세요.
- **Immer의 `return`과 mutation 혼용**: Immer reducer에서 한 case는 `return draft.filter(...)`로 새 값을 돌려주고 다른 case는 `draft.push(...)`로 변경만 하면 동작은 하지만 일관성이 깨져 읽기 어려워집니다. 한 reducer 안에서는 한 스타일로 통일하세요.

## 복습
4축(코드량·가독성·디버깅·테스트)으로 비교하고, 핸들러가 다수이며 갱신이 복잡할 때 `useReducer`로 갑니다. 한 컴포넌트 내 혼용은 자연스럽고, Immer는 mutation 스타일 단축 표기로 일반 reducer와 의미 동등합니다. 다음 섹션 [S6]에서는 Context로 reducer를 컴포넌트 트리에 뿌리는 패턴을 만나게 됩니다.
