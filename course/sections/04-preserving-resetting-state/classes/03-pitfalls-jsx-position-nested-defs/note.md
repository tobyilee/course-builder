# 함정 — JSX 위치 ≠ 트리 위치 & 컴포넌트 정의 중첩 금지

> LOs: LO-S4.4, LO-S4.2

## 개요

코드 두 조각을 먼저 보겠습니다 [slide 1]. 첫째는 `if` 분기로 JSX를 두 군데에 따로 적었는데도 state가 사라지지 않습니다. 둘째는 컴포넌트 안에 또 다른 컴포넌트를 정의했더니 입력창에 글자를 칠 때마다 input이 비워집니다. 둘 다 미스터리처럼 보이지만, 지난 두 class([S4.C1], [S4.C2])의 트리 위치 규칙으로 정확히 설명됩니다.

## 핵심 개념

**함정 1 — JSX 위치(코드 라인)와 트리 위치(렌더된 슬롯)는 다릅니다** [slide 2]. 우리가 코드 위에서 두 줄로 갈라 적었다고 React가 두 위치로 인식하는 것이 아닙니다. 기준은 **리턴된 트리에서 부모의 몇 번째 자식인가**입니다.

```jsx
if (isFancy) return <div><Counter isFancy={true} /></div>;
return <div><Counter isFancy={false} /></div>;
```

두 분기 모두 "div의 첫 자식 = Counter"로 트리상 같은 위치, 같은 타입입니다 [slide 3]. 토글해도 score는 보존됩니다. 의도가 보존이면 OK, 의도가 리셋이라면 버그입니다. 디버깅할 때는 코드 라인이 아니라 머릿속에 **리턴된 트리 다이어그램**을 그리세요.

**함정 2 — 컴포넌트 정의를 다른 컴포넌트 함수 본문 안에 두지 마세요** [slide 4]. 부모가 렌더될 때마다 자식 컴포넌트 함수가 **새로운 함수 객체**로 다시 만들어집니다. React 입장에서는 매 렌더마다 컴포넌트 타입이 바뀐 셈이고, 같은 위치 + 다른 타입 → 규칙 2에 의해 state는 매번 리셋됩니다. 증상은 "input에 한 글자 칠 때마다 비워짐" 같은 미스터리 버그로 나타납니다.

## 예시

안티패턴 [slide 5].

```jsx
function MyComponent() {
  function MyTextField() {
    const [text, setText] = useState('');
    return <input value={text} onChange={e => setText(e.target.value)} />;
  }
  return <MyTextField />;
}
```

`MyComponent`가 키 입력으로 리렌더 → `MyTextField`가 새 함수 객체로 다시 정의 → React는 이전과 다른 타입으로 인식 → unmount → 새 state. 한 글자 입력될 때마다 빈 input이 됩니다.

리팩터링 — `MyTextField`를 파일 top-level로 빼냅니다.

```jsx
function MyTextField({ value, onChange }) {
  return <input value={value} onChange={onChange} />;
}

function MyComponent() {
  const [text, setText] = useState('');
  return <MyTextField value={text} onChange={e => setText(e.target.value)} />;
}
```

이제 같은 위치 + 안정된 타입 → state 정상 보존. 필요한 데이터는 props로 넘기면 충분합니다. "안에 두어야만 하는" 이유는 거의 없습니다.

## 흔한 실수

- **"클로저로 부모 변수를 캡처하려고" 컴포넌트를 안에 정의.** 매력적이지만 매 렌더마다 타입이 바뀌어 state가 붕괴합니다. top-level로 빼고 그 변수를 props로 넘기세요.
- **`if` 분기로 JSX를 갈라 쓰면 위치가 분리될 거라는 착각.** 같은 부모의 같은 슬롯이면 같은 위치입니다. 정말 리셋이 필요하면 `key`를 주거나([S4.C2] 전략 2) 다른 부모 슬롯에 두세요.

## 복습

JSX의 코드 위치가 아니라 **리턴된 트리의 위치**가 기준입니다. 컴포넌트 정의는 항상 top-level에 — 안에 두면 매 렌더마다 타입이 새로 생겨 state가 리셋됩니다. S4 전체 도구는 결국 세 가지입니다 — **위치, 타입, key**. 이 셋이면 보존과 리셋을 100% 통제할 수 있습니다.
