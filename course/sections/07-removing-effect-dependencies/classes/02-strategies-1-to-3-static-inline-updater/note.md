# 객체·함수는 Effect 안에서, state는 updater로

> LOs: LO-7.3 (객체·함수 의존성을 Effect 내부로 이동시켜 매 렌더 재실행을 막는다), LO-7.4 (state setter의 updater 형태로 state 의존성을 제거한다)

## 개요

`serverUrl` 같은 문자열은 외부화로 끝났습니다 [S7.C1]. 하지만 의존성 경고를 가장 많이 만드는 범인은 **객체와 함수**입니다. JavaScript에서 `{ a: 1 } !== { a: 1 }`이기 때문에, 컴포넌트 본문에서 매 렌더 새로 만들어진 객체는 매 렌더 "변한 의존성"으로 취급됩니다. 그리고 카운터를 1씩 올리는 interval처럼 **이전 state를 읽으려고** state를 의존성에 넣는 패턴은, tick마다 interval을 처음부터 다시 만드는 비극을 낳습니다 [slide 1]. 이 클래스에서는 두 번째·세 번째 전략 — 객체/함수를 Effect 안으로 이동, state는 updater로 — 을 익힙니다.

## 핵심 개념

**객체·함수 의존성은 매 렌더 "변한다".** 컴포넌트 안에 `const options = { roomId }`라고 쓰면, options는 렌더마다 새 참조입니다. 이 객체를 Effect 의존성에 넣으면 Effect는 매 렌더 재실행되고, 채팅방 연결이라면 매 렌더 재연결됩니다 [slide 2]. 해결은 의존성에서 빼는 게 아니라 **객체 자체를 Effect 안에서 만드는 것**입니다.

```tsx
useEffect(() => {
  const options = { serverUrl: SERVER_URL, roomId }; // Effect 안에서
  const conn = createConnection(options);
  conn.connect();
  return () => conn.disconnect();
}, [roomId]); // 이제 진짜 reactive 값(roomId)만 의존
```

같은 원리로 `function fetchData(...)`도 Effect 내부에서 정의하면 의존성에서 사라집니다.

**updater로 state 의존성 제거.** 1초마다 카운터를 +1 하는 interval을 떠올려 보세요. `setCount(count + 1)`을 쓰면 `count`를 의존성에 넣어야 하고, count가 바뀔 때마다 interval이 clear → 재생성됩니다 [slide 3]. 그러면 1초 간격이 깨지죠. updater를 쓰면 React가 최신 state를 인자로 넘겨주므로 **count를 읽지 않아도** 됩니다.

```tsx
// Before — count 의존성으로 매 tick 재생성
useEffect(() => {
  const id = setInterval(() => setCount(count + 1), 1000);
  return () => clearInterval(id);
}, [count]); // 안티패턴
```

```tsx
// After — updater로 의존성 0
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000);
  return () => clearInterval(id);
}, []); // interval은 마운트 시 한 번만
```

**왜 두 전략을 같이 묶는가.** 둘 다 "Effect가 reactive로 보이는 무엇을 안 보게 만드는" 같은 사고법입니다 — 외부화는 컴포넌트 밖으로, 내부화는 Effect 안으로, updater는 setter 인자로. 의존성 배열은 거짓말을 안 하면서도 깨끗해집니다.

## 예시

부모에서 받은 `options` prop을 channel 구독에 쓰는 자주 보는 케이스:

```tsx
// Before — 부모가 매 렌더 새 객체 prop을 내려주면 매 렌더 재구독
function ChatRoom({ options }: { options: ChatOptions }) {
  useEffect(() => {
    const conn = createConnection(options);
    conn.connect();
    return () => conn.disconnect();
  }, [options]); // options는 매 렌더 새 참조
}
```

이 경우 객체를 Effect 안으로 옮겨도, 부모가 객체를 넘겨주는 한 의존성에 들어갈 수밖에 없습니다. 진짜 해법은 객체를 받지 말고 **원시 필드(roomId, serverUrl)를 따로 받는 것**입니다 — 그 패턴은 [S7.C4]에서 다룹니다. 지금 단계에서 가능한 차선은 부모가 객체를 useMemo로 안정화하거나, 자식이 필요한 필드만 꺼내 의존성에 쓰는 것입니다.

## 흔한 실수

**state를 읽으려고 의존성에 넣고, 매 tick interval 재생성.** updater를 모르면 거의 모두가 한 번씩 빠집니다. 1초 interval인데 800ms마다 재생성돼서 사실상 "뭔가 빠르게 뛰는 것"이 됩니다. 증상은 "타이머가 가끔 두 번 뛴다", "애니메이션이 가속된다" — 원인은 의존성에 들어간 state입니다 [slide 4].

**Options 객체를 부모 prop으로 받아 매 렌더 새 객체.** `<ChatRoom options={{ roomId, serverUrl }} />`처럼 인라인 객체를 내려보내면, 부모가 다른 이유로 리렌더될 때마다 자식 Effect가 재실행됩니다. 부모의 무관한 state 변경이 채팅 재연결을 일으키는 미스터리는 거의 이 패턴입니다 [slide 5].

## 복습

- 객체·함수는 가능하면 Effect **내부**에서 만듭니다.
- state를 읽기만 하는 setter는 `setX(prev => ...)` updater로 의존성을 0으로 만듭니다.
- prop으로 받은 객체는 [S7.C4]의 원시값 분해 전략으로 마무리합니다.
