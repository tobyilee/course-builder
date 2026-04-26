# Source: Preserving and Resetting State

## 핵심 원리: state는 트리 위치(tree position)에 묶인다

React는 **컴포넌트 인스턴스가 아닌, 렌더 트리에서의 위치**로 state를 추적한다. 같은 위치에 같은 컴포넌트 타입이 있으면 props가 바뀌어도 state 보존.

```js
function App() {
  const counter = <Counter />;
  return <div>{counter}{counter}</div>; // 두 위치 → 두 개의 독립 state
}
```

## 같은 위치 + 같은 컴포넌트 = state 보존
```js
{isFancy ? <Counter isFancy={true} /> : <Counter isFancy={false} />}
// isFancy 토글해도 score 유지
```

## 다른 컴포넌트가 같은 위치 = state 리셋
```js
{isPaused ? <p>See you</p> : <Counter />}
// 토글 시 Counter의 state 파괴
```

## state 리셋 두 전략

### 전략 1: 다른 위치로 렌더
```js
{isPlayerA && <Counter person="Taylor" />}
{!isPlayerA && <Counter person="Sarah" />}
```

### 전략 2: `key` prop
```js
{isPlayerA
  ? <Counter key="Taylor" person="Taylor" />
  : <Counter key="Sarah" person="Sarah" />
}
```
key는 위치를 구별하는 React의 신호다. globally unique일 필요는 없고, **같은 부모 안에서**만 유일하면 된다.

## 실전: 채팅 폼 리셋
```js
// ❌ 연락처 바꿔도 입력 중이던 텍스트 그대로
<Chat contact={to} />
// ✅ key로 리셋
<Chat key={to.id} contact={to} />
```

## ⚠️ Pitfall 1: JSX 위치 ≠ 트리 위치
```js
if (isFancy) return <div><Counter isFancy={true} /></div>;
return <div><Counter isFancy={false} /></div>;
// 둘 다 div의 첫 자식 = 같은 위치 = state 보존
```

## ⚠️ Pitfall 2: 컴포넌트 정의를 컴포넌트 안에 두지 말라
```js
// ❌ 매 렌더마다 MyTextField가 새로 만들어져서 state 리셋됨
function MyComponent() {
  function MyTextField() {
    const [text, setText] = useState('');
    return <input value={text} ... />;
  }
  return <MyTextField />;
}
```
→ 항상 top-level에 정의.

## Recap
- state는 컴포넌트 정체성이 아닌 트리 위치에 묶임
- 같은 타입+같은 위치 = 보존
- 다른 타입 / 다른 위치 / 다른 key = 리셋
- key prop은 위치 안에서 명시적 정체성 부여
- 컴포넌트 정의 중첩 금지
