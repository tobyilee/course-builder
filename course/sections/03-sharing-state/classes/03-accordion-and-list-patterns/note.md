# 케이스 스터디 — Accordion·Synced Inputs·Filterable List
> LOs: LO-S3.4

## 개요
[S3.C1]의 3단계 절차와 [S3.C2]의 Single Source of Truth 원칙을 실전 패턴 세 개에 적용해 봅니다 [slide 1]. Accordion·Synced Inputs·Filterable List는 면접과 실무에서 반복적으로 등장하는 표준 템플릿입니다. 셋 모두 **부모 state 1개 + 자식들에 (값, 핸들러) 쌍 props**라는 똑같은 모양을 갖는다는 점을 손에 새기는 것이 오늘의 목표입니다.

## 핵심 개념
세 패턴은 표면이 달라 보이지만 동일한 골격을 공유합니다 [slide 2]:

- **Accordion** — "한 번에 하나만 열림" 제약을 단일 `activeIndex`로 강제
- **Synced Inputs** — 두 Input의 동일성 보장을 단일 `text` state로 표현
- **Filterable List** — `query` 하나로 검색·표시·파생값을 모두 통제

공통 골격: 부모가 **단일 state 변수**를 보유하고, 자식들에는 "현재 값 + 변경을 알리는 콜백"을 props로 내려보냅니다. 이 모양이 손에 익으면 새로운 컴포넌트 설계도 같은 틀로 빠르게 시작할 수 있습니다.

## 예시
**케이스 1 — Almaty Accordion** [slide 3]. Before에서는 각 Panel이 `isActive` `useState`를 보유해 두 패널이 동시에 열릴 수 있었지만, After에서는 부모가 `activeIndex` 단 하나로 통제합니다.

```jsx
function Accordion() {
  const [activeIndex, setActiveIndex] = useState(0);
  return (
    <>
      <Panel
        title="About"
        isActive={activeIndex === 0}
        onShow={() => setActiveIndex(0)}
      >...</Panel>
      <Panel
        title="Etymology"
        isActive={activeIndex === 1}
        onShow={() => setActiveIndex(1)}
      >...</Panel>
    </>
  );
}
```

핵심 인사이트 — **"한 번에 하나" 제약은 "state 변수를 하나만 갖는다"로 표현됩니다.** 두 boolean이 아니라 하나의 인덱스이기 때문에 "둘 다 열림"은 표현 자체가 불가능합니다.

**케이스 2 — Synced Inputs** [slide 4].

```jsx
const [text, setText] = useState('');
<Input value={text} onChange={e => setText(e.target.value)} />
<Input value={text} onChange={e => setText(e.target.value)} />
```

같은 값을 두 번 저장하지 마라 — SST의 가장 단순한 시각화입니다. 만약 각 Input이 자체 state를 가졌다면 첫 입력에는 한쪽만 바뀌어 동기화가 깨집니다.

**케이스 3 — Filterable List** [slide 5].

```jsx
function FilterableList() {
  const [query, setQuery] = useState('');
  const results = filterItems(foods, query); // derived
  return (
    <>
      <SearchBar query={query} onChange={e => setQuery(e.target.value)} />
      <List items={results} />
    </>
  );
}
```

여기서 `results`는 **state가 아니라 derive**된 값입니다. state를 lift 했더니 파생값도 자연스럽게 부모에서 계산되는 모양 — [S2.C1]의 redundant 회피 원칙이 그대로 적용됩니다.

## 흔한 실수
- **두 곳에 같은 state 사본** — Synced Inputs에서 부모도 `text`, 자식 Input도 자기 `useState`를 갖는 경우. 부모 변경이 자식에 반영되지 않거나 그 반대.
- **child 자체 useState로 부모와 어긋남** — Accordion에서 Panel을 lift 한 뒤에도 옛 `useState(isActive)`를 지우지 않으면 부모의 `activeIndex`가 props로 흘러도 화면은 자식 state를 따라갑니다.
- **controlled/uncontrolled 혼용** — Filterable List의 SearchBar에 `query` props는 받지만 내부에서 또 `useState`로 입력값을 관리하면 "누가 진실인가"가 모호해져 onChange가 누락되는 버그가 생깁니다.

## 복습
Accordion = 단일 `activeIndex`로 "한 번에 하나" 강제, Synced Inputs = 단일 `text`로 동기화, Filterable List = 단일 `query` + derived `results`. 공통 모양은 **부모 state 1개 → 자식들에 (값, 핸들러) props**. 다음 [S4]에서는 state가 의도치 않게 리셋되거나 보존되는 문제를 다룹니다.
