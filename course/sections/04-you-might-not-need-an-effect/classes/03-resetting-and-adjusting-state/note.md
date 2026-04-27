# State 리셋과 조정 — key prop과 state-during-render
> LOs: LO-S4.3

## 개요
프로필 페이지에서 `userId`가 바뀌었는데, 직전 사용자에게 쓰던 댓글 입력이 그대로 남아 새 사용자에게 보내질 뻔한 버그 [slide 1]. 흔한 처방은 `useEffect(() => setComment(''), [userId])`입니다. 그런데 이 처방은 한 번 깜빡이고, 개발 모드에서 두 번 실행되며, state를 하나 추가할 때마다 리셋 코드를 까먹기 쉽습니다. 더 깔끔한 답이 두 개 있습니다 — `key` prop과 state-during-render.

## 핵심 개념
**안티패턴 #3 — prop이 바뀔 때 컴포넌트의 모든 state를 Effect로 리셋한다.** [slide 2]

답은 단순합니다. 컴포넌트 인스턴스를 **통째로 갈아 끼우세요.**

```tsx
<Profile userId={userId} key={userId} />
```

`key`가 바뀌면 React는 이를 다른 컴포넌트로 인식해 트리에서 노드를 제거하고 새 노드를 생성합니다. 모든 state가 자연스럽게 초기값으로 돌아가고, 어떤 state를 추가하더라도 자동으로 리셋되며, dev 더블 마운트의 영향도 받지 않습니다. Effect 한 블록 대신 prop 한 단어 — 압도적입니다.

**안티패턴 #4 — prop이 바뀔 때 일부 state만 조정한다.** [slide 4]

전체 리셋이 과한 경우입니다. items 리스트가 바뀌면 selection만 비워야 하는 상황을 떠올려 보세요.

- **1순위 — derived value로 바꿀 수 있다면 그게 최선.** selection을 state로 두지 않고 `items.find(...)`로 매 렌더 도출합니다.
- **2순위 — state-during-render.** 렌더 중 `prevItems`를 비교하고 `setSelection(null)`을 즉시 호출합니다.

`setState in render`가 합법인 이유는, React가 같은 렌더 안에서 즉시 다시 렌더하되 자식에게는 영향을 주지 않기 때문입니다. Effect로 리셋할 때 발생하는 한 번의 페인트 비용을 절약하고, 사용자에게는 일관된 한 화면만 보입니다.

## 예시
전체 리셋 케이스 [slide 3]:

```tsx
// Before
function Profile({ userId }) {
  const [comment, setComment] = useState('');
  useEffect(() => setComment(''), [userId]); // 안티패턴
  // ...
}

// After — 부모에 key 추가, 자식의 useEffect 통째로 삭제
<Profile userId={userId} key={userId} />
```

부분 조정 케이스 [slide 5]:

```tsx
// Before — Effect
useEffect(() => setSelection(null), [items]);

// After A — state-during-render
const [prevItems, setPrevItems] = useState(items);
if (items !== prevItems) {
  setPrevItems(items);
  setSelection(null);
}

// After B — derived (가장 좋음)
const selection = items.find(i => i.id === selectedId) ?? null;
```

세 답안의 라인 수, 렌더 횟수, 깜빡임 여부를 비교해 보면 derived가 압도적으로 짧고 정확합니다. state로 둘 이유가 정말 있는지 먼저 의심하세요.

## 흔한 실수
가장 자주 보이는 함정은 **prop을 받아서 그걸 useEffect로 state에 동기화하는 패턴**입니다 — `useEffect(() => setX(propX), [propX])`. 이건 두 가지를 동시에 망칩니다. 첫째, 한 번 깜빡이는 렌더가 추가됩니다. 둘째, 자식이 prop을 "한 번 복제한 뒤 자기 마음대로 수정"한다는 흐릿한 멘탈모델을 만듭니다. prop을 그대로 쓸 수 있는 자리에서는 그대로 쓰고, 부분 변형이 필요하면 derived로 도출하고, 컴포넌트 정체성이 바뀌는 수준이면 `key`로 인스턴스를 갈아 끼우세요. Effect로 prop을 state에 sync하는 건 거의 항상 잘못된 답입니다.

## 복습
- 전체 리셋 → `key` prop 한 줄
- 부분 조정 → derived value 우선, 안 되면 state-during-render
- Effect로 setState 처방은 깜빡임·이중 호출·확장성 문제로 마지막 후보
- 다음 클래스 [S4.C4] 에서는 Q3 가지, **인터랙션 vs 표시**의 6가지 패턴을 정리합니다.
