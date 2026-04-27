# Source: Manipulating the DOM with Refs

## You will learn
- ref={myRef}로 React가 관리하는 DOM 노드 접근
- 다른 컴포넌트의 DOM 노드 접근
- React가 관리하는 DOM 직접 조작이 안전한 경우/위험한 경우

## 기본 패턴
```js
import { useRef } from 'react';
const myRef = useRef(null);

return <div ref={myRef}>;
// commit phase 후 myRef.current === DOM node
```

## 흔한 사용 사례

### 입력 포커스
```js
const inputRef = useRef(null);
function handleClick() { inputRef.current.focus(); }
return (<><input ref={inputRef} /><button onClick={handleClick}>Focus</button></>);
```

### 스크롤
```js
elementRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
```

### 비디오 재생/정지
```js
isPlaying ? videoRef.current.play() : videoRef.current.pause();
```

### 측정
`getBoundingClientRect()` 등 브라우저 API 호출.

## flushSync — DOM 업데이트 동기화
state setter는 기본적으로 비동기 batch. ref로 새 DOM을 즉시 읽어야 하면 flushSync로 강제:
```js
import { flushSync } from 'react-dom';

function handleAdd() {
  flushSync(() => setTodos([...todos, newTodo]));
  listRef.current.lastChild.scrollIntoView();
}
```
flushSync 없으면 새 항목이 아직 DOM에 없어 스크롤이 어긋난다.

## ⚠️ Pitfall: React가 관리하는 DOM 직접 조작 금지

```js
// ❌
ref.current.remove();   // React 모르는 사이 노드 제거
setShow(true);          // React는 노드가 있다고 생각 → 충돌/크래시
```

**안전한 영역**: React가 손대지 않는 빈 노드 — JSX에서 항상 비어있는 div 같은 곳에는 직접 자식 append 가능.

## 자식 컴포넌트로 ref 전달

### forwardRef 패턴 (React 18 이전 / 19 이전)
```js
const MyInput = forwardRef((props, ref) => <input ref={ref} {...props} />);
```

### React 19+: ref가 일반 prop처럼 동작
```js
function MyInput({ ref }) { return <input ref={ref} />; }
function MyForm() {
  const inputRef = useRef(null);
  return <MyInput ref={inputRef} />;
}
```

### useImperativeHandle — 노출 API 제한
```js
function MyInput({ ref }) {
  const realInputRef = useRef(null);
  useImperativeHandle(ref, () => ({
    focus() { realInputRef.current.focus(); }
  }));
  return <input ref={realInputRef} />;
}
// 부모는 .focus()만 호출 가능, .value 직접 접근 X
```

## ref가 부착되는 시점 (timing)
- **render phase**: 컴포넌트 호출. ref.current는 아직 null.
- **commit phase**: React가 DOM 변경 적용 + ref.current = node 설정.
- 업데이트 시: 변경 직전에 null로 초기화 → 변경 후 재설정.
- **읽기 위치**: 이벤트 핸들러 또는 Effect 안 (render 중 X).

## Recap
- useRef + ref={...}로 React 관리 DOM 노드 접근
- 사용처: focus, scroll, measure, video 같은 브라우저 API
- flushSync로 state 업데이트 직후 DOM 즉시 읽기 가능
- React가 관리하는 노드는 직접 조작 금지 (자체 빈 영역만)
- 자식 ref 노출은 forwardRef → React 19에서 ref prop으로 단순화
- useImperativeHandle로 노출 API 통제
