# Source: Removing Effect Dependencies

## 핵심 원칙

### 1. 의존성은 코드와 일치해야 한다
deps는 "고르는 것"이 아니라 Effect 코드가 결정. reactive 값(props/state/body 변수)을 사용하면 반드시 listing.

### 2. linter suppress 절대 금지
> "Suppressing the dependency linter leads to unintuitive bugs that are hard to find."

```js
// 🔴
useEffect(() => {/* uses count */
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []); // count가 frozen → counter가 1에 멈추는 버그
```

## 의존성 줄이는 6가지 전략

### 전략 1: 정적 값을 컴포넌트 밖으로
```js
const options = { serverUrl: 'https://...', roomId: 'music' }; // 진짜 상수
function ChatRoom() {
  useEffect(() => { createConnection(options).connect(); }, []); // ✅ deps 비어도 OK
}
```

### 전략 2: 객체/함수를 Effect 안에서 생성 (원시값만 deps)
```js
// 🔴 매 렌더 새 객체 → 매 렌더 재동기화
function ChatRoom({ roomId }) {
  const options = { serverUrl, roomId };
  useEffect(() => {createConnection(options);}, [options]);
}

// ✅ 안에서 생성
function ChatRoom({ roomId }) {
  useEffect(() => {
    const options = { serverUrl, roomId };
    createConnection(options);
  }, [roomId]);
}
```

### 전략 3: state 의존 → updater 함수
```js
// 🔴
useEffect(() => {
  c.on('message', m => setMessages([...messages, m]));
}, [roomId, messages]); // messages 의존 → 메시지마다 재연결

// ✅
useEffect(() => {
  c.on('message', m => setMessages(prev => [...prev, m])); // updater
}, [roomId]); // messages 안 필요
```

### 전략 4: 비-반응형 로직 → useEffectEvent
```js
// 🔴 isMuted 변경 시 재연결
function ChatRoom({ roomId }) {
  const [isMuted, setIsMuted] = useState(false);
  useEffect(() => {
    c.on('message', m => { if (!isMuted) playSound(); });
  }, [roomId, isMuted]);
}

// ✅
function ChatRoom({ roomId }) {
  const [isMuted, setIsMuted] = useState(false);
  const onMessage = useEffectEvent(m => { if (!isMuted) playSound(); });
  useEffect(() => {
    c.on('message', onMessage);
  }, [roomId]); // ✅ isMuted 빠짐
}
```

### 전략 5: 무관한 동기화는 Effect 분리
```js
// 🔴 한 Effect가 country fetch + city fetch 둘 다
useEffect(() => {
  fetchCities(country);
  if (city) fetchAreas(city);
}, [country, city]); // city 바뀌면 country fetch도 재실행

// ✅
useEffect(() => fetchCities(country), [country]);
useEffect(() => { if (city) fetchAreas(city); }, [city]);
```

### 전략 6: 객체 prop → 원시값 분해
```js
// ✅ options 객체 대신 원시값 props
function ChatRoom({ roomId, serverUrl }) {
  useEffect(() => {
    createConnection({ roomId, serverUrl });
  }, [roomId, serverUrl]);
}
```

## 실전 예제

### 1) 타이머 — updater 패턴
```js
// 🔴 매 tick마다 interval 재생성
useEffect(() => {
  const id = setInterval(() => setCount(count + 1), 1000);
  return () => clearInterval(id);
}, [count]);

// ✅
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000);
  return () => clearInterval(id);
}, []);
```

### 2) Animation — useEffectEvent로 duration 추출
```js
// 🔴 slider 움직일 때마다 애니메이션 다시 시작
function Welcome({ duration }) {
  useEffect(() => {
    const a = new FadeInAnimation(ref.current);
    a.start(duration);
  }, [duration]);
}

// ✅ duration 변경에 무반응
function Welcome({ duration }) {
  const onAppear = useEffectEvent(a => a.start(duration));
  useEffect(() => {
    const a = new FadeInAnimation(ref.current);
    onAppear(a);
  }, []);
}
```

### 3) 채팅 — 객체 prop을 원시값으로
```js
// 🔴 부모 렌더마다 새 options
function App() { return <ChatRoom options={{ serverUrl, roomId }} />; }
function ChatRoom({ options }) {
  useEffect(() => createConnection(options).connect(), [options]); // 매번 재연결
}

// ✅
function App() { return <ChatRoom roomId={roomId} serverUrl={serverUrl} />; }
function ChatRoom({ roomId, serverUrl }) {
  useEffect(() => {
    const c = createConnection({ roomId, serverUrl });
    c.connect();
    return () => c.disconnect();
  }, [roomId, serverUrl]);
}
```

## 워크플로

1. Effect 코드 작성 (필요한 reactive 값 다 사용)
2. linter 따라서 deps 채우기
3. deps가 마음에 안 들면 → **deps가 아닌 코드를 변경**
4. 만족할 때까지 반복

> "deps는 코드의 거울. 변경하려면 코드를 바꾼다."

## Recap

| 문제 | 해결 |
|---|---|
| deps 너무 많음 | 정적 값 밖으로, 객체/함수는 Effect 안으로 |
| state 의존 무한 루프 | updater `setX(prev => ...)` |
| 읽기만 하고 반응 안 시키고 싶음 | useEffectEvent |
| 객체/함수 매 렌더 재생성 | 원시값 추출, 안에서 생성 |
| 여러 동기화 묶임 | Effect 분리 |
| linter suppress 유혹 | 절대 금지, 위 기법 사용 |
