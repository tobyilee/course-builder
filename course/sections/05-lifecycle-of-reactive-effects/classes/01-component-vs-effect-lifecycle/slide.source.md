---
marp: true
theme: default
paginate: true
footer: "LO-S5.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# 컴포넌트 vs Effect 라이프사이클

## 매 렌더는 자기만의 closure를 가진다

LO-S5.1 · 반응형 Effect의 라이프사이클

---

<!-- beat: b1 -->

## 방을 바꾸면 무슨 일이 벌어질까?

- ChatRoom은 마운트된 채로 살아있는데
- 사용자가 `general` → `travel` → `music`으로 옮긴다
- 연결은 끊고-맺기를 두 번 반복한다
- "Effect = mount/unmount 훅"으로는 설명이 안 된다

---

<!-- beat: b2 -->

## 두 개의 사이클이 겹쳐 흐른다

- **컴포넌트 라이프사이클**: mount → update → unmount (한 번의 일생)
- **Effect 라이프사이클**: 그 안에서 동기화 시작 ↔ 중지 반복
- Effect를 볼 땐 두 질문만: "어떻게 시작? 어떻게 중지?"
- 이 관점이면 deps · cleanup · 더블 호출이 한 줄에 꿰인다

---

<!-- beat: b3 -->

## 매 렌더 = 자체 closure

- 함수 컴포넌트는 렌더마다 처음부터 다시 호출된다
- 그 호출에서 만든 변수·함수는 그 시점의 props/state를 캡처
- Effect 본문의 `roomId`는 "그 렌더의 스냅샷"
- 그래서 "매 렌더는 자기만의 Effect를 가진다"

---

<!-- beat: b4 -->

## ChatRoom 재연결 시퀀스

```jsx
const serverUrl = 'https://localhost:1234';

function ChatRoom({ roomId }) {
  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.connect();
    return () => c.disconnect();
  }, [roomId]);
}
```

`render('general')` → connect general → `render('travel')` → **disconnect general** → connect travel

---

<!-- beat: b5 -->

## 자문자답 — 몇 번 호출됐을까?

- ChatRoom이 마운트된 채로 `general` → `travel` → `music`
- **connect는 몇 번? disconnect는 몇 번?**
- 정답: connect 3번, disconnect 2번 (마지막은 unmount 시 호출)
- 만약 Effect가 정말 'mount 훅'이라면 이 횟수가 어떻게 달라질까?

---

<!-- beat: b6 -->

## 정리 — 세 줄

- ✅ 컴포넌트는 일생을 살고, Effect는 그 안에서 시작/중지를 반복
- ✅ Effect를 볼 땐 "어떻게 시작? 어떻게 중지?"만 묻는다
- ✅ 매 렌더는 자체 closure이며, 그래서 자체 Effect를 가진다
