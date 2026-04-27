---
marp: true
theme: default
paginate: true
footer: "LO-S2.3"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 20px; }
---

<!-- beat: b1 -->

# flushSync로 타이밍 맞추기

그리고 React가 관리하는 DOM은 손대지 않기

---

<!-- beat: b1 -->
<!-- _footer: "LO-S2.3" -->

## todo-list 자동 스크롤이 어긋나는 이유

```jsx
function handleAdd() {
  setTodos([...todos, newTodo]);
  listRef.current.lastChild.scrollIntoView();
  // 새 항목이 아니라 '이전 마지막' 항목까지만 스크롤됨
}
```

- state setter는 **비동기 batch** — 핸들러가 끝나야 commit
- 다음 줄에서 lastChild를 읽으면 아직 옛 DOM
- 오늘의 출발점

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.3" -->

## flushSync — 동기 commit 강제

- 기본 setState는 핸들러 끝에서 **batch commit**
- `flushSync(() => setX(...))`는 콜백 내부 setter를 **즉시 commit**
- 다음 줄에서는 새 DOM이 이미 반영됨 → lastChild가 새 항목
- 남용 금지: batching 이점을 망친다
- 사용처: 'state 직후 새 DOM을 측정·스크롤해야 할 때'만

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.3" -->

## 예제 — flushSync로 새 항목 스크롤

```jsx
import { flushSync } from 'react-dom';
// react가 아니라 react-dom!

function handleAdd() {
  const newTodo = { id: nextId++, text };
  flushSync(() => {
    setText('');
    setTodos([...todos, newTodo]);
  });
  // 여기서 새 DOM이 보장됨
  listRef.current.lastChild.scrollIntoView();
}
```

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.4" -->

## React 관리 DOM 직접 조작 금지

```jsx
// ❌ 충돌·크래시 시나리오
ref.current.remove();   // React 모르게 노드 제거
setShow(true);          // React는 노드가 있다고 믿음 → 다음 렌더에서 충돌
```

- React가 JSX로 그리는 노드는 **React만 add/remove**
- 우리는 읽기·측정·명령형 메서드 호출만
- 안전 영역: JSX에서 **항상 비어있는 컨테이너** (third-party가 그 안에서 자유롭게)

---

<!-- beat: b5 -->
<!-- _footer: "LO-S2.4" -->

## 자문자답 — 4가지 판단

- setTodos 후 새 노드 위치 측정? → **flushSync 필요**
- setTodos 후 토스트만 띄우기? → **flushSync 불필요**
- 제거된 항목을 다시 보이게? → **state로만 제어**, `remove()` 폐기
- D3 차트를 React에 끼우려면? → 빈 `<div ref={...}>` + 안쪽은 D3 위임 (안전 영역)

---

<!-- beat: b6 -->
<!-- _footer: "LO-S2.3" -->

## 정리 — 다음 시간 예고

- `flushSync`는 batching을 깨고 즉시 commit → 직후 새 DOM 측정·스크롤 가능
- React 관리 노드 직접 추가/제거는 state-DOM 불일치 → 충돌
- 안전 영역은 'JSX에서 늘 비어있는 컨테이너' 내부뿐
- 다음 시간: 자식 컴포넌트에 ref 안전하게 넘기기 — **forwardRef → ref-as-prop → useImperativeHandle**
