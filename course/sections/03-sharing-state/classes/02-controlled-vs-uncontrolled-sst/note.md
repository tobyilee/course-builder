# Controlled vs Uncontrolled와 Single Source of Truth
> LOs: LO-S3.2, LO-S3.3

## 개요
[S3.C1]에서 lift를 마친 Panel은 더 이상 자기 상태를 갖지 않습니다 — 이것이 바로 **controlled** 컴포넌트입니다 [slide 1]. 그렇다면 모든 컴포넌트를 controlled로 만들어야 할까요? 어떤 기준으로 결정해야 할까요? 이 class는 두 스타일의 트레이드오프를 정리하고, "state를 어느 컴포넌트에 둘지"를 정당화하는 사고 알고리즘을 손에 쥐는 시간입니다.

## 핵심 개념
**Uncontrolled 컴포넌트**는 자기 state를 자식 내부 `useState`로 보유합니다 [slide 2]. 부모는 영향을 줄 수 없지만 그만큼 부모가 신경 쓸 props가 적어 "드롭인"으로 쓰기 편합니다.

**Controlled 컴포넌트**는 같은 정보를 부모 props로 받습니다. 부모가 완전히 통제하므로 형제 간 협조·동기화가 가능하지만, 부모가 모든 props를 책임져야 합니다.

식별법은 단순합니다: 같은 정보를 **props로 받는가(controlled), useState로 보유하는가(uncontrolled)**를 보세요. 그러나 둘은 흑백이 아닙니다 — 실제 컴포넌트 대부분은 일부 정보는 부모가, 일부는 내부 state가 들고 있는 **부분 controlled**입니다 [slide 3].

선택 기준은 한 줄로 압축됩니다: **"다른 컴포넌트와 협조해야 하는가?"** Yes면 controlled, No면 uncontrolled로 두면 됩니다.

**Single Source of Truth (SST)** 원칙은 한 발짝 더 나아갑니다 — 각 state는 **단 하나의** 컴포넌트가 소유하며, 공유가 필요해지는 순간 가장 가까운 공통 부모로 lift 합니다 [slide 4]. 결정 알고리즘은 세 줄입니다:

1. 이 state를 누가 **읽는가**(쓰는 쪽도 포함) 나열
2. 그들의 **가장 가까운 공통 조상**을 찾는다
3. 거기에 state를 배치

요구사항이 바뀌면 state는 위/아래로 자유롭게 이동시켜도 됩니다.

## 예시
**Synced Inputs** — 두 Input이 같은 값을 보여줘야 합니다 [slide 5]. 각 Input이 자체 `useState`를 가지면 동기화가 불가능하니, 부모에 `text` state 하나만 두고 두 Input을 controlled로 만듭니다.

```jsx
const [text, setText] = useState('');
<Input value={text} onChange={e => setText(e.target.value)} />
<Input value={text} onChange={e => setText(e.target.value)} />
```

**Filterable List** — `SearchBar`는 `query`를 입력받고 `List`는 필터된 결과를 보여줍니다. `query`를 누가 읽나요? SearchBar(쓰기)와 List(읽기). 그들의 공통 부모(`FilterableList`)에 `query`를 배치하고 `results`는 state가 아니라 derive 합니다.

```jsx
const [query, setQuery] = useState('');
const results = filterItems(foods, query); // derived, not state
```

`results`를 별도 state로 두면 [S2]의 redundant 안티패턴 — `query`와 어긋날 위험을 다시 들이는 셈입니다.

## 흔한 실수
- **두 곳에 같은 state 사본** — 부모와 자식이 동시에 같은 값을 `useState`로 보유하면 동기화 버그의 온상이 됩니다. SST는 "단 하나만 소유"입니다.
- **child의 자체 useState가 부모와 어긋남** — controlled로 바꾼다고 선언했는데 자식 안에 `useState` 잔재를 남기면 첫 클릭에서 props가 무시됩니다.
- **controlled/uncontrolled 혼용으로 props/state 충돌** — 같은 정보를 `value` props로도 받고 `useState`로도 들고 있으면 누가 진실인지 모호해집니다. 한 정보는 한 쪽에서만 관리하세요.

## 복습
Controlled = 부모 props 주도, Uncontrolled = 자식 내부 state 주도. 협조가 필요하면 controlled + 가장 가까운 공통 부모로 lift, SST 유지. 다음은 세 패턴으로 손에 익히기 [S3.C3].
