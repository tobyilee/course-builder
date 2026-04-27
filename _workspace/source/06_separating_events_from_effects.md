# Source: Separating Events from Effects

## Events vs Effects

| 구분 | Event Handler | Effect |
|---|---|---|
| 트리거 | 특정 사용자 액션 (클릭, submit) | 동기화가 필요할 때 (인터랙션 무관) |
| 반응성 | **Non-reactive** — 같은 인터랙션 반복돼야 다시 실행 | **Reactive** — 의존성 변경 시 재실행 |
| reactive 값 읽기 | 읽어도 "반응" X | 읽으면 deps에 명시 + 재실행 |

핵심 질문: 이 코드는 **왜** 실행돼야 하는가?
- 사용자가 그 액션을 했기 때문에 → handler
- 컴포넌트가 화면에 있기 때문에 → Effect

```js
// EVENT — 사용자가 send 클릭했을 때만
function handleSendClick() { sendMessage(message); }

// EFFECT — 컴포넌트가 보이는 동안 연결 유지
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);
```

## Reactive 값 위치별 반응성
- **이벤트 핸들러 안**: non-reactive
- **Effect 안**: reactive — 모든 사용 값을 deps에

## useEffectEvent (실험적)

**목적**: Effect의 **non-reactive 부분**을 추출해 reactive Effect 안에 끼워 넣기.

특성:
- Event handler처럼 동작 (non-reactive)
- 항상 **최신** props/state 봄
- **Effect 안에서만** 호출 가능
- 다른 컴포넌트/Hook에 전달 금지
- Effect deps에 **올리지 마라**

```js
import { useEffectEvent } from 'react';

function ChatRoom({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme); // 최신 theme 읽음
  });

  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.on('connected', () => onConnected());
    c.connect();
    return () => c.disconnect();
  }, [roomId]); // theme 빠짐 — Effect Event 안에 있으니까
}
```

## 문제: 너무 많이 재동기화

**Before**:
```js
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.on('connected', () => showNotification('Connected!', theme));
  c.connect();
  return () => c.disconnect();
}, [roomId, theme]); // ❌ theme 토글 시마다 재연결
```
다크/라이트 토글마다 채팅 끊김 — 끔찍.

**After (useEffectEvent)**: theme 변경은 재연결 안 시키고도 알림은 최신 theme.

## 패턴: reactive 값은 인자로, non-reactive는 안에서 직접

```js
function Page({ url }) {
  const { items } = useContext(ShoppingCartContext);
  const numberOfItems = items.length;

  const onVisit = useEffectEvent(visitedUrl => {
    logVisit(visitedUrl, numberOfItems); // 최신 numberOfItems 자동
  });

  useEffect(() => {
    onVisit(url); // url을 인자로 — closure 캡처 X
  }, [url]); // 오직 url만 — 카트 변경에 재발화 안 함
}
```
**원칙**: reactive 값 → 인자, non-reactive → Effect Event 본체에서 직접.

## ⚠️ 제한
```js
// ❌ 다른 Hook으로 전달
function Timer() {
  const onTick = useEffectEvent(() => setCount(c => c + 1));
  useTimer(onTick, 1000); // ❌
}

// ✅ 사용처(Hook)에 함께 정의
function useTimer(callback, delay) {
  const onTick = useEffectEvent(() => callback());
  useEffect(() => {
    const id = setInterval(onTick, delay);
    return () => clearInterval(id);
  }, [delay]);
}
```

## ⚠️ Pitfall: linter suppress 금지
```js
// ❌
useEffect(() => { logVisit(url, numberOfItems);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [url]);
```
대신 useEffectEvent.

## Naming
"무슨 일이 발생했나" 시점에서:
- ✅ `onMessage`, `onTick`, `onVisit`, `onConnected`
- ❌ `onMount`, `onUpdate`, `onAfterRender`

## Recap
- Event handler = 인터랙션 응답 (non-reactive)
- Effect = reactive 값 동기화
- useEffectEvent로 non-reactive 로직 추출 → reactive Effect 안에 호출
- Effect Event는 deps에 안 들어감
- Effect 외부에 노출 금지 (다른 Hook/컴포넌트 인자 X)
- reactive 값은 인자로, non-reactive는 본체에서 직접
