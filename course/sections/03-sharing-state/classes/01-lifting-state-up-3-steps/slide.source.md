---
marp: true
theme: default
paginate: true
footer: "LO-S3.1"
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

# Lifting State Up

### 형제 컴포넌트를 협조시키는 3단계

S3.C1 · 12분 · LO-S3.1

---

<!-- beat: b1 -->

## 형제는 직접 대화할 수 없다

- Almaty Accordion — 두 Panel이 각자 `useState(isActive)`
- "About" 펼친 뒤 "Etymology" 누르면 **둘 다 열림**
- React는 단방향 흐름 — 형제끼리 통신 통로가 없다
- 오늘의 약속: 3단계만 따르면 형제 협조가 **기계적으로** 풀린다

> 통증의 정체 — state가 자식에 흩어져 있어서, 한쪽 변경이 다른 쪽에 닿지 못한다.

---

<!-- beat: b2 -->

## Lifting state up — 흐름의 모양

- **자식 → 부모**: state를 공통 부모로 옮긴다
- **부모 → 자식**: 데이터는 `props`로 아래로
- **자식 → 부모**: 이벤트는 핸들러로 위로
- 공통 부모 = 두 형제를 모두 렌더하는 가장 가까운 컴포넌트

```text
        Accordion (state: activeIndex)
        ↙ props        ↘ props
   Panel A           Panel B
        ↖ onShow      ↗ onShow
```

---

<!-- beat: b3 -->

## 표준 3단계 레시피

1. **자식에서 state 제거** — `useState(isActive)` 삭제
2. **부모에서 하드코딩 props로 자식 렌더** — `<Panel isActive={true} />` 같은 임시값
3. **부모에 state + 핸들러를 props로 내려보냄** — `useState(activeIndex)` + `onShow`

> 핵심: 각 단계가 **독립적으로 컴파일/렌더 가능한 체크포인트**.
> 한 번에 한 단계씩만 바꿔야 디버깅 가능하다.

---

<!-- beat: b4 -->

## Almaty Accordion — Before & After

<div class="two-col">

**Before (자식이 state 보유)**

```jsx
function Panel({ title, children }) {
  const [isActive, setIsActive] =
    useState(false);
  return (
    <section>
      <h3>{title}</h3>
      {isActive
        ? <p>{children}</p>
        : <button onClick={
            () => setIsActive(true)
          }>Show</button>}
    </section>
  );
}
```

**After (부모가 activeIndex 보유)**

```jsx
function Accordion() {
  const [activeIndex, setActiveIndex]
    = useState(0);
  return (<>
    <Panel title="About"
      isActive={activeIndex === 0}
      onShow={() => setActiveIndex(0)}
    >...</Panel>
    <Panel title="Etymology"
      isActive={activeIndex === 1}
      onShow={() => setActiveIndex(1)}
    >...</Panel>
  </>);
}
```

</div>

---

<!-- beat: b5 -->

## 흔한 실수 두 가지

- **Step 1 건너뛰기** — 부모에 state만 추가
  - 자식의 옛 `useState`가 부모 값을 덮어써 동기화 깨짐
- **핸들러를 자식 안에서만 처리** — 부모에 통보 안 함
  - 데이터가 위로 못 올라가서 다른 형제가 반응 못함
- 컨벤션 — `onShow`, `onChange` 처럼 **"이벤트 발생을 알림"** 표현

---

<!-- beat: b6 -->

## Practice — 라디오 Toggle 두 개

미니 시나리오: 두 Toggle 중 **동시에 하나만 on** 만들고 싶다면?

**자문자답 체크리스트**

1. 공통 부모는 어떤 컴포넌트인가?
2. 부모 state 모양은? (예: `activeId: 'a' | 'b' | null`)
3. 자식에 내려보낼 props 2개는? (`isOn`, `onTurnOn`)
4. 자식에서 `useState`를 정말 지웠는가?

---

<!-- beat: b7 -->

## Recap — 한 장 요약

- **3단계** — 자식 state 제거 → 부모 하드코딩 → 부모 state + 핸들러
- **데이터 ↓ props · 이벤트 ↑ 핸들러**
- 각 단계는 깨지지 않는 체크포인트로
- 다음(C2): "그래서 state를 **어디에** 둘지" 결정 사고법
