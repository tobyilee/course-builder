---
marp: true
theme: default
paginate: true
footer: "LO-S4.4 · LO-S4.2"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 22px; }
---

<!-- beat: b1 -->

# 두 가지 함정

JSX 위치 ≠ 트리 위치 · 컴포넌트 정의 중첩 금지

S4 · Class 3

---

<!-- beat: b1 -->

## 결과를 예측해 보자

- 코드 A — `if` 분기로 JSX를 **따로** 적었다. state가 사라질까?
- 코드 B — 컴포넌트 안에 컴포넌트를 정의했다. 입력은 잘 될까?
- 둘 다 직관과 다르게 동작한다
- 그 이유는 결국 한 가지 규칙 — **트리 위치**

---

<!-- beat: b2 -->
<!-- _footer: "LO-S4.2" -->

## 함정 1 — JSX 위치는 기준이 아니다

- 코드의 **줄 위치**(JSX 위치)와 **렌더된 슬롯**(트리 위치)은 다르다
- if 분기로 두 군데에 `<Counter/>`를 적어도, React는 "부모의 첫 자식"으로 같은 위치라 본다
- 기준은 코드 위치가 아니라 **리턴된 트리에서 부모의 몇 번째 자식인가**
- 모르면 "코드를 분리했는데 왜 보존되지?" 미궁에 빠진다

---

<!-- beat: b3 -->
<!-- _footer: "LO-S4.2" -->

## 함정 1 코드 — 의도치 않은 보존

```jsx
if (isFancy) {
  return <div><Counter isFancy={true} /></div>;
} else {
  return <div><Counter isFancy={false} /></div>;
}
```

- 둘 다 **div의 첫 자식 = Counter** — 트리상 같은 위치/같은 타입
- 결과 — 토글해도 score 보존 (의도가 리셋이었다면 버그)
- 고치려면 — `key` 부여하거나 다른 부모 슬롯으로 분리
- 교훈 — "코드가 갈라졌다"가 아니라 **리턴된 트리**를 머릿속에 그려라

---

<!-- beat: b4 -->
<!-- _footer: "LO-S4.4" -->

## 함정 2 — 컴포넌트 정의를 안에 두지 말 것

- 컴포넌트 함수 본문 **안에** 또 다른 컴포넌트를 정의하지 말 것
- 부모가 렌더될 때마다 자식 컴포넌트가 **새 함수 객체**로 다시 생성
- React 입장에선 매 렌더마다 타입이 바뀐 셈 → 같은 위치 + 다른 타입 → **리셋**
- 증상 — "한 글자 칠 때마다 input이 비워짐" 같은 미스터리 버그

---

<!-- beat: b5 -->
<!-- _footer: "LO-S4.4" -->

## 함정 2 리팩터링 — top-level로 빼라

```jsx
// 안티패턴
function MyComponent() {
  function MyTextField() {
    const [text, setText] = useState('');
    return <input value={text} onChange={e=>setText(e.target.value)} />;
  }
  return <MyTextField />;
}

// 리팩터링 — top-level로 이동
function MyTextField() { /* 동일 본문 */ }
function MyComponent() { return <MyTextField />; }
```

- 필요한 데이터는 props로 전달 — 안에 둘 이유는 거의 없다
- 리뷰 룰 — "이 함수 안에 다른 컴포넌트 정의가 있는가?"

---

<!-- beat: b6 -->
<!-- _footer: "LO-S4.4 · LO-S4.2" -->

## 미니 연습 — 코드 리뷰

- "props를 클로저로 캡처하려고 컴포넌트를 안에 정의했다"는 동료 코드를 봤다
- 정답 — top-level로 빼고 데이터를 props로 넘기면 끝
- 두 함정 모두 머릿속에서 **트리 그림**으로 재현해 보기
- 공통 진단 도구 — "리턴된 트리에서 위치와 타입을 보라"

---

<!-- beat: b7 -->
<!-- _footer: "LO-S4.4 · LO-S4.2" -->

## S4 마무리 — 위치 · 타입 · key

- JSX의 코드 위치가 아니라 **리턴된 트리의 위치**가 기준이다
- 컴포넌트 정의는 항상 **top-level**에 둔다
- S4 도구 세 가지 — **위치 · 타입 · key**로 보존/리셋 100% 통제
