---
marp: true
theme: default
paginate: true
footer: "LO-S2.5"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 20px; }
---

<!-- beat: b1 -->

# 자식에게 ref 넘기기

forwardRef → React 19 ref-as-prop
그리고 useImperativeHandle

---

<!-- beat: b1 -->
<!-- _footer: "LO-S2.5" -->

## `<MyInput ref={...} />`가 그냥 안 되는 이유

- 디자인 시스템의 `<MyInput />`에 부모가 ref를 꽂아 focus 부르고 싶다
- 그런데 ref는 **prop이 아니다** — 컴포넌트 함수의 인자로 자동 전달되지 않음
- 해결 경로 3가지를 본다
  - React 18까지의 `forwardRef`
  - React 19의 ref-as-prop
  - `useImperativeHandle`로 노출 API 좁히기

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.5" -->

## React 18까지 — forwardRef로 명시 노출

```jsx
import { forwardRef } from 'react';

const MyInput = forwardRef(function MyInput(props, ref) {
  return <input ref={ref} {...props} />;
});

// 부모
const inputRef = useRef(null);
<MyInput ref={inputRef} />
```

- 시그니처가 `(props, ref)` 두 인자로 바뀌는 게 핵심
- 디자인 시스템 전반에 깔리던 보일러플레이트

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.5" -->

## React 19 — ref가 그냥 prop

```jsx
function MyInput({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}

function MyForm() {
  const inputRef = useRef(null);
  return <MyInput ref={inputRef} />;
}
```

- `forwardRef` 래핑 불필요 → boilerplate 제거
- 마이그레이션은 codemod로 점진 전환
- 라이브러리 호환성 위해 두 패턴은 한동안 공존

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.5" -->

## useImperativeHandle — 노출 API 좁히기

```jsx
function MyInput({ ref }) {
  const realInputRef = useRef(null);
  useImperativeHandle(ref, () => ({
    focus() { realInputRef.current.focus(); }
  }));
  return <input ref={realInputRef} />;
}
// 부모는 .focus()만 호출 가능 — .value · .blur() 차단
```

- ref를 그냥 노출하면 input의 **모든 API**가 새어 나간다
- facade를 직접 설계해 명령형 표면을 의도적으로 좁힌다

---

<!-- beat: b5 -->
<!-- _footer: "LO-S2.5" -->

## 자문자답 — 어떤 도구를 골라야 하나

- React 19 새 프로젝트? → **ref-as-prop**으로 충분, forwardRef 도입 X
- React 18 사용자도 지원하는 라이브러리? → **forwardRef 유지** (호환성 우선)
- `<Modal>`이 부모에 `open()/close()`만 노출? → **useImperativeHandle**로 facade
- 모든 자식에 `useImperativeHandle`? → ❌ 캡슐화가 진짜 깨질 때만

---

<!-- beat: b6 -->
<!-- _footer: "LO-S2.5" -->

## 정리 — S2 마무리 & 다음 섹션 예고

- ref는 자동 prop이 아니다 — 18은 `forwardRef`, 19는 ref-as-prop
- `useImperativeHandle`로 자식이 노출하는 명령형 API를 의도적으로 좁힌다
- S2 종합: ref는 **마지막 수단** — 타이밍과 노출 표면을 설계하라
- 다음 섹션: 또 다른 escape hatch — **Effect로 외부 시스템과 동기화**
