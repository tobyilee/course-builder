# Source: Referencing Values with Refs

## You will learn
- 컴포넌트가 정보를 "기억"하지만 새 렌더를 트리거하고 싶지 않을 때 ref 추가
- useRef Hook이 반환하는 것
- Ref와 State의 차이
- Ref를 안전하게 사용하는 법

## useRef 기본
```js
import { useRef } from 'react';
const ref = useRef(0);
// ref → { current: 0 }
ref.current = 5;     // 직접 mutation 가능 (state와 다름)
console.log(ref.current); // 5 (즉시, 동기적)
```

## Ref vs State

| 측면 | useRef | useState |
|---|---|---|
| 반환 | `{ current: initial }` | `[value, setValue]` |
| 재렌더 트리거 | ❌ 안 함 | ✅ 함 |
| Mutation | 직접 `current = ...` | setter 호출 필수 |
| 렌더 중 읽기 | ⚠️ 금지 (초기화 제외) | ✅ snapshot |
| 다음 렌더까지 보존 | ✅ | ✅ |

**규칙**: 화면에 보일 정보면 state, 영향 안 주면 ref.

## 좋은 사용 사례
1. **timeout/interval ID 보관**:
```js
const timeoutRef = useRef(null);
timeoutRef.current = setTimeout(() => {...}, 1000);
clearTimeout(timeoutRef.current);
```
2. DOM 노드 (다음 챕터)
3. 렌더에 영향 없는 객체
4. 비동기 콜백에서 최신 값 읽어야 할 때

## 안티패턴

### ❌ 렌더 중 ref.current 읽기
```js
// 클릭해도 화면 안 바뀜 — ref는 재렌더 트리거 X
function Counter() {
  let countRef = useRef(0);
  function handleClick() { countRef.current = countRef.current + 1; }
  return <button onClick={handleClick}>You clicked {countRef.current} times</button>;
}
```

### ❌ 렌더에 쓰일 값을 ref로
```js
const isOnRef = useRef(false);
return <div>{isOnRef.current ? 'On' : 'Off'}</div>; // 항상 stale
```

## 핵심 예제: 채팅 + timeout (Before/After)

**Before (지역 변수 — 매 렌더마다 초기화돼서 timeout cancel 안 됨)**:
```js
let timeoutID = null; // ❌
function handleSend() { timeoutID = setTimeout(..., 3000); }
function handleUndo() { clearTimeout(timeoutID); } // null!
```

**After (ref — 렌더 사이 보존)**:
```js
const timeoutRef = useRef(null);
function handleSend() { timeoutRef.current = setTimeout(..., 3000); }
function handleUndo() { clearTimeout(timeoutRef.current); } // OK
```

## Stopwatch 예제 (state + ref 조합)
```js
const [startTime, setStartTime] = useState(null);
const [now, setNow] = useState(null);          // 렌더 데이터 → state
const intervalRef = useRef(null);              // ID → ref

function handleStart() {
  setStartTime(Date.now());
  setNow(Date.now());
  clearInterval(intervalRef.current);
  intervalRef.current = setInterval(() => setNow(Date.now()), 10);
}
function handleStop() { clearInterval(intervalRef.current); }
```

## Debouncing — 컴포넌트별 ref vs 전역 변수
```js
// ❌ 전역 — 모든 버튼이 서로의 timeout 취소
let timeoutID;
// ✅ 인스턴스마다 자체 ref
const timeoutRef = useRef(null);
```

## 비동기에서 최신 state 읽기 (state + ref 동기 유지)
```js
const [text, setText] = useState('');
const textRef = useRef(text);
function handleChange(e) {
  setText(e.target.value);
  textRef.current = e.target.value; // sync
}
function handleSend() {
  setTimeout(() => alert(textRef.current), 3000); // 최신 값
}
```

## 내부 구현 (개념적)
```js
function useRef(initial) {
  const [ref] = useState({ current: initial });
  return ref; // 매 렌더 같은 객체
}
```

## Recap
- ref = 재렌더 X로 값을 기억
- ref.current로 접근 (mutable)
- 렌더 사이 보존, but 트리거 안 함
- 적절: timeout ID, DOM 노드, 비-렌더 데이터
- 렌더 중 읽기/쓰기 금지 (초기화 제외)
- 표시되는 값에는 state. 부수효과 데이터에는 ref.
- 인스턴스별로 자체 ref — 전역 변수 회피
