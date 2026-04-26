# 왜 state 설계가 따로 필요한가 — 4가지 통증 진단

> LOs: LO-S0.1, LO-S0.3

## 개요
`useState`는 손에 익었는데, 앱이 커질수록 state가 자꾸 꼬이는 경험 한 번쯤 있죠? 어제 잘 돌던 화면이 오늘 prop 하나 추가하니까 동기화가 깨지고, 어떤 input은 탭만 바꾸면 멋대로 리셋됩니다 [slide 1]. 이 강의는 `useState` **사용법**이 아니라 **state 설계**를 다룹니다. 오늘 수업에서는 중급 개발자가 반복해서 부딪히는 4가지 통증의 정체를 진단하고, 강의 전체를 관통할 한 문장의 출발선을 세웁니다.

## 핵심 개념
state 통증은 우연히 발생하는 게 아니라, **state 구조 결정의 부재**에서 같은 패턴으로 재생산됩니다 [slide 2]. 4가지로 정리해 봅시다.

- **통증 #1 — 중복(redundancy):** 같은 정보를 여러 state에 복제해 두면 한쪽만 갱신되며 모순이 생깁니다. 단일 출처(single source of truth)가 무너진 상태입니다 [slide 3].
- **통증 #2 — 동기화 버그:** props로 받은 값을 `useState` 초기값으로 mirror 하는 안티패턴. prop이 바뀌어도 화면이 안 따라옵니다. #1과 뿌리가 같습니다 — "한 진실을 두 곳에 둔" 결과죠.
- **통증 #3 — prop drilling:** 깊은 트리에 데이터를 넘기느라 중간 컴포넌트가 자기와 무관한 prop을 그저 통과시키기만 합니다 [slide 4].
- **통증 #4 — 의도치 않은 리셋:** 조건부 렌더나 컴포넌트 타입 교체로 화면은 같아 보이는데 input 값이 갑자기 사라집니다. React가 state를 트리 위치에 묶는다는 모델을 모르면 추적이 불가능해요.

이 4가지 통증을 "내가 잘못 코딩했나" 하고 자책하기 전에, **구조 결정 단계에서 이미 어긋났다**는 시선으로 바꾸는 것이 오늘의 핵심입니다.

## 예시
폼 컴포넌트에 `isLoading`, `isError`, `isSuccess`, `isEmpty` 4개 boolean을 따로 두면 어떻게 될까요? [slide 5]

```tsx
// 통증 #1·#2가 동시에 터지는 전형
const [isLoading, setLoading] = useState(false);
const [isError, setError] = useState(false);
const [isSuccess, setSuccess] = useState(false);
const [isEmpty, setEmpty] = useState(false);
// 가능한 조합 2^4 = 16개. 그중 의미 있는 건 4개 정도.
// (isLoading=true, isSuccess=true) 같은 모순이 코드 어딘가에서 슬쩍 생김
```

선언형 사고로 바꾸면 한 줄로 정리됩니다.

```tsx
type Status = "idle" | "loading" | "success" | "error";
const [status, setStatus] = useState<Status>("idle");
```

상태 공간이 4개로 줄고, 모순 조합 자체가 타입 시스템에서 사라집니다. 이게 다음 챕터 [S1.C1]의 예고편입니다.

## 흔한 실수
- "useState를 더 잘 쓰면 된다"고 오해하는 것. 통증은 훅 사용법이 아니라 **state 모양** 문제입니다. 같은 boolean 4개를 `useReducer`로 옮겨도 모순 조합은 그대로 남습니다.
- props를 `useState` 초기값으로 받아두는 mirroring 패턴 [slide 6]. 처음 한 번만 동작하고 그다음부터는 prop과 state가 따로 놉니다 — 동기화 버그의 단골 출처죠.

## 복습
오늘 못 박은 3가지 [slide 7]: ① state 통증은 중복·동기화·drilling·리셋 4가지 패턴으로 반복된다, ② 뿌리는 코드가 아니라 **구조 미설계**다, ③ 강의 전체의 척도는 한 문장 — **"상태 → UI 자동 반영"**(선언형 UI). 이 명제 하나가 앞으로 7개 챕터를 관통합니다. 다음 class [S0.C2]에서는 7개 챕터가 어떤 통증을 어디서 푸는지 한 장의 지도로 봅니다.
