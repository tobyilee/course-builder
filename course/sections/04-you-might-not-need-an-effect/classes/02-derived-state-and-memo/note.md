# Derived state — render 중 계산과 useMemo
> LOs: LO-S4.2

## 개요
이름과 성을 합쳐 풀네임을 보여 주는 컴포넌트 [slide 1] 를 떠올려 봅시다. 어떤 코드에서는 이 일을 두 번 렌더하고, 어떤 코드에서는 한 번 렌더합니다. 차이는 단 한 줄 — `useEffect`를 썼느냐, 안 썼느냐입니다. 이번 클래스에서는 결정 트리의 Q1/Q2에 해당하는 두 가지 안티패턴, **Derived state**와 **비싼 계산 캐싱**을 정리합니다.

## 핵심 개념
**안티패턴 #1 — props/state로부터 파생되는 값을 Effect+state로 보관한다.** [slide 2]

이 패턴이 무엇을 만드는지 타임라인으로 봐 두는 게 좋습니다. 입력이 한 번 바뀌면 React는 (1) 부모 렌더 → (2) Effect 실행 → (3) `setState` 호출 → (4) 재렌더의 4단계를 거치게 되죠. 그런데 사실 그 사이에 "외부 시스템"이 끼어든 적이 없습니다. 그저 입력으로부터 출력을 계산했을 뿐인데, 우리는 그것을 두 번 렌더하는 코드로 만들어 버린 겁니다.

해결은 한 문장입니다 — **render는 순수 함수다. 그러니까 render 중에 그냥 계산하라.** 함수 본문에 `const fullName = firstName + ' ' + lastName;`을 적으면 `firstName`이 바뀔 때마다 자동으로 일관성이 유지됩니다.

**안티패턴 #2 — 비싼 계산을 Effect로 캐싱하려 한다.** [slide 4]

비싼 계산도 render 중에 하되, `useMemo`로 메모이즈합니다. 단, `useMemo`는 다음 세 조건이 모두 맞을 때만 의미가 있습니다.

1. 계산이 **진짜로 비싸다** — 수십~수백 ms 이상이어야 체감 효과가 있습니다.
2. 의존성이 **안정적**이다 — 매 렌더 새 객체가 들어가면 메모이즈는 무용지물입니다.
3. 참조 일관성이 필요한 **하위 트리가 있다** — `React.memo` 자식이 prop 동일성을 본다든지.

세 조건을 만족하지 않으면 메모이즈는 코드만 복잡하게 만듭니다. `console.time`이나 React Profiler로 먼저 측정한 뒤 결정하세요.

## 예시

```tsx
// 안티패턴 #1 — Before
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);

// After — render 중 계산
const fullName = firstName + ' ' + lastName;
```

`useState`를 지우고 `useEffect`를 지우면 5줄이 1줄로 줄어듭니다 [slide 3]. 추가 렌더는 0회.

비싼 계산 케이스 [slide 5] 도 봅시다.

```tsx
// 안티패턴 #2 — Before
const [visibleTodos, setVisibleTodos] = useState([]);
useEffect(() => {
  setVisibleTodos(getFilteredTodos(todos, filter));
}, [todos, filter]);

// After — useMemo
const visibleTodos = useMemo(
  () => getFilteredTodos(todos, filter),
  [todos, filter]
);
```

1만 개 todo 필터링이라면 `useMemo`가 꽤 의미 있는 차이를 만듭니다. 100개 정도라면 그냥 한 줄 계산이 더 좋습니다. React Compiler [slide 6] 가 자동 메모이즈를 도입한 환경이라면 `useMemo`조차 점차 불필요해지지만, 1차 원칙은 여전히 같습니다 — **Effect로 옮기지 말고 render 중에 계산하라.**

## 흔한 실수
가장 흔한 실수는 **Effect를 "값을 저장하는 슬롯"으로 오해하는 것**입니다. "이 값을 어딘가에 보관해야 다음 렌더에서 쓸 수 있겠지" 하는 직관 때문에 `useState`를 만들고 그걸 Effect로 채우는 거죠. 그런데 React 함수 컴포넌트는 매 렌더마다 함수 본문을 다시 실행합니다. 입력에서 도출되는 값은 매번 다시 계산해도 비용이 0에 가까우며, "저장"이라는 개념 자체가 필요 없습니다. 또 하나 자주 보는 실수는 **useMemo를 모든 계산에 자동 반사적으로 두르는 것** — 비싸지 않은 계산을 메모이즈하면 비교 비용과 코드 복잡도만 늘어납니다.

## 복습
- props/state 파생값은 render 중 계산
- 비싸면 `useMemo`, 비싸지 않으면 그냥 변수
- Effect+state로 옮기지 말 것 — 추가 렌더와 동기화 부담만 추가됩니다
- 다음 클래스 [S4.C3] 에서는 Q4의 가지, **state 리셋과 조정**으로 넘어갑니다.
