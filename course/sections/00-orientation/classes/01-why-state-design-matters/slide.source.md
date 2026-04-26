---
marp: true
theme: default
paginate: true
footer: "LO-S0.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  .small { font-size: 22px; color: #555; }
---

<!-- beat: b1 -->

# 왜 state 설계가 따로 필요한가

## 4가지 통증 진단

<span class="small">React 중급자가 매일 부딪히는 state의 정체</span>

---

<!-- beat: b1 -->
<!-- _footer: "LO-S0.1" -->

## 익숙한 useState, 그런데 왜 꼬일까

- `useState`는 손에 익었는데, 앱이 커지면 state가 자꾸 꼬인다
- 어제 잘 돌던 화면이 prop 하나 추가하니 동기화가 깨진 경험, 익숙하시죠?
- 이 강의는 **'useState 사용법'이 아니라 'state 설계'** 를 다룹니다
- 오늘의 약속: 4가지 통증을 진단하고, 강의 전체의 출발점을 한 문장으로 잡기

---

<!-- beat: b2 -->
<!-- _footer: "LO-S0.1" -->

## 통증 #1·#2 — 중복과 동기화 버그

- **중복(redundancy)**: 같은 정보를 여러 state에 복제 → 한쪽만 갱신되며 모순 발생
- **동기화 버그**: props 값을 `useState` 초기값으로 mirror → prop이 바뀌어도 화면이 안 따라옴
- 두 통증 모두 "한 진실을 두 곳에 둔" 결과 — **single source of truth 부재**
- 이건 코딩 실수가 아니라 **state 구조 결정의 문제**

---

<!-- beat: b3 -->
<!-- _footer: "LO-S0.1" -->

## 통증 #3·#4 — Drilling과 의도치 않은 리셋

- **prop drilling**: 깊은 트리에 데이터 전달 → 중간 컴포넌트가 무관한 prop만 통과시킴
- **의도치 않은 리셋**: 조건부 렌더·타입 교체로 화면은 같은데 input 값이 사라짐
- 공통점: **React가 state를 트리 어디에 묶는지** 모르면 추적 불가
- 4가지 통증은 우연이 아니라 **구조 미설계**에서 반복 재생산된다

---

<!-- beat: b4 -->
<!-- _footer: "LO-S0.3" -->

## 한 화면에서 통증이 동시에 터진다

```tsx
// 잘못된 설계 — 4 boolean이 모순 상태를 허용
const [isLoading, setIsLoading] = useState(false);
const [isError, setIsError] = useState(false);
const [isSuccess, setIsSuccess] = useState(false);
const [isEmpty, setIsEmpty] = useState(false);
// (true, true, …) 같은 불가능한 조합이 가능해짐

// 선언형으로 정리 — status enum 한 줄
type Status = 'idle' | 'loading' | 'success' | 'error';
const [status, setStatus] = useState<Status>('idle');
```

---

<!-- beat: b5 -->
<!-- _footer: "LO-S0.3" -->

## 강의 전체의 출발선 한 문장

# 상태 → UI 자동 반영

- **명령형**: "이벤트가 일어나면 DOM을 이렇게 바꿔라" — 단계를 코드가 직접 지시
- **선언형**: "지금 상태가 X이면 UI는 Y이다" — React가 알아서 그려줌
- 이 명제 하나가 앞으로 7개 챕터(구조·lifting·key·reducer·context)를 관통하는 척도

---

<!-- beat: b7 -->
<!-- _footer: "LO-S0.1" -->

## 오늘 못 박은 3가지

- ① state 통증은 **4가지 패턴**(중복 / 동기화 / drilling / 리셋)으로 반복된다
- ② 통증의 뿌리는 잘못된 코드가 아니라 **state 구조 결정 부재**다
- ③ 강의 전체의 척도는 한 문장 — **"상태 → UI 자동 반영"**
- 다음 class: 7개 챕터가 어떤 통증을 푸는지 **코스 맵**으로 본다
