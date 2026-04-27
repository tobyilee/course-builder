---
marp: true
theme: default
paginate: true
footer: "LO-S2.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 20px; }
---

<!-- beat: b1 -->

# ref={...}로 DOM 만지기

focus · scroll · measure · play

선언형으로 표현 안 되는 명령형 작업

---

<!-- beat: b1 -->
<!-- _footer: "LO-S2.1" -->

## React만으로는 안 되는 순간

- 검색창에 자동으로 커서를 넣고 싶다
- 리스트의 새 항목까지 부드럽게 스크롤
- video.play() / pause() · getBoundingClientRect()
- 모두 브라우저의 명령형 DOM API가 필요
- React가 남겨둔 escape hatch — `ref={...}`

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.1" -->

## 기본 패턴 — useRef + ref 부착

```jsx
import { useRef } from 'react';

function SearchBox() {
  const inputRef = useRef(null);
  // commit 후 inputRef.current = <input> DOM
  return <input ref={inputRef} />;
}
```

JSX의 `ref={inputRef}` → React가 commit phase에 `inputRef.current`에 노드를 주입.

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.2" -->

## 타이밍 — render에는 null, commit 이후 채워짐

- **render phase**: 컴포넌트 함수가 호출되는 시점, `ref.current === null`
- **commit phase**: React가 DOM 변경 후 `ref.current = node` 주입
- 업데이트 시: 노드 교체 직전 null → 직후 재설정
- 안전한 읽기 위치: **이벤트 핸들러** 또는 **Effect 안**
- 렌더 본문에서 `ref.current` 만지면 null 또는 옛 노드를 본다

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.1" -->

## 예제 — focus / scroll / play

```jsx
// 1) 버튼 클릭으로 input에 포커스
<button onClick={() => inputRef.current.focus()}>Focus</button>

// 2) 카드를 부드럽게 화면에 가져오기
cardRef.current.scrollIntoView({
  behavior: 'smooth', block: 'nearest'
});

// 3) 상태에 따라 비디오 제어
useEffect(() => {
  isPlaying ? videoRef.current.play() : videoRef.current.pause();
}, [isPlaying]);
```

공통점: 전부 **이벤트 핸들러나 Effect 안**에서 접근.

---

<!-- beat: b5 -->
<!-- _footer: "LO-S2.2" -->

## 자기점검 — 어디서 ref를 읽었나

```jsx
// ❌ render 본문 — ref.current는 아직 null
function X() {
  const ref = useRef(null);
  console.log(ref.current); // null
  return <div ref={ref} />;
}

// ✅ Effect 안 — commit 이후
useEffect(() => { console.log(ref.current); }, []);
```

질문: "내가 ref를 읽는 위치는 commit 이후인가?"

---

<!-- beat: b6 -->
<!-- _footer: "LO-S2.1" -->

## 정리 — 다음 시간 예고

- `useRef` + `ref={...}`로 DOM 노드를 잡고 명령형 API 호출
- 타이밍: render에는 null → commit 이후 핸들러/Effect에서 안전하게 읽기
- ref는 'React가 못 하는 일'을 위한 escape hatch
- 다음 시간: setState 직후 새 DOM을 즉시 측정해야 할 때 — **flushSync**, 그리고 직접 DOM 조작이 위험한 이유
