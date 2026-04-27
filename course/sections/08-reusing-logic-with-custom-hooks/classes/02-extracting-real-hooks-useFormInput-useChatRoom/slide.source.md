---
marp: true
theme: default
paginate: true
footer: "LO-S8.2"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
---

<!-- beat: b1 -->

# 실전 추출

## useFormInput · useChatRoom · useEffectEvent

오늘은 직접 손으로 만든다 — 난이도 사다리 세 칸

---

<!-- beat: b2 -->
<!-- _footer: "LO-S8.2" -->

## useFormInput — 인자 + 반환 객체

```jsx
function useFormInput(initial) {
  const [value, setValue] = useState(initial);
  return {
    value,
    onChange: e => setValue(e.target.value),
  };
}

// 사용처
const firstName = useFormInput('Mary');
const lastName  = useFormInput('Poppins');
return <input {...firstName} />;
```

5개 input도 한 줄씩으로 압축 — 각자 독립 useState slot

---

<!-- beat: b3 -->
<!-- _footer: "LO-S8.3" -->

## useChatRoom의 요구사항

- `roomId` 바뀌면 → **재연결** (reactive)
- `serverUrl` 바뀌면 → **재연결** (reactive)
- `onReceiveMessage`는 매 렌더 새 함수여도 → **재연결 X**
- deps에 넣으면? 매 렌더마다 connect/disconnect 폭주
- deps에서 빼면? exhaustive-deps 경고 + stale closure
- 해법: 핸들러를 **`useEffectEvent`로 wrap** — Hook 정의 안에서

---

<!-- beat: b4 -->
<!-- _footer: "LO-S8.3" -->

## useChatRoom 구현

```jsx
function useChatRoom({ serverUrl, roomId, onReceiveMessage }) {
  const onMessage = useEffectEvent(onReceiveMessage);
  useEffect(() => {
    const c = createConnection({ serverUrl, roomId });
    c.connect();
    c.on('message', m => onMessage(m));
    return () => c.disconnect();
  }, [roomId, serverUrl]); // 핸들러는 deps에 없음
}
```

부모가 100번 리렌더해도 connect는 1회 — `roomId` 바뀔 때만 재연결

---

<!-- beat: b4 -->
<!-- _footer: "LO-S8.3" -->

## 사용처는 useEffectEvent를 모른다

```jsx
function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://...');
  useChatRoom({
    roomId,
    serverUrl,
    onReceiveMessage(msg) {
      showNotification('New: ' + msg);
    },
  });
  // ...
}
```

캡슐화: 호출자는 평범한 콜백만 넘기면 끝

---

<!-- beat: b5 -->

## 세 Hook 한눈 비교

| Hook | 인자 | 반환 | Effect | EffectEvent |
|---|---|---|---|---|
| `useOnlineStatus` | 없음 | `boolean` | ✅ | — |
| `useFormInput` | `initial` | `{value, onChange}` | — | — |
| `useChatRoom` | `{url, id, onMsg}` | `void` | ✅ | ✅ |

도메인이 요구하는 모양으로만 인자/반환 설계

---

<!-- beat: b6 -->

## 직접 답해보세요

- Q1. `useChatRoom` deps에 `onReceiveMessage` 넣으면? → 매 렌더 재연결, 메시지 누락
- Q2. `useEffectEvent` 결과를 deps에 넣어도 되나? → ❌ linter가 막는다
- Q3. `useFormInput`은 Effect 없는데 일반 함수면 안 되나? → `useState` 호출하므로 Hook 필수
- Q4. `useEffectEvent` 대신 `useCallback`? → deps 같을 때만 같은 참조. 의도가 다름

---

<!-- beat: b7 -->

## 오늘의 3줄

- 도메인 의미 있는 Hook은 **호출처를 한 줄로** 줄여준다
- **reactive 값** → 인자/deps · **핸들러** → 인자/`useEffectEvent`
- `useEffectEvent`는 Hook 안에 **캡슐화** — 사용처는 평범한 콜백만
