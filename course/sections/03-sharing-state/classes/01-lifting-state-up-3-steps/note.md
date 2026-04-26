# Lifting State Up — 형제 컴포넌트를 협조시키는 3단계
> LOs: LO-S3.1

## 개요
두 형제 컴포넌트가 각자 `useState`를 갖고 있을 때 한 쪽을 클릭해도 다른 쪽이 반응하지 않는 상황은 누구나 한 번쯤 겪습니다 [slide 1]. Almaty Accordion에서 두 Panel이 각자 `isActive`를 보유하면 둘 다 동시에 열려버리죠. React의 단방향 데이터 흐름은 형제끼리 직접 대화하지 못하게 막기 때문에, 우리는 state를 **공통 부모로 끌어올려야** 합니다. 이 class는 그 작업을 기계적으로 수행하는 3단계 절차를 손에 익히는 시간입니다.

## 핵심 개념
**Lifting state up**은 자식이 갖던 state를 두 형제를 모두 렌더하는 가장 가까운 공통 부모로 옮기는 리팩터링입니다 [slide 2]. 결과적으로 데이터는 props로 **아래로**, 이벤트는 핸들러로 **위로** 흐르는 양방향 모양이 됩니다.

표준 절차는 세 단계로 끊어집니다 [slide 3]:

1. **자식에서 state 제거** — Panel 내부의 `useState(isActive)`를 삭제하고 `isActive`를 props로 받도록 시그니처를 바꿉니다.
2. **부모에서 하드코딩 props로 자식 렌더** — `<Panel isActive={true} />`처럼 임시값을 박아 넣고 화면이 의도대로 그려지는지부터 확인합니다.
3. **부모에 state 추가 + 핸들러를 props로 내려보냄** — `useState(activeIndex)`를 부모에 만들고 `isActive={activeIndex === i}`, `onShow={() => setActiveIndex(i)}`를 자식에 주입합니다.

각 단계가 **독립적으로 컴파일/렌더 가능한 체크포인트**라는 점이 중요합니다. 한 번에 한 단계씩만 바꾸면 어디서 깨졌는지 즉시 보입니다.

## 예시
Almaty Accordion을 절차대로 변형해 봅시다 [slide 4].

```jsx
// After — 부모가 단일 activeIndex 보유
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

`activeIndex`라는 **단 하나의 숫자**가 "어느 패널이 열려 있는가"를 통째로 표현한다는 점에 주목하세요. 두 개의 boolean이 아니라 하나의 인덱스로 모델링했기 때문에 "둘 다 열림" 같은 모순 상태가 원천적으로 불가능합니다 — 이는 [S2.C1]에서 본 모순 회피 원칙과 정확히 같은 결입니다.

## 흔한 실수
- **두 곳에 같은 state 사본을 둔다** — Step 1을 건너뛰고 부모에 `activeIndex`만 추가하면 자식의 옛 `useState(isActive)`가 부모 값을 무시해 화면이 props 변화에 반응하지 않습니다.
- **자식이 자기 useState로 부모와 어긋난다** — Panel 안에 `useState`를 남겨둔 채 부모에서도 state를 만들면 첫 클릭 시 한쪽만 갱신되어 동기화가 깨집니다.
- **핸들러를 자식에서 정의하고 부모에 통보 안 함** — 이벤트가 위로 못 올라갑니다. `onShow` 같은 콜백 props로 명시적으로 알리세요 [slide 5].

## 복습
자식에서 state 제거 → 부모에서 하드코딩 → 부모에 state 추가의 3단계, 그리고 데이터는 아래로·이벤트는 위로. 다음 class에서는 "그래서 state를 어디에 둘지" 결정하는 사고법을 배웁니다 [S3.C2].
