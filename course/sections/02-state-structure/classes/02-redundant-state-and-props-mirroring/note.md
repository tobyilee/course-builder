# redundant state 제거와 props mirroring 안티패턴

> LOs: LO-S2.4

## 개요

입력란에 `firstName`을 'Bob'으로 바꿨는데 화면 한쪽의 `fullName`만 옛 값을 그대로 보여주는 버그 [slide 1], 본 적 있나요? 원인은 로직이 아니라 *fullName을 state로 보관했다*는 **구조적 결정**입니다. 이번 class의 질문은 단순합니다. **어떤 값이 state여야 하고, 어떤 값은 매 렌더 계산해야 하는가?** 그리고 그 결정에서 가장 자주 미끄러지는 자리, 즉 props를 useState 초기값으로 mirror 하는 안티패턴을 진단합니다.

## 핵심 개념

**원칙③: 다른 state나 props로부터 계산 가능한 값은 state로 두지 말 것** [slide 2]. 판단 기준은 한 줄입니다. *"매 렌더마다 같은 입력으로 같은 출력이 나오는가?"* 그렇다면 그건 state가 아니라 **derived value**입니다. `fullName = firstName + ' ' + lastName` 같은 단순 결합은 별도 useState 없이 그냥 변수로 계산합니다. `useMemo`는 비용이 클 때만 — 짧은 string 결합엔 오히려 오버헤드입니다 [S2.C1] 슬로건을 떠올려 보세요.

**안티패턴: props를 useState 초기값으로 mirror** [slide 3].

```jsx
function Message({ messageColor }) {
  const [color, setColor] = useState(messageColor); // 안티패턴
}
```

왜 버그일까요? `useState`의 초기값은 **첫 렌더에만** 사용됩니다. 부모가 나중에 `messageColor='red'`로 바꿔도 자식의 내부 `color`는 'blue'로 굳어버리죠.

처방은 두 갈래입니다.

- **해법 A — 직접 사용.** `const color = messageColor`. 부모 변경이 곧바로 반영되어야 하는 *대부분의 경우*가 여기에 해당합니다.
- **해법 B — `initial` 접두사.** `function Message({ initialColor })` 후 `useState(initialColor)`. 이름 자체가 *"이 prop은 첫 값만 쓰고 이후 변경은 의도적으로 무시한다"*는 신호가 됩니다. 폼의 초기값 시드, 모달의 `defaultOpen` 같은 use case에 적합합니다.

선택 기준은 결국 *"부모의 갱신을 자식이 따라가야 하나, 아니면 첫 값만 시드로 쓰나?"* 한 줄입니다.

## 예시

```jsx
// 예제 1 — fullName은 derive
function Form() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName]   = useState('');
  const fullName = firstName + ' ' + lastName; // 영원히 동기 상태
  return <h1>{fullName}</h1>;
}

// 예제 2 — Message: 직접 사용
function Message({ messageColor }) {
  const color = messageColor; // 부모가 'blue'→'red'로 바꾸면 즉시 반영
  return <div style={{ color }}>...</div>;
}

// 예제 3 — EditableForm: 'initial' 접두사
function EditableForm({ initialName }) {
  const [name, setName] = useState(initialName); // 사용자가 편집 중일 때 부모가 덮으면 안 됨
  return <input value={name} onChange={e => setName(e.target.value)} />;
}
```

디버깅 신호 하나만 기억하세요. *"왜 갱신이 안 되지?"* 의문이 들면 가장 먼저 의심할 곳은 `useState(...)`의 **초기값 자리에 prop이 들어있는지** 입니다 [slide 4].

## 흔한 실수

- **`const [items, setItems] = useState(props.items)`.** 부모의 items가 갱신되면 자식은 stale 상태로 남습니다. 직접 사용으로 바꾸거나, 편집이 필요하면 *lifting state up*으로 부모가 owner가 되게 하세요.
- **`Modal({ defaultOpen })` 안에서 `useState(defaultOpen)`.** 동작은 맞지만 prop 이름이 거짓말을 합니다. `initialOpen`으로 바꿔 *"첫 값 시드"* 의도를 API에 솔직히 노출하세요.

## 복습

계산 가능한 값은 state가 아니라 render에서 derive합니다. props를 useState 초기값으로 mirror 하지 말고, 직접 사용하거나 `initial` 접두사로 의도를 드러내세요. 다음 class [S2.C3]에서는 객체 자체를 보관할 때 생기는 duplication 문제를 다룹니다.
