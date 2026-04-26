---
marp: true
theme: default
paginate: true
footer: "LO-S3.4"
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

# 케이스 스터디 3종

### Accordion · Synced Inputs · Filterable List

S3.C3 · 11분 · LO-S3.4

---

<!-- beat: b1 -->

## 오늘 적용할 표준 패턴 3개

- 지금까지의 **3단계 절차 + SST 원칙** 을 실전 패턴에 적용
- 면접·실무에서 반복적으로 등장하는 표준 템플릿
- **공통 모양** — 부모가 state 보유, 자식들에 (값, 핸들러) props
- 마치고 나면 lifting state up이 **어떤 모양으로 코드에 나타나는가**가 손에 익는다

---

<!-- beat: b2 -->

## Case 1 — Almaty Accordion

```jsx
function Accordion() {
  const [activeIndex, setActiveIndex] = useState(0);
  return (
    <>
      <Panel title="About"
        isActive={activeIndex === 0}
        onShow={() => setActiveIndex(0)}>...</Panel>
      <Panel title="Etymology"
        isActive={activeIndex === 1}
        onShow={() => setActiveIndex(1)}>...</Panel>
    </>
  );
}
```

> "한 번에 하나" 제약 = **state 변수 하나만** 갖는다 (모순/redundant 회피)

---

<!-- beat: b3 -->

## Case 2 — Synced Inputs

```jsx
const [text, setText] = useState('');

<Input
  value={text}
  onChange={e => setText(e.target.value)}
/>
<Input
  value={text}
  onChange={e => setText(e.target.value)}
/>
```

- 부모에 `text` state **하나**만 — 두 Input이 동일하게 props 받음
- SST의 가장 단순한 시각화 — **같은 값을 두 번 저장하지 마라**
- 자체 state를 가졌다면 첫 입력에 한쪽만 바뀜 (S2의 duplication 안티패턴)

---

<!-- beat: b4 -->

## Case 3 — Filterable List

```jsx
function FilterableList() {
  const [query, setQuery] = useState('');
  const results = filterItems(foods, query); // derive
  return (
    <>
      <SearchBar query={query}
        onChange={e => setQuery(e.target.value)} />
      <List items={results} />
    </>
  );
}
```

- `query`는 SearchBar(쓰기)·List(읽기) 공통 부모에 — `FilterableList`
- `results`는 state가 아니라 `query`로부터 **derive** — 부모에서 자연 계산

---

<!-- beat: b5 -->

## 세 패턴의 공통 모양

| 패턴 | 부모 state | 자식 props |
|---|---|---|
| **Accordion** | `activeIndex` | `isActive`, `onShow` |
| **Synced Inputs** | `text` | `value`, `onChange` |
| **Filterable List** | `query` | `query`/`onChange`, `items` |

> 모두 **부모 state 1개 + 자식들에 (값, 핸들러) 쌍 props**
> 새 컴포넌트 설계도 같은 틀로 시작 가능

---

<!-- beat: b6 -->

## Practice — Tabs UI 3개

탭 3개. 한 번에 하나만 활성. Accordion과 같은 패턴인가?

**자문자답 체크리스트**

1. state 모양은? — `activeTab: 'home' | 'about' | 'contact'`
2. 부모 `Tabs`는 무엇을 props로? — 각 Tab에 `isActive`, `onSelect`
3. "두 개 동시 활성" 버그가 **원천적으로 불가능한 이유**는? — state 변수가 단 하나

---

<!-- beat: b7 -->

## Recap — 섹션 마무리

- **Accordion** = 단일 `activeIndex` → "한 번에 하나" 강제
- **Synced Inputs** = 단일 `text` → 동기화 보장
- **Filterable List** = 단일 `query` + derived `results`
- **공통 모양**: 부모 state 1개 → 자식들에 (값, 핸들러) props
- 다음(S4): state가 의도치 않게 **리셋 vs 보존**되는 문제
