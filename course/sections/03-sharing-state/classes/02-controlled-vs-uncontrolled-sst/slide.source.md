---
marp: true
theme: default
paginate: true
footer: "LO-S3.2"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  table { font-size: 22px; }
  th, td { padding: 6px 10px; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
---

<!-- beat: b1 -->

# Controlled vs Uncontrolled

### Single Source of Truth로 위치 결정하기

S3.C2 · 12분 · LO-S3.2 / LO-S3.3

---

<!-- beat: b1 -->

## 같은 컴포넌트, 두 얼굴

- C1에서 lift 한 뒤 Panel은 **자기 상태가 없다** — 이게 controlled
- 같은 Panel이라도 state 위치에 따라 협조 능력이 완전히 달라짐
- 모두 controlled로 만들면 될까? 아니면 어떤 기준으로?
- 오늘 — 두 스타일 트레이드오프 + state 위치 결정 사고법

---

<!-- beat: b2 -->

## 두 스타일의 정체

<div class="two-col">

**Uncontrolled**

```jsx
function Panel({ title, children }) {
  const [isActive, setIsActive] =
    useState(false);
  // 부모는 영향 못 줌
  // 드롭인 사용 편함
}
```

**Controlled**

```jsx
function Panel({
  title, children,
  isActive, onShow
}) {
  // state 없음
  // 부모가 완전히 통제
  // 부모가 props 책임짐
}
```

</div>

> 식별법: **같은 정보가 props로 오는가, useState로 보유하는가?**

---

<!-- beat: b3 -->

## 3축 비교 매트릭스

| 축 | Uncontrolled | Controlled |
|---|---|---|
| **상태 위치** | 자식 내부 `useState` | 부모 `props` |
| **부모 영향** | 없음 | 완전 통제 |
| **사용 편의** | 부모 설정 적음, 협조 어려움 | 부모가 모든 props 제공해야 |

> 선택 기준 한 줄 — **다른 컴포넌트와 협조해야 하나?**
> Yes → controlled · No → uncontrolled 유지
> 실전은 대부분 **부분 controlled** (둘이 섞임)

---

<!-- beat: b4 -->
<!-- _footer: "LO-S3.3" -->

## Single Source of Truth

- 각 state는 **단 하나의 컴포넌트가 소유**
- 공유 필요해지는 순간 → 가장 가까운 공통 부모로 lift
- 정적 원칙 아님 — 요구사항 바뀌면 state는 위/아래로 자유 이동

**결정 알고리즘 3단계**

1. 이 state를 **누가 읽는가** 나열
2. 그들의 **가장 가까운 공통 조상**을 찾는다
3. 거기에 state 배치

---

<!-- beat: b5 -->
<!-- _footer: "LO-S3.3" -->

## 두 시나리오로 확인

**Synced Inputs** — 두 Input이 같은 값
```jsx
const [text, setText] = useState('');
<Input value={text} onChange={e => setText(e.target.value)} />
<Input value={text} onChange={e => setText(e.target.value)} />
```

**Filterable List** — 검색바 + 결과 목록
```jsx
const [query, setQuery] = useState('');
const results = filterItems(foods, query); // derive!
```

> `results`는 state 아님 — `query`로부터 매번 계산 (S2 redundant 회수).

---

<!-- beat: b6 -->

## Practice — 장바구니 시나리오

`ProductCard`의 "담기" 버튼이 `CartBadge` 숫자를 올려야 한다.

**자문자답 체크리스트**

1. `cartCount`를 **누가 읽는가**? — Card(쓰기), Badge(읽기)
2. **가장 가까운 공통 부모**는? — 두 컴포넌트를 함께 렌더하는 페이지
3. 둘 중 어느 자식이 controlled가 되나? — **둘 다** controlled
4. Card가 자체 `useState`를 갖고 있다면 어떤 버그? — Badge와 동기화 안됨 (redundant)

---

<!-- beat: b7 -->

## Recap — 두 원칙 한 장에

- **Controlled** = 부모 props 주도 · **Uncontrolled** = 자식 내부 state
- 협조 필요 → controlled로, state는 가장 가까운 공통 부모로 lift
- **Single Source of Truth** — 각 state는 단 하나의 소유자
- 결정 알고리즘: 누가 읽나 → 공통 조상 → 거기에 배치
- 다음(C3): Accordion · Synced Inputs · Filterable List 직접 구현
