---
marp: true
theme: default
paginate: true
footer: "LO-S1.4 · LO-S1.5"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  pre { line-height: 1.35; }
---

<!-- beat: b1 -->

# Ref 안티패턴과 리팩터링

렌더 중 ref.current 읽기 금지 · 전역 변수 → useRef

S1 · Class 3

---

<!-- beat: b1 -->
<!-- _footer: "LO-S1.4" -->

## 두 개의 이상한 버그

- 카운터 버튼 — 클릭해도 화면 숫자가 안 바뀐다
- 토글 스위치 — 항상 'Off'만 보인다
- 두 버그 모두 **ref를 잘못된 자리에 쓴** 같은 원인
- 오늘 — 안티패턴을 식별하고, 전역 변수 디바운싱을 ref로 리팩터링

---

<!-- beat: b2 -->
<!-- _footer: "LO-S1.4" -->

## 렌더 중 ref.current는 만지지 않는다

- **안티패턴 1**: 렌더 결과에 `ref.current`를 박는다 → stale 표시
- **안티패턴 2**: 렌더 함수 안에서 `ref.current`로 분기 → 비결정적
- 이유: ref는 mutable + 재렌더 트리거 X → "같은 입력 다른 출력"
- **원칙**: 렌더 중 `ref.current` 읽기/쓰기 금지 (`useRef(initial)` 호출만 예외)
- **안전한 자리**: 이벤트 핸들러, Effect — 렌더가 끝난 뒤

---

<!-- beat: b3 -->
<!-- _footer: "LO-S1.4" -->

## Counter & Toggle — 진단과 처방

```js
// 안티패턴: 화면 표시값을 ref로
function Counter() {
  const countRef = useRef(0);
  function handleClick() { countRef.current++; }
  return <button onClick={handleClick}>
    You clicked {countRef.current} times {/* stale! */}
  </button>;
}
```

- ref는 1, 2, 3으로 증가 — 그러나 재렌더 없음 → 화면은 0
- 처방: **표시 값이면 useState로** (Toggle도 동일)
- 한 줄 진단: "이 값이 바뀌면 화면이 다시 그려져야 하는가?"

---

<!-- beat: b4 -->
<!-- _footer: "LO-S1.5" -->

## Before — 모듈 전역 timeoutID

```js
let timeoutID; // 모든 인스턴스가 공유 ❌

function DebouncedButton({ onClick, timeout }) {
  return <button onClick={() => {
    clearTimeout(timeoutID);
    timeoutID = setTimeout(onClick, timeout);
  }}>...</button>;
}
```

버튼 B를 누르면 버튼 A의 timeoutID가 덮어써져 cancel 충돌.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S1.5" -->

## After — useRef로 인스턴스별 격리

```js
function DebouncedButton({ onClick, timeout }) {
  const timeoutRef = useRef(null); // 인스턴스마다 자기 { current }

  return <button onClick={() => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClick, timeout);
  }}>...</button>;
}
```

각 버튼이 자기 ref를 가져 격리 회복. 화면 영향 없으니 state 아님 정당화.

---

<!-- beat: b5 -->
<!-- _footer: "LO-S1.4 · LO-S1.5" -->

## 진단 퀴즈 — 한 줄로 답해보기

- (a) `return <span>{positionRef.current.x}</span>` (마우스 위치 표시)
- (b) `if (modeRef.current === 'dark') return <Dark/>` (렌더 분기)
- (c) 모듈 전역 `let activeTimer;`로 여러 카드의 자동 닫힘 관리

처방
- (a) stale 표시 → **state로**
- (b) 비결정적 렌더 → **state로**
- (c) 인스턴스 충돌 → **useRef로**

---

<!-- beat: b6 -->
<!-- _footer: "LO-S1.4 · LO-S1.5" -->

## Recap

- 렌더 결과·렌더 분기에 `ref.current` → stale·비결정적
- 전역 변수 → `useRef` 리팩터링은 인스턴스별 격리 표준 처방
- 다음 섹션 (S2) — 같은 ref를 **DOM 노드**에 붙여 focus·scroll
