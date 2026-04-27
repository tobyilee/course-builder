# Ref 안티패턴과 전역 변수 → ref 리팩터링

> LOs: LO-S1.4, LO-S1.5

## 개요

ref가 강력하다고 아무 자리에나 넣으면 무서운 버그가 생깁니다 [slide 1]. 카운터를 만들었는데 클릭해도 숫자가 안 바뀌거나, 토글 스위치가 항상 'Off'만 보이는 식입니다. 두 버그 모두 "ref를 잘못된 자리에 쓴" 같은 원인에서 출발합니다. 오늘은 안티패턴 두 가지를 식별하고, 반대로 전역 변수로 timeout을 관리하던 코드를 ref로 리팩터링하는 표준 처방까지 익힙니다.

## 핵심 개념

두 가지 안티패턴을 외워두세요 [slide 2].

**안티패턴 1 — 렌더 결과에 ref.current 사용**: `<button>You clicked {countRef.current} times</button>`. ref.current가 바뀌어도 React는 재렌더하지 않으므로 화면에는 옛 값이 박혀 있습니다(stale 표시).

**안티패턴 2 — 렌더 함수에서 ref.current로 분기**: `if (modeRef.current === 'dark') return <Dark/>`. ref는 mutable이고 React는 언제 렌더할지 정확한 보장이 없으니 같은 입력에 다른 출력이 나올 수 있습니다(비결정적 렌더).

원칙은 한 줄. **렌더 중에는 ref.current를 읽지도 쓰지도 않습니다** (예외: `useRef(initial)` 초기화). 안전한 자리는 이벤트 핸들러와 Effect 안 — 렌더가 끝난 뒤입니다 [slide 2].

진단 질문도 한 줄. "이 값이 바뀌면 화면이 다시 그려져야 하는가?" YES면 state, NO면 ref [S1.C1].

## 예시

**Counter / Toggle 진단** [slide 3]

```js
// Before (Counter): 클릭해도 화면 0 그대로
const countRef = useRef(0);
function handleClick() { countRef.current++; }
return <button>{countRef.current} times</button>;
// After: 표시 값이므로 useState
const [count, setCount] = useState(0);
```

Toggle도 동일 — `isOnRef`를 `useState(false)`로 옮기면 끝납니다.

**전역 변수 → useRef 리팩터링** [slide 4]

```js
// Before — 모듈 전역, 모든 인스턴스 공유
let timeoutID;
function DebouncedButton({ onClick }) {
  return <button onClick={() => {
    clearTimeout(timeoutID);
    timeoutID = setTimeout(onClick, 1000);
  }}/>;
}

// After — 인스턴스별 ref
function DebouncedButton({ onClick }) {
  const timeoutRef = useRef(null);
  return <button onClick={() => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClick, 1000);
  }}/>;
}
```

리팩터링 절차는 기계적입니다. 모듈 전역 `let timeoutID;`를 제거 → 컴포넌트 본문 안에 `const timeoutRef = useRef(null);` 추가 → 모든 `timeoutID` 참조를 `timeoutRef.current`로 일괄 치환. 결과적으로 각 인스턴스가 자기 `{ current }`를 가져 격리가 회복되고, 화면 표시와 무관하니 ref가 정당화됩니다.

## 흔한 실수

- **"전역 변수면 어쨌든 보존되니까 OK"라는 착각**: 보존은 되지만 모든 인스턴스가 공유하므로 동일 컴포넌트가 둘 이상 렌더되는 순간 cancel이 엉킵니다. 인스턴스별 격리는 ref만 줍니다.
- **리팩터링 시점을 놓치는 실수**: 처음엔 한 화면에 한 개만 쓸 거라 전역 변수로 시작했다가, 나중에 같은 컴포넌트가 여러 곳에 등장할 때 버그가 터집니다. 비-렌더 데이터를 컴포넌트 본문에 둘지 모듈 최상단에 둘지 고민될 때, 답은 거의 항상 useRef입니다.

## 복습

렌더 결과·렌더 분기에 ref.current를 쓰면 stale 표시와 비결정적 렌더가 발생합니다. 진단은 "화면에 영향이 있는가?" 한 줄, 처방은 state로 옮기기. 반대로 전역 변수로 비-렌더 데이터를 관리하던 코드는 useRef로 옮겨 인스턴스별 격리를 회복합니다. 다음 섹션 [S2.C1]에서는 같은 ref를 'DOM 노드'에 붙여 focus·scroll 같은 명령형 작업으로 확장합니다.
