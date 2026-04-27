---
marp: true
theme: default
paginate: true
footer: "LO-S4.2"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  blockquote { color: #555; border-left: 4px solid #888; }
---

<!-- beat: b1 -->

# 한 줄이면 끝나는데, 왜 두 번 렌더할까

### Derived state — render 중 계산과 useMemo

`firstName + lastName`을 위해 `useState + useEffect`를 쓰는 흔한 코드.

> 한 번의 입력에 **렌더 → Effect → setState → 재렌더** 4단계가 펼쳐진다.

---

<!-- beat: b2 -->
<!-- _footer: "LO-S4.2" -->

## 안티패턴 #1 — props/state 파생값을 state로 보관

- 증상: `useState(fullName)` + `useEffect(() => setFullName(...))`
- 원인: "값이 바뀔 때 동기화해야지" 라는 라이프사이클 사고
- 정정 원칙: **render는 순수 함수** — 같은 입력이면 매번 같은 출력
  → 그냥 `const`로 계산하면 자동으로 일관성 유지
- 옮기지 말아야 할 비용: 추가 렌더 1회 + dev 더블 호출 + deps 부담

---

<!-- beat: b3 -->
<!-- _footer: "LO-S4.2" -->

## Before / After — fullName 한 줄로

```tsx
// Before — 5줄, 추가 렌더 1회
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);

// After — 1줄, 추가 렌더 0회
const fullName = firstName + ' ' + lastName;
```

> 단계: `useState` 제거 → `useEffect` 제거 → `const` 한 줄.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S4.2" -->

## 안티패턴 #2 — 비싼 계산을 Effect로 캐싱

- 증상: `useEffect(() => setVisible(getFiltered(todos, filter)), [...])`
- 정정 원칙: 비싼 계산도 **render 중에**, 단 `useMemo`로 메모이즈
- `useMemo` 적용 3조건
  - 계산이 진짜 비싸다 (수백 ms 이상)
  - 의존성이 안정적
  - 참조 일관성이 필요한 하위 트리가 있다
- 측정 후 결정: `console.time` · React Profiler

---

<!-- beat: b5 -->
<!-- _footer: "LO-S4.2" -->

## Before / After — getFilteredTodos

```tsx
// Before — Effect + state, 매번 추가 렌더
const [visible, setVisible] = useState([]);
useEffect(() => {
  setVisible(getFilteredTodos(todos, filter));
}, [todos, filter]);

// After — useMemo, deps 변경 시에만 재계산
const visible = useMemo(
  () => getFilteredTodos(todos, filter),
  [todos, filter]
);
```

> 1만 개 todo에서 `console.time` 차이를 직접 확인해보자.

---

<!-- beat: b6 -->
<!-- _footer: "LO-S4.2" -->

## React Compiler — 자동 메모이즈 시대

- 트렌드: React Compiler가 메모이즈를 자동화 → `useMemo` 코드량 감소
- 그러나 **1차 원칙은 동일**: *"Effect로 옮기지 말고 render 중에 계산하라"*
- 지금 시점 가이드
  - 비싸지 않으면 `const` 한 줄
  - 비싸면 `useMemo` (Compiler가 들어와도 큰 손해 없음)
  - 절대 Effect + state로 옮기지 말 것

---

<!-- beat: b7 -->
<!-- _footer: "LO-S4.2" -->

## 잠깐 — 이건 어떻게 풀까?

- **Q1**. 장바구니 합계 = `items.reduce((s, i) => s + i.price, 0)`
  → 100개 이하면 한 줄, 1만 개면 `useMemo` 검토
- **Q2**. 검색어 글자 수 = `query.length`
  → 의심의 여지 없이 한 줄
- 결정 기준 한 문장: *"진짜 비싼가? 측정했나?"*

---

<!-- beat: b8 -->
<!-- _footer: "LO-S4.2" -->

## 정리 — Q1·Q2 가지 채우기

- **props/state 파생값** → render 중 계산이 1차 답
- **비싸면** `useMemo`, 비싸지 않으면 그냥 `const`
- **Effect + state** 로 옮기는 순간 추가 렌더 + 동기화 부담
- 다음: prop 변경 시 state를 리셋·조정하는 가지로 (Q4)
