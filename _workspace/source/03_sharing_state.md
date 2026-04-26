# Source: Sharing State Between Components

## Lifting State Up — 3단계
1. 자식 컴포넌트에서 state 제거
2. 공통 부모에서 하드코딩 데이터로 자식들 전달
3. 부모에 state 추가, 자식에 값+이벤트 핸들러 props로 내려보냄

## Accordion 예제 — 한 번에 하나만 열림
```js
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

function Panel({ title, children, isActive, onShow }) {
  return (
    <section>
      <h3>{title}</h3>
      {isActive ? <p>{children}</p> : <button onClick={onShow}>Show</button>}
    </section>
  );
}
```

## Synced Inputs 예제
두 input이 같은 값을 보여줘야 할 때:
```js
const [text, setText] = useState('');
<Input value={text} onChange={e => setText(e.target.value)} />
<Input value={text} onChange={e => setText(e.target.value)} />
```

## Filterable List 예제
```js
const [query, setQuery] = useState('');
const results = filterItems(foods, query);
<SearchBar query={query} onChange={e => setQuery(e.target.value)} />
<List items={results} />
```

## Controlled vs Uncontrolled

| 구분 | 상태 위치 | 부모 영향 | 사용 편의 |
|---|---|---|---|
| Uncontrolled | 자식 내부 useState | 없음 | 부모 설정 적게 필요, 협조 어려움 |
| Controlled | 부모 props | 완전 통제 | 부모가 모든 props 제공해야 |

대부분 컴포넌트는 두 스타일이 섞인 형태(부분 controlled).

## Single Source of Truth
- 각 state는 하나의 컴포넌트에서만 소유
- 공유가 필요하면 가장 가까운 공통 부모로 lift
- 그 부모에서 props로 내려보냄
- 리팩터링 시 state는 자유롭게 위/아래로 이동

## Recap
- 두 컴포넌트를 협조시키려면 공통 부모로 state lift
- props로 내려보내고 핸들러로 다시 올려받기
- Controlled = props 주도, Uncontrolled = 내부 state 주도
