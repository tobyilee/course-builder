---
marp: true
theme: default
paginate: true
footer: "LO-S6.2 · LO-S6.4"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# `useEffectEvent`로 non-reactive 추출

## theme/roomId 패턴

LO-S6.2 · LO-S6.4 · 알림은 최신 theme로, 재연결은 roomId만

---

<!-- beat: b1 -->

## 테마 토글했을 뿐인데 채팅이 끊긴다?

- 다크/라이트 토글 → "Disconnected... Reconnecting..." 반복
- 사용자도 개발자도 처음엔 의아하다
- 원인: `theme`이 deps에 있어 토글마다 disconnect→reconnect
- 처방 한 줄 예고: **`useEffectEvent`로 non-reactive만 잘라내기**

---

<!-- beat: b2 -->

## Before — '올바른 deps', '잘못된 동작'

```jsx
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.on('connected', () => {
    showNotification('Connected!', theme);
  });
  c.connect();
  return () => c.disconnect();
}, [roomId, theme]); // exhaustive-deps 룰대로
```

알림은 `theme`을 **읽지만**, 그 때문에 **재연결될 이유는 없다**.
→ Effect 안에 reactive와 non-reactive가 섞여 있다.

---

<!-- beat: b3 -->

## `useEffectEvent` — 4가지 특성

```jsx
import { useEffectEvent } from 'react'; // experimental
```

- Event handler처럼 **non-reactive**
- 호출 시 **항상 최신** props/state를 본다
- **Effect 안에서만** 호출
- **deps에 올리지 않는다** (linter도 요구 안 함)

> "Effect 안에 끼워 넣는 작은 event handler"

⚠️ **실험적 API** — react.dev 기준 패턴으로 다룸

---

<!-- beat: b4 -->

## After — theme를 읽되, theme에 반응하지 않는다

```jsx
const onConnected = useEffectEvent(() => {
  showNotification('Connected!', theme); // 항상 최신
});

useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.on('connected', () => onConnected());
  c.connect();
  return () => c.disconnect();
}, [roomId]); // theme 빠짐
```

테마 토글 → 연결 유지 / `roomId` 변경 → 재연결.
**"읽는다 ≠ 반응한다"** — 그 경계를 만들어준다.

---

<!-- beat: b5 -->

## 두 번째 시나리오 — Page 방문 로깅

```jsx
const onVisit = useEffectEvent(visitedUrl => {
  logVisit(visitedUrl, numberOfItems); // 카트 길이는 최신값 직접
});

useEffect(() => {
  onVisit(url); // url은 인자로 — reactive
}, [url]);
```

- 원하는 동작: `url` 변경에만 재발화, 카트 변경엔 X
- **원칙**: reactive 값은 **인자로**, non-reactive는 **본체에서 직접**

---

<!-- beat: b6 -->

## 자문자답 — `roomId`도 메시지에 넣고 싶다면?

- 요구: 알림에 roomId 표시 + roomId 바뀌면 재연결
- `roomId`는 **재연결 트리거** → reactive → **인자로**
- `theme`은 그대로 **non-reactive** → **본체에서 직접**
- 사고 순서: **"재발화 조건이 뭔가?"** → 그 값만 인자/deps로
- 실습: react.dev 예제에서 직접 토글해보기

---

<!-- beat: b7 -->

## 정리 — 세 원칙

- ✅ `useEffectEvent` = Effect 안에 끼우는 **non-reactive 핸들러**
- ✅ non-reactive는 추출, reactive만 deps에
- ✅ **reactive → 인자, non-reactive → 본체 직접**

⚠️ 실험적 API — 다음 시간엔 **제약과 안티패턴**
