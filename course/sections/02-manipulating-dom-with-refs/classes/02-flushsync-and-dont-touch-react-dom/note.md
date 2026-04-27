# flushSync로 타이밍 맞추기 + React가 관리하는 DOM은 손대지 않기

> LOs: LO-S2.3, LO-S2.4

## 개요

투두 리스트에 새 항목을 추가하면 자동으로 맨 아래로 스크롤되길 원합니다. 그래서 이렇게 씁니다 — `setTodos([...todos, newTodo])` 직후 `listRef.current.lastChild.scrollIntoView()`. 그런데 한 칸이 어긋납니다 [slide 1]. 새 항목이 아니라 **이전 마지막 항목**으로 스크롤되죠. 왜일까요? 이번 시간에는 이 미스터리의 정체인 React의 batching을 들여다보고, `flushSync`로 타이밍을 맞추는 법을 익힙니다. 이어서 정반대 방향의 위험 — React가 관리하는 DOM을 직접 건드리는 일 — 이 왜 충돌을 부르는지도 분석합니다.

## 핵심 개념

**기본적으로 `setState`는 batched 입니다.** [slide 2] 이벤트 핸들러가 끝날 때까지 React는 setter들을 모아두었다가 한 번에 commit 합니다. 따라서 `setTodos(...)` 다음 줄에서 `lastChild`를 읽으면 아직 새 항목이 DOM에 들어가지 않은 **예전 DOM**의 마지막 자식을 보게 됩니다.

`flushSync(() => setTodos(...))`는 콜백 내부의 setter들을 **동기적으로 즉시 commit**하라고 React에게 강제합니다 [S1.C1]에서 본 useRef 타이밍 모델과 결합해 보면, flushSync 다음 줄에서는 이미 commit이 끝났으므로 `ref.current`가 새 DOM을 가리킵니다. 다만 매 setState마다 동기 commit을 강요하면 batching의 성능 이점을 잃으므로, "state 변경 직후 새 DOM의 위치/크기를 즉시 읽어야 할 때"에만 좁게 사용합니다.

다른 한 축은 **"React가 관리하는 DOM은 손대지 않는다"** 원칙입니다 [slide 4]. JSX로 그린 노드는 React의 가상 DOM과 실제 DOM이 짝을 이룬 채 동기화됩니다. 우리가 `ref.current.remove()`로 노드를 직접 떼어내면, React는 그 사실을 모릅니다. 다음 렌더에서 그 노드의 텍스트를 갱신하거나 자식을 끼워 넣으려는 순간 — `Failed to execute 'removeChild'` 같은 에러로 충돌합니다. **읽기와 측정, 명령형 메서드 호출은 OK, 추가/제거는 NO** 가 원칙입니다.

단 하나의 안전 영역이 있습니다. **JSX에서 늘 비어 있는 컨테이너** — 예: `<div ref={chartRef} />` — 의 내부는 React가 손대지 않으므로 D3나 지도 라이브러리가 자식을 자유롭게 append/remove해도 충돌하지 않습니다.

## 예시

자동 스크롤 패턴을 flushSync로 깔끔하게 처리합니다 [slide 3].

```jsx
import { flushSync } from 'react-dom'; // 'react'가 아니라 'react-dom'

function handleAdd() {
  const newTodo = { id: nextId++, text };
  flushSync(() => {
    setText('');
    setTodos([...todos, newTodo]);
  });
  // 이 줄에 도달했을 때 새 todo는 이미 DOM에 들어가 있다
  listRef.current.lastChild.scrollIntoView();
}
```

반면 위험한 패턴은 다음과 같습니다.

```jsx
// 빨간 영역 — state-DOM 불일치
<div>{show && <p ref={ref}>Hello</p>}</div>
// ...
ref.current.remove();   // React 모르게 노드 삭제
setShow(true);          // React: "노드는 거기 있을 텐데?" → 충돌
```

차트 라이브러리 통합 같은 안전한 시나리오는 이렇게 갑니다.

```jsx
function MapPanel() {
  const containerRef = useRef(null);
  useEffect(() => {
    const map = thirdParty.createMap(containerRef.current);
    return () => map.destroy();
  }, []);
  return <div ref={containerRef} />; // JSX에서 늘 비어 있음 → 안전 영역
}
```

## 흔한 실수

- **`flushSync` 없이 새 DOM을 즉시 읽기**: `setTodos` 직후 `lastChild.scrollIntoView()`를 부르면 batching 때문에 한 박자 어긋납니다. 같은 핸들러 안에서 새 DOM이 필요하면 setter를 `flushSync`로 감싸세요.
- **React가 관리하는 노드 직접 변경**: `ref.current.remove()`로 사라지게 만든 뒤 state로 다시 보이려 하면, React state와 실제 DOM이 어긋나 충돌합니다. 보이고 숨기는 것은 **반드시 state로만** 제어하세요.
- **flushSync 남용**: 단순히 토스트 메시지를 띄우거나 다음 화면을 이동시키는 데에는 동기 commit이 필요 없습니다. "DOM을 즉시 측정해야 하는가?"가 유일한 판단 기준입니다.

## 복습

flushSync는 setState batching을 깨고 즉시 commit을 강제해 새 DOM을 곧바로 측정·스크롤할 수 있게 해줍니다. React가 관리하는 노드를 직접 추가·제거하면 state-DOM 불일치로 충돌하므로, 안전 영역은 "JSX에서 늘 비어 있는 컨테이너 내부"뿐입니다. 다음 시간에는 자식 컴포넌트에 ref를 안전하게 넘기는 법 — forwardRef, React 19 ref-as-prop, useImperativeHandle — 을 봅니다 [S2.C3].
