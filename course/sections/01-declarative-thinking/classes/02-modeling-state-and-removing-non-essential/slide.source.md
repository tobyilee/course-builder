---
marp: true
theme: default
paginate: true
footer: "LO-S1.2"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 18px; }
  pre { line-height: 1.35; }
  table { font-size: 22px; }
  th, td { padding: 6px 10px; }
  .bad { color: #c0392b; font-weight: bold; }
  .good { color: #1e8449; font-weight: bold; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
---

<!-- beat: b1 -->

# useState로 모델링하고
# 비핵심 state 제거하기

### boolean paradox에서 status enum으로

S1.C2 · 12분 · LO-S1.2 + LO-S1.4

---

<!-- beat: b1 -->
<!-- _footer: "LO-S1.2" -->

## 7개 boolean — 어디가 함정일까

```js
const [isEmpty,      setIsEmpty]      = useState(true);
const [isTyping,     setIsTyping]     = useState(false);
const [isSubmitting, setIsSubmitting] = useState(false);
const [isSuccess,    setIsSuccess]    = useState(false);
const [isError,      setIsError]      = useState(false);
```

- `isTyping=true` 이면서 `isSuccess=true` 가 동시에? → **paradox**
- 실전 버그: 에러 후 `isSubmitting=false` 잊으면 spinner + 에러 동시 노출
- 질문: 모순이 **원천적으로 불가능한** 모양은?

---

<!-- beat: b2 -->
<!-- _footer: "LO-S1.2" -->

## 비핵심 state 제거 — 3대 질문

| # | 질문 | 처방 |
|---|---|---|
| ① | **모순(paradox)** 을 만드나? | 상호배타 boolean → status enum |
| ② | 다른 변수에서 **같은 정보** ? | 중복 제거 (렌더 시 계산) |
| ③ | 다른 변수의 **역** 인가? | 역수 제거 (렌더 시 계산) |

선언형 5단계 중 **③ useState 모델링 → ④ 비핵심 제거** 단계.

---

<!-- beat: b2 -->
<!-- _footer: "LO-S1.4" -->

## state vs 파생값 — 분류 기준

- **state 변수** = 사용자/시간이 바꾸는 **진짜 입력값**
  - 예: `answer`, `error`, `status`
- **파생값 (computed at render)** = 다른 state로부터 매 렌더 계산
  - 예: `isEmpty = answer.length === 0`
  - 예: `isError = error !== null`

> 파생값을 useState로 두면 곧 **동기화 버그의 원천**.

---

<!-- beat: b3 -->
<!-- _footer: "LO-S1.2" -->

## Before — 7개 boolean

```jsx
const [answer,       setAnswer]       = useState('');
const [error,        setError]        = useState(null);
const [isEmpty,      setIsEmpty]      = useState(true);
const [isTyping,     setIsTyping]     = useState(false);
const [isSubmitting, setIsSubmitting] = useState(false);
const [isSuccess,    setIsSuccess]    = useState(false);
const [isError,      setIsError]      = useState(false);
```

7개 변수 = **2⁷ = 128가지 조합** — 그중 유효한 건 5개뿐.

---

<!-- beat: b3 -->
<!-- _footer: "LO-S1.2" -->

## After — 3개 변수

```jsx
const [answer, setAnswer] = useState('');
const [error,  setError]  = useState(null);
const [status, setStatus] = useState('typing');
// 'typing' | 'submitting' | 'success'

// 파생값 (state 아님)
const isEmpty = answer.length === 0;
const isError = error !== null;
```

- ① 4개 boolean → **status enum** 으로 합침
- ② `isEmpty` 제거 (계산)
- ③ `isError` 제거 (계산)

> 진짜 이득: 존재 불가능한 상태가 **타입상 만들어지지 않는다**.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S1.4" -->

## Practice — 6개 boolean을 줄이세요

```js
isLoggedIn, isLoading, isLoadingProfile,
hasProfileError, profileLoaded, isLoggedOut
```

- 힌트 1: **항상 정반대**인 두 변수는? → 질문 ③
- 힌트 2: 동시에 true면 **paradox**인 것은? → 질문 ①

> 잠시 멈추고 직접 작성해 보세요.

정답 예시 (다음 슬라이드).

---

<!-- beat: b4 -->
<!-- _footer: "LO-S1.4" -->

## Practice — 정답 예시

```ts
const [status, setStatus] = useState<
  'logged-out' | 'loading' | 'ready' | 'error'
>('logged-out');
const [profile, setProfile] = useState<User | null>(null);

// 나머지는 모두 파생값
const isLoggedIn       = status !== 'logged-out';
const isLoading        = status === 'loading';
const hasProfileError  = status === 'error';
```

state는 **2개**, 나머지는 매 렌더 계산.

---

<!-- beat: b5 -->
<!-- _footer: "LO-S1.2" -->

## Recap — state는 최소, 파생은 계산

1. **3대 질문** (모순 / 중복 / 역수) 으로 비핵심을 걸러낸다
2. 파생값은 useState 가 아니라 **render 시 계산**
3. **status enum** 은 존재 불가능한 상태를 타입 차원에서 차단

> 다음(C3): 마지막 5단계 — 핸들러로 트리거 표를 코드로 옮긴다.
