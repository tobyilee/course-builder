# Source: Reusing Logic with Custom Hooks

## Custom Hook이란
React 내장 Hooks(useState/useEffect/useContext...)를 조합한 함수. **stateful 로직**을 컴포넌트 간 재사용.

## "use" 접두사 규칙
- 이름은 `use` + 대문자 (예: `useOnlineStatus`, `useChatRoom`)
- 의미:
  1. Hook 호출 신호 (linter가 enforce)
  2. Hook 사용 위치 명시
  3. 의도 분명히

```js
// ❌ Hook 안 쓰면서 'use' 접두사
function useSorted(items) { return items.slice().sort(); }

// ✅ Hook 쓸 때만
function useAuth() { return useContext(Auth); }
```

## 핵심 원칙: 로직 공유 (state는 공유 안 함)
**Custom Hook은 stateful 로직만 공유. State 자체는 공유 안 함.** 각 호출 사이트가 **완전히 독립** state 가짐.

```js
function StatusBar() { const isOnline = useOnlineStatus(); /* instance #1 */ }
function SaveButton() { const isOnline = useOnlineStatus(); /* instance #2 */ }
```
같은 외부 값(네트워크 상태)과 동기화될 뿐, 두 state는 별개.
**여러 컴포넌트가 같은 state를 보려면** lifting + props (이전 코스 S3).

## 대표 예제

### useOnlineStatus
```js
export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);
  useEffect(() => {
    function on() { setIsOnline(true); }
    function off() { setIsOnline(false); }
    window.addEventListener('online', on);
    window.addEventListener('offline', off);
    return () => {
      window.removeEventListener('online', on);
      window.removeEventListener('offline', off);
    };
  }, []);
  return isOnline;
}
```

### useFormInput — 폼 필드 props 추출
```js
function useFormInput(initial) {
  const [value, setValue] = useState(initial);
  return { value, onChange: e => setValue(e.target.value) };
}

function Form() {
  const firstName = useFormInput('Mary');
  const lastName = useFormInput('Poppins');
  return (<>
    <input {...firstName} />
    <input {...lastName} />
    <p>Hello {firstName.value} {lastName.value}</p>
  </>);
}
```

### useChatRoom — reactive 값 + 핸들러
```js
export function useChatRoom({ serverUrl, roomId, onReceiveMessage }) {
  const onMessage = useEffectEvent(onReceiveMessage); // 핸들러는 wrap

  useEffect(() => {
    const options = { serverUrl, roomId };
    const c = createConnection(options);
    c.connect();
    c.on('message', m => onMessage(m));
    return () => c.disconnect();
  }, [roomId, serverUrl]); // onReceiveMessage는 Effect Event 안에 → deps에 X
}
```

## 핸들러를 Custom Hook 인자로 받기
```js
useChatRoom({
  roomId,
  serverUrl,
  onReceiveMessage(msg) { showNotification('New: ' + msg); }
});
```
**패턴**: 핸들러는 useEffectEvent로 wrap → 매 렌더마다 새 함수여도 deps 오염 X.

## 추출 시점

### ✅ 추출하라
- 여러 컴포넌트에 반복
- 외부 시스템 동기화 Effect (의도 명료해짐)
- 구현 세부 숨기고 싶음
- 명확한 단일 목적

**Before / After**:
```js
// Before
function ShippingForm({ country }) {
  const [cities, setCities] = useState(null);
  useEffect(() => { fetch(`/api/cities?country=${country}`).then(...); }, [country]);
  const [city, setCity] = useState(null);
  const [areas, setAreas] = useState(null);
  useEffect(() => { if (city) fetch(`/api/areas?city=${city}`).then(...); }, [city]);
}

// After
function useData(url) {
  const [data, setData] = useState(null);
  useEffect(() => {
    if (url) fetch(url).then(r => r.json()).then(setData);
  }, [url]);
  return data;
}

function ShippingForm({ country }) {
  const cities = useData(`/api/cities?country=${country}`);
  const [city, setCity] = useState(null);
  const areas = useData(city ? `/api/areas?city=${city}` : null);
}
```

### ❌ 추출하지 마라
- 한 컴포넌트만 사용
- Hook 호출 안 하는 함수 → 일반 함수로
- 단순 wrapper / 가짜 lifecycle:
```js
// ❌ useMount 같은 lifecycle wrapper
function useMount(fn) { useEffect(fn, []); }
// ✅ 그냥 useEffect
useEffect(() => {...}, [deps]);
```

## Composition
```js
function useInterval(callback, delay) {
  const onTick = useEffectEvent(callback);
  useEffect(() => {
    const id = setInterval(onTick, delay);
    return () => clearInterval(id);
  }, [delay]);
}

function useCounter(delay) {
  const [count, setCount] = useState(0);
  useInterval(() => setCount(c => c + 1), delay);
  return count;
}

const count = useCounter(1000);
```

## Best Practice: 고수준 use case에 집중
```js
// ✅ 도메인 의미
useChatRoom(...), useData(...), useOnlineStatus()
// ❌ 일반 lifecycle
useMount, useEffectOnce, useUpdateEffect
```

## 미래 개선 가능성
React가 더 좋은 API 추가하면 Hook만 바꾸고 호출처는 그대로:
```js
// 옛날: useState + useEffect
// 새 버전: useSyncExternalStore — 호출처 변경 0
export function useOnlineStatus() {
  return useSyncExternalStore(subscribe, () => navigator.onLine, () => true);
}
```

## Recap

| 개념 | 규칙 |
|---|---|
| Naming | `use` + 대문자 (Hook 호출 시에만) |
| State 공유 | 각 호출은 독립 — 공유는 lifting으로 |
| Composition | Hook 안에서 다른 Hook 호출 OK |
| Reactive 값 | props/state 받아서 Effect 재실행 |
| 핸들러 | useEffectEvent로 wrap |
| 추출 트리거 | 반복 + 의도 명료화 |
| 회피 | 단일 사용처 / lifecycle wrapper / Hook 안 쓰는 함수 |
