---
marp: true
theme: default
paginate: true
footer: "LO-S3.2 · LO-S3.3"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 19px; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# 시그니처, 의존성, cleanup

S3.C2 · LO-S3.2 · LO-S3.3

- 지난 시간: Effect는 **동기화**다
- 그럼 "**언제, 얼마나 자주**"는 누가 정하나? → **deps**
- 동기화의 다른 절반 — "이전 연결을 끊는" **cleanup**

---

<!-- beat: b2 -->
<!-- _footer: "LO-S3.2" -->

## useEffect(setup, deps?) — deps 3가지 형태

| deps        | 실행 시점                       |
| ----------- | ------------------------------- |
| 생략        | **매 렌더 후** (대부분 잘못된 신호) |
| `[]`        | **마운트 1회** (dev에선 2회로 보임)  |
| `[a, b]`    | 마운트 + a/b가 `Object.is` 변경 시 |

- deps는 "내가 고르는 값"이 아니라 **Effect 안에서 읽는 reactive 값을 그대로 적은 것**

---

<!-- beat: b3 -->
<!-- _footer: "LO-S3.2" -->

## 시연 — 동기화 빈도 다이얼

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  const [other, setOther] = useState(0);

  useEffect(() => { console.log('run'); });        // 매 렌더
  useEffect(() => { console.log('run'); }, []);    // 1회
  useEffect(() => { console.log('run'); }, [count]); // count 변경 시
  // ...
}
```

- 같은 코드, deps만 다르면 호출 빈도가 **다이얼처럼** 바뀐다

---

<!-- beat: b4 -->
<!-- _footer: "LO-S3.3" -->

## Cleanup — 동기화의 나머지 절반

- **setup이 return하는 함수**가 cleanup
- 호출 시점: ① unmount 시, ② **다음 setup 직전** (deps 변경 재실행 전)
- 역할: "이전 동기화"가 만든 효과를 깨끗하게 거둔다
- 패턴은 항상 **한 쌍**: connect/disconnect, add/remove, 시작/취소

---

<!-- beat: b5 -->
<!-- _footer: "LO-S3.3" -->

## 패턴 1 — Chat connection

```jsx
useEffect(() => {
  const conn = createConnection(roomId);
  conn.connect();
  return () => conn.disconnect();
}, [roomId]);
```

- 방을 옮기면 cleanup이 옛 방을 끊고 새 방을 연결
- cleanup이 빠지면? **N개 방에 동시 접속 — 좀비 연결**
- "메시지가 자꾸 두 번씩 오는" production 사고의 단골 원인

---

<!-- beat: b6 -->
<!-- _footer: "LO-S3.3" -->

## 패턴 2·3 — Listener / Animation

```jsx
useEffect(() => {
  const handler = () => { /* ... */ };
  window.addEventListener('scroll', handler);
  return () => window.removeEventListener('scroll', handler);
}, []);
```

- `removeEventListener`는 **같은 함수 참조**여야 동작
- 애니메이션도 동일 — 시작 후 cleanup에서 `cancelAnimationFrame` 또는 원복
- 공통: "시작한 효과를 **정확히 같은 손으로** 거둔다"

---

<!-- beat: b7 -->
<!-- _footer: "LO-S3.3" -->

## 패턴 4 — Fetch race condition

```jsx
useEffect(() => {
  let ignore = false;
  fetchResults(query).then(r => {
    if (!ignore) setData(r);
  });
  return () => { ignore = true; };
}, [query]);
```

- 빠르게 바뀐 query가 **늦은 응답**에 덮이는 사고를 막는다
- 이전 query의 cleanup이 `ignore=true`로 만들어 폐기
- `AbortController.abort()`도 같은 의도

---

<!-- beat: b8 -->

## 자가 진단 — 어디가 잘못됐나

- `useEffect(() => { setInterval(tick, 1000); }, [])` → cleanup에 **clearInterval 없음**
- 같은 코드 deps `[tick]` 이면? → tick 바뀔 때마다 정리하고 재시작
- 자동완성 race condition 처방 → cleanup에 `ignore = true` 또는 `controller.abort()`

---

<!-- beat: b9 -->

## Recap — 오늘의 한 줄

- deps = 동기화 **빈도 다이얼**: 생략 / `[]` / `[a,b]`
- cleanup = 동기화의 나머지 절반 — "**같은 손으로 거둔다**"
- 4가지 패턴: **connect/disconnect, add/remove, animation reset, fetch ignore**
- 다음 — Strict Mode 더블 호출의 의도와 ref 회피 안티패턴
