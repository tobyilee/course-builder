---
marp: true
theme: default
paginate: true
footer: "LO-S2.4"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
---

<!-- beat: b1 -->

# redundant state와 props mirroring

## 어떤 값이 state여야 할까?

LO-S2.4

---

<!-- beat: b1 -->
<!-- _footer: "LO-S2.4" -->

## firstName을 바꿨는데 fullName은 그대로?

- 입력란에 'Bob' 을 타이핑해도 `fullName` 영역은 옛 값 그대로
- 원인은 로직이 아니라 **fullName을 state로 보관**했다는 구조적 결정
- 오늘의 질문: 어떤 값이 state여야 하고, 어떤 값은 매 렌더 계산해야 하는가?

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.4" -->

## 원칙 ③ 계산 가능한 값은 state가 아니다

```jsx
// X — fullName을 state로 보관 (동기화 버그의 씨앗)
const [fullName, setFullName] = useState('');

// O — 매 렌더에서 derive
const fullName = firstName + ' ' + lastName;
```

- 같은 입력으로 같은 출력이 나오면 그건 **derived value**
- `useMemo`는 **비용이 클 때만** — 작은 string 결합엔 오버헤드

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.4" -->

## 안티패턴: props를 useState 초기값으로 mirror

```jsx
// X — messageColor가 바뀌어도 state는 첫 값 그대로
function Message({ messageColor }) {
  const [color, setColor] = useState(messageColor);
  // ...
}
```

- `useState`의 초기값은 **첫 렌더에만** 사용됨
- 부모가 prop을 바꿔도 자식 state는 갱신되지 **않음** → stale UI

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.4" -->

## 두 가지 해법 — 직접 사용 vs initial 접두사

```jsx
// 해법 A — 그냥 직접 사용 (대부분 이게 정답)
function Message({ messageColor }) {
  const color = messageColor;
}

// 해법 B — '의도적으로 무시한다'를 이름으로 신호
function Message({ initialColor }) {
  const [color, setColor] = useState(initialColor);
}
```

선택 기준: **부모 변경을 반영해야 하면 A**, **'폼 초기값처럼 첫 값만 시드'로 쓸 거면 B**

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.4" -->

## 세 예제로 굳히기

- **fullName** — `firstName/lastName`만 useState, fullName은 render 계산 → 영원히 동기 상태
- **Message(messageColor)** — 부모가 'blue'→'red' 변경 시, mirror는 'blue' 고정 / 직접 사용은 즉시 'red'
- **EditableForm(initialName)** — 사용자 편집을 부모 prop이 덮으면 안 되므로 **'initial' 접두사가 정답**

> 디버깅 신호: '왜 갱신 안 되지?' → useState 초기값 자리에 prop이 있는지 먼저 확인

---

<!-- beat: b5 -->
<!-- _footer: "LO-S2.4" -->

## 자가 진단 — 코드 두 줄

```jsx
// 진단 1
const [items, setItems] = useState(props.items);
```
부모 `items`가 갱신되면 stale → **직접 사용** 또는 lifting state up

```jsx
// 진단 2
function Modal({ defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen);
}
```
이름을 **`initialOpen`** 으로 바꾸자 — '첫 값 시드'를 API에 노출

---

<!-- beat: b6 -->
<!-- _footer: "LO-S2.4" -->

## Recap — redundant & mirroring

- 계산 가능한 값은 state가 아니다 — render에서 **derive**
- props를 `useState` 초기값으로 mirror 하지 않기
- 부모 변경을 반영해야 하면 **직접 사용**, '시드'로 쓸 거면 **`initial` 접두사**
- 다음 class: 객체 자체를 보관하면 생기는 **duplication** 문제
