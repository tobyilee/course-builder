---
marp: true
theme: default
paginate: true
footer: "LO-S7.3"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# 전략 1-3

## 정적값 외부화 · 객체 안에서 · updater

LO-S7.2 / LO-S7.3 · Effect 의존성 줄이기 6 전략 (1/2)

---

<!-- beat: b1 -->

## 1초마다 깜빡이는 타이머 — 본 적 있죠?

- 화면이 매 초마다 리셋되며 깜빡인다
- 원인: `setInterval`이 매 tick마다 재생성되고 있다
- cleanup → 새 interval → cleanup → 새 interval 무한 반복
- 이번 class의 3 전략으로 깔끔히 해결합니다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S7.2" -->

## 전략 1 — 진짜 상수는 컴포넌트 밖으로

```jsx
// 컴포넌트 밖 — module scope, 비-reactive
const serverUrl = 'https://localhost:1234';
const roomId = 'music';

function ChatRoom() {
  useEffect(() => {
    createConnection(serverUrl, roomId);
  }, []); // ← linter도 만족
}
```

- 신호: "절대 안 바뀌는 값이 왜 deps에?"
- 주의: prop/state는 절대 밖으로 옮길 수 없음

---

<!-- beat: b3 -->
<!-- _footer: "LO-S7.2" -->

## 전략 2 — 객체/함수는 Effect 안에서 만든다

```jsx
// Before: options가 매 렌더 새 참조 → 무한 재연결
const options = { serverUrl, roomId };
useEffect(() => createConnection(options), [options]);

// After: 원시값 roomId만 deps
useEffect(() => {
  const options = { serverUrl, roomId };
  createConnection(options);
}, [roomId]);
```

- 원시값은 `Object.is` 비교에서 안정 → 재연결 폭주 사라짐

---

<!-- beat: b4 -->
<!-- _footer: "LO-S7.3" -->

## 전략 3 — updater로 의존성을 끊는다

```jsx
// Before: messages를 읽기 위해 deps에 추가
c.on('message', m => setMessages([...messages, m]));
// deps: [roomId, messages] ← 매 메시지마다 재실행

// After: prev로 최신값 받기 → messages 제거
c.on('message', m => setMessages(prev => [...prev, m]));
// deps: [roomId]
```

- 신호: 누적·토글·카운트업처럼 '쓰기 위해 읽는' 패턴

---

<!-- beat: b5 -->
<!-- _footer: "LO-S7.3" -->

## 타이머 Before/After — 한 줄로 두 문제 해결

```jsx
// Before — count 변경마다 cleanup/재등록 반복
useEffect(() => {
  const id = setInterval(() => setCount(count + 1), 1000);
  return () => clearInterval(id);
}, [count]);

// After — mount 시 한 번만 등록
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000);
  return () => clearInterval(id);
}, []);
```

closure 캡처 + 재생성 문제 동시 해결

---

<!-- beat: b6 -->
<!-- _footer: "LO-S7.2" -->

## 미니 연습 — 적용 전략은?

- (a) `const config = { apiKey: 'fixed' }`를 컴포넌트 안에 → ?
- (b) `deps=[onClick]`인데 부모가 매 렌더 새 함수 prop → ?
- (c) `setScore(score + bonus)` 때문에 score가 deps에 → ?

힌트: 1 = 밖으로, 2 = Effect 안에서, 3 = updater

---

<!-- beat: b7 -->
<!-- _footer: "LO-S7.3" -->

## 정리 — 세 전략 한 줄씩

- 전략 1 — 진짜 상수는 컴포넌트 **밖**으로
- 전략 2 — 객체/함수는 Effect **안**에서, 원시값만 deps
- 전략 3 — state 읽기만이면 **updater**로 의존성을 끊는다
