---
marp: true
theme: default
paginate: true
footer: "LO-S1.1 · LO-S1.2"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  pre { line-height: 1.35; }
---

<!-- beat: b1 -->

# useRef 기본과 state와의 차이

재렌더 없이 값을 기억하는 "메모 칸"

S1 · Class 1

---

<!-- beat: b1 -->
<!-- _footer: "LO-S1.1" -->

## 채팅 "전송 취소" 버튼이 안 먹는다

- `setTimeout`으로 3초 뒤 전송, 그 사이 취소 버튼을 누르면 cancel
- `let timeoutID` — 매 렌더마다 `null`로 초기화돼 cancel 실패
- `useState` — setter 호출이 또 다른 재렌더를 유발해 어색
- 필요한 건: **재렌더 없이 렌더 사이에 살아남는 자리**
- 그게 바로 `ref`다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S1.1" -->

## useRef가 돌려주는 것

```js
import { useRef } from 'react';

const ref = useRef(0);
// ref → { current: 0 }   ← 매 렌더 같은 객체

ref.current = 5;          // 직접 mutation OK
console.log(ref.current); // 5 (즉시, 동기적)
```

- setter 없이 `current`를 바로 바꾼다
- mutation해도 React는 **재렌더하지 않는다**
- 값은 다음 렌더, 그 다음 렌더까지 그대로 유지

---

<!-- beat: b3 -->
<!-- _footer: "LO-S1.2" -->

## state vs ref — 세 축으로 가르기

| 축 | useState | useRef |
|---|---|---|
| 재렌더 트리거 | 함 | 안 함 |
| Mutation 방식 | setter 필수 | 직접 `current = ...` |
| 렌더 중 읽기 | snapshot 안전 | 금지(초기화 제외) |
| 렌더 사이 보존 | 함 | 함 |

**판별 규칙**: 화면에 보이면 state, 영향 없으면 ref

---

<!-- beat: b4 -->
<!-- _footer: "LO-S1.1" -->

## Before — 지역 변수는 매 렌더마다 리셋

```js
function Chat() {
  let timeoutID = null; // 매 렌더 null

  function handleSend() {
    timeoutID = setTimeout(() => send(), 3000);
  }
  function handleUndo() {
    clearTimeout(timeoutID); // null! cancel 실패
  }
  return <>...</>;
}
```

---

<!-- beat: b4 -->
<!-- _footer: "LO-S1.1" -->

## After — useRef로 렌더 사이 보존

```js
function Chat() {
  const timeoutRef = useRef(null);

  function handleSend() {
    timeoutRef.current = setTimeout(() => send(), 3000);
  }
  function handleUndo() {
    clearTimeout(timeoutRef.current); // 살아있는 ID
  }
  return <>...</>;
}
```

ID는 화면에 안 보임 → ref가 정답. "몇 초 남았는지"는 state.

---

<!-- beat: b5 -->
<!-- _footer: "LO-S1.2" -->

## 잠깐, 직접 분류해보기

다음 값은 state? ref?

- (a) Stopwatch가 화면에 보여주는 **경과 시간**
- (b) Stopwatch의 `setInterval`이 반환한 **ID**
- (c) 디바운싱용 `setTimeout` **ID**

기준 한 줄: "이 값이 바뀌면 화면이 다시 그려져야 하는가?"
정답: **(a) state, (b) ref, (c) ref**

---

<!-- beat: b6 -->
<!-- _footer: "LO-S1.1 · LO-S1.2" -->

## Recap

- `useRef`는 `{ current }` 객체 — mutation해도 재렌더 X
- 비교 세 축: 재렌더 트리거 / mutation / 렌더 중 읽기
- **화면에 보이면 state, 영향 없으면 ref**
- 다음 class — ref가 빛나는 실전 사례 셋
