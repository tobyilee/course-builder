---
marp: true
theme: default
paginate: true
footer: "LO-S5.2"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 21px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# Reactive vs Non-reactive 값

## Object.is로 판정되는 재실행 흐름

LO-S5.2 · LO-S5.3

---

<!-- beat: b1 -->

## deps 배열에 뭘 넣어야 할까?

- `roomId`는 deps에 넣어야 하는데
- 같은 함수에서 쓰는 `serverUrl`은 안 넣어도 된다 — 왜?
- "reactive가 뭔지"가 흐릿하면 매번 헷갈린다
- 이 한 줄 차이가 전체 동기화 흐름을 결정한다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S5.2" -->

## Reactive vs Non-reactive — 분류표

| 분류 | 예시 | deps 필요? |
|---|---|---|
| Reactive | props, state, context, body에서 derived | ✅ 필수 |
| Non-reactive | 모듈 상수, 컴포넌트 밖 함수 | ❌ 불필요 |
| Non-reactive | `ref.current` (mutable, 추적 X) | ❌ 불필요 |
| Non-reactive | 외부 mutable global (location 등) | ❌ (필요시 useSyncExternalStore) |

판정 기준: "다음 렌더에 다른 값일 수 있나?" → Yes면 reactive

---

<!-- beat: b3 -->
<!-- _footer: "LO-S5.2" -->

## roomId vs serverUrl — 한 줄 차이

```jsx
// ✅ serverUrl은 컴포넌트 밖 상수 → non-reactive
const serverUrl = 'https://localhost:1234';
function ChatRoom({ roomId }) {
  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.connect();
    return () => c.disconnect();
  }, [roomId]); // serverUrl 생략 OK
}

// 🔁 state로 옮기면 reactive 됨 → deps에 추가
const [serverUrl, setServerUrl] = useState('https://...');
useEffect(() => { /* ... */ }, [roomId, serverUrl]);
```

---

<!-- beat: b4 -->
<!-- _footer: "LO-S5.3" -->

## React는 어떻게 재실행을 결정하나

- 매 렌더마다 deps 배열을 보관: 첫 렌더 `['general']`, 다음 `['travel']`
- 두 배열을 같은 위치끼리 **`Object.is`** 로 한 칸씩 비교
- `Object.is('general', 'travel')` → false → cleanup → 새 Effect 본체
- 전부 true면 아무 일 없음 (재동기화 X)
- 객체·함수는 **참조 비교** → 매 렌더 새 객체는 무한 재동기화의 원인

---

<!-- beat: b5 -->
<!-- _footer: "LO-S5.3" -->

## 재연결 시퀀스 — 6단계

```jsx
// 1) 사용자 'travel' 클릭 → setRoomId('travel')
// 2) ChatRoom 함수 재호출, 새 closure, deps=['travel']
// 3) React: Object.is('general', 'travel') → false
// 4) 이전 cleanup 실행 → 'general' disconnect
// 5) 새 Effect 본체 실행 → 'travel' connect
// 6) UI 선택 방과 연결이 항상 일치 ✅
```

핵심: 이전 렌더의 cleanup이 다음 렌더의 본체보다 **먼저** 호출된다

---

<!-- beat: b6 -->
<!-- _footer: "LO-S5.3" -->

## 빈 `[]` deps의 진짜 의미

- ✅ "이 Effect는 어떤 reactive 값도 안 읽으므로 재동기화가 필요 없다"
- ❌ 흔한 오해: "한 번만 실행하라는 뜻"
- 안에서 props/state를 읽고 있으면 linter가 즉시 잡는다 — 거짓 주장이니까
- 정당한 `[]`: 모든 의존이 컴포넌트 밖 const거나, 외부 reactive를 안 읽는 Effect

---

<!-- beat: b7 -->

## 자문자답 — derived 값은?

```jsx
function ChatRoom({ roomId }) {
  const greeting = `Welcome to ${roomId}`;
  useEffect(() => { use(greeting); }, [???]);
}
```

- 정답: `[roomId]` — derived 값은 그 출처(reactive)만 넣으면 충분
- 보너스: `[greeting]`도 무해 (값이 같으면 `Object.is` true → 재동기화 X)

---

<!-- beat: b8 -->

## 정리 — 세 줄

- ✅ Reactive = 렌더마다 달라질 수 있는 값(props/state/derived)
- ✅ React는 deps를 `Object.is`로 한 칸씩 비교 → cleanup→재실행 결정
- ✅ `[]`는 "한 번 실행"이 아니라 "재동기화 조건 없음"이라는 주장
