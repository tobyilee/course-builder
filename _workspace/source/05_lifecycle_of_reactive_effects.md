# Source: Lifecycle of Reactive Effects

## 컴포넌트 ≠ Effect 라이프사이클
- **컴포넌트**: mount → update → unmount
- **Effect**: **synchronization 시작/중지** 사이클

핵심: "Effect는 콜백이 mount/unmount에 발화" 가 아니라 "각 Effect는 독립된 시작/중지 사이클".

## 매 렌더가 자체 Effect 가짐 (closure)

```js
const serverUrl = 'https://localhost:1234';

function ChatRoom({ roomId }) {
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => connection.disconnect();
  }, [roomId]);
}
```

**roomId: "general" → "travel" 시나리오**:
1. cleanup 실행 → "general" 연결 해제
2. Effect 본체 다시 실행 → 새 closure가 새 roomId 캡처 → "travel" 연결
3. UI에서 선택한 방과 항상 동기화됨

## Reactive vs Non-Reactive 값

| 종류 | 정의 | 예 | 의존성 필요? |
|---|---|---|---|
| Reactive | 렌더 중 계산, 렌더마다 바뀔 수 있음 | props, state, derived in body | ✅ |
| Non-Reactive | 절대 안 바뀜, 컴포넌트 밖 선언 | 모듈 상수, 글로벌 URL | ❌ |

```js
const serverUrl = 'https://localhost:1234'; // non-reactive
function ChatRoom({ roomId }) {              // reactive (prop)
  const [message, setMessage] = useState(''); // reactive (state)
  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.connect();
    return () => c.disconnect();
  }, [roomId]); // serverUrl 생략 OK
}
```

state로 만들면 reactive 됨:
```js
const [serverUrl, setServerUrl] = useState('https://localhost:1234');
useEffect(() => {...}, [roomId, serverUrl]); // 이제 둘 다 필수
```

## Reactive 판정 기준
- prop / state / context 값 / 컴포넌트 body에서 derived
- **NON-reactive**: 모듈 상수, ref.current(intentionally mutable), `location.pathname` 같은 외부 mutable

```js
// ❌ ref.current를 deps로 — React가 추적 못 함
useEffect(() => { use(ref.current); }, []); // OK to omit
```

mutable 외부 값에는 useSyncExternalStore.

## ESLint exhaustive-deps
**모든** reactive 값 명시 필수. linter는 `react-hooks/exhaustive-deps`로 강제.

```js
useEffect(() => {
  const c = createConnection(serverUrl, roomId); // ❌ Lint error
}, []); // missing roomId, serverUrl
```

> **절대 suppress 금지**. linter가 부르면 코드를 바꾸지 deps만 바꾸지 마라.

해결 옵션:
1. reactive 값 deps에 추가
2. non-reactive 코드를 Effect 밖으로
3. 비-반응형 부분만 useEffectEvent 안으로

## 채팅 서버 재연결 — 단계별

```js
function ChatRoom({ roomId }) {
  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.connect();
    return () => c.disconnect();
  }, [roomId]);
}
```

흐름:
1. 초기 render `roomId="general"` → connect to general
2. 사용자가 dropdown에서 "travel" 선택 → `roomId="travel"`
3. React가 `Object.is("general", "travel") === false` → cleanup → "general" disconnect
4. Effect 다시 실행 → "travel" connect
5. ✅ UI 항상 선택된 방과 동기화

## 의존성 비교: `Object.is`
```js
// 첫 render
useEffect(() => {...}, ["general"]);
// 다음 render
useEffect(() => {...}, ["travel"]);
// Object.is("general", "travel") → false → 재동기화
```

## 빈 deps `[]` 의미
"이 Effect는 어떤 reactive 값도 안 읽으니 재동기화 X" — 즉 mount/unmount 한 번씩.
```js
const serverUrl = 'https://...';
const roomId = 'general';
useEffect(() => {...}, []); // 둘 다 const → ✅
```

## 각 Effect = 독립 동기화 프로세스
```js
// 🔴 채팅 + 분석 섞임
useEffect(() => {
  logVisit(roomId);
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);

// ✅ 분리
useEffect(() => logVisit(roomId), [roomId]);
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);
```

## Notes
- `setX` setter (useState), ref 객체 (useRef): 안정 식별자 → deps 생략 OK (포함도 무해).
- React가 dev에서 remount하는 이유: cleanup 검증.

## Recap
- 컴포넌트 라이프사이클과 Effect 라이프사이클은 다르다.
- "어떻게 동기화 시작? 어떻게 중지?" 관점.
- reactive 값은 모두 deps에. linter 절대 suppress 금지.
- `Object.is` 비교로 재동기화 결정.
- 무관한 동기화는 Effect 분리.
