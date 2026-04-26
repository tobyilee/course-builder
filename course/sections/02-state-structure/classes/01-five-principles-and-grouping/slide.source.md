---
marp: true
theme: default
paginate: true
footer: "LO-S2.1"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
---

<!-- beat: b1 -->

# 5원칙 한눈에

## 관련 state 묶기 · 모순 회피

LO-S2.1 / LO-S2.2

---

<!-- beat: b1 -->
<!-- _footer: "LO-S2.1" -->

## 그 버그, 로직이 아니라 구조 문제예요

- `useState` 두 개 따로 두니 한쪽만 갱신되어 UI가 어긋남
- `isSending=true` 와 `isSent=true` 가 동시에 켜지는 순간 발생
- 버그의 80%는 로직이 아니라 state **구조**에서 비롯된다
- 오늘은 그 구조를 다듬는 5원칙을 펼쳐 봅시다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.1" -->

## state 구조 설계 5원칙

1. 관련 state **묶기** — 항상 함께 변하면 객체로
2. **모순** 회피 — impossible state를 만들지 않기
3. **redundant** state 제거 — 계산 가능한 값은 derive
4. **duplication** 회피 — 같은 데이터는 한 곳에만
5. deep nesting **평탄화** — 트리는 정규화

> "Make your state as simple as it can be — but no simpler."

오늘은 ①·②, 다음 class에서 ③·④·⑤

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.2" -->

## 원칙 ① 관련 state는 묶기 — MovingDot

```jsx
// before — x, y가 항상 함께 갱신
const [x, setX] = useState(0);
const [y, setY] = useState(0);

// after — 하나의 객체로 묶기
const [position, setPosition] = useState({ x: 0, y: 0 });
setPosition({ ...position, x: 100 }); // 스프레드 비용 감수
```

판단 기준: **한 변수만 바뀌는 경우가 실제로 존재하는가?** 없으면 묶는다. 동적 키 컬렉션이면 객체 대신 Map/배열을 고려.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.2" -->

## 원칙 ② 모순 회피 — status enum으로 단일화

```jsx
// before — 두 boolean = 4조합, 그중 1개는 impossible
const [isSending, setIsSending] = useState(false);
const [isSent, setIsSent]       = useState(false);

// after — status 하나로, derive로 표현
const [status, setStatus] = useState('typing');
// 'typing' | 'sending' | 'sent'
const isSending = status === 'sending';
const isSent    = status === 'sent';
```

두 변수가 항상 함께 변한다 → 사실은 **한 변수의 다른 표현**

---

<!-- beat: b5 -->
<!-- _footer: "LO-S2.2" -->

## FeedbackForm 리팩터 — 컴파일 타임 보장

```jsx
async function handleSubmit(e) {
  e.preventDefault();
  setStatus('sending');
  await sendMessage(text);
  setStatus('sent');
}
// JSX는 derive 변수 그대로 사용 — 마크업 변경 최소
if (isSent) return <h1>Thanks!</h1>;
return (
  <form onSubmit={handleSubmit}>
    <textarea disabled={isSending} />
    <button disabled={isSending}>Send</button>
  </form>
);
```

`'sending' && 'sent'` 동시 상태는 **타입 시스템상 불가능**

---

<!-- beat: b6 -->
<!-- _footer: "LO-S2.2" -->

## 잠깐 자가 진단

- Q1. `useState({ x, y })` 대신 두 useState로 둬도 되는 경우는?
  - 가로 스크롤처럼 **x만** 바뀌는 시나리오가 따로 있다면 분리가 더 정확
- Q2. 폼에 `isLoading / isError / isSuccess` 가 있다면 status enum 후보 값은?
  - `'idle' | 'loading' | 'error' | 'success'` — 4값
  - boolean 3개의 8조합 중 합법은 4개뿐

---

<!-- beat: b7 -->
<!-- _footer: "LO-S2.1" -->

## Recap — 오늘의 두 원칙

- 5원칙은 결국 **"동기화 버그를 어떻게 차단할까?"** 한 질문
- 함께 변하는 변수는 **묶고**, 모순 가능한 boolean 쌍은 **enum으로 단일화**
- 다음 class: redundant state 제거 + props mirroring 안티패턴
