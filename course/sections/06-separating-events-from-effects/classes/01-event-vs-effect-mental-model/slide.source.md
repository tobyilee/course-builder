---
marp: true
theme: default
paginate: true
footer: "LO-S6.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# Event냐 Effect냐

## "왜 실행돼야 하나?"로 가르기

LO-S6.1 · 같은 코드, 어디에 둘지가 의미를 바꾼다

---

<!-- beat: b1 -->

## 같은 `sendMessage`, 다른 자리

- "Send 버튼 클릭" 한 번에만 보내고 싶은 메시지
- "방에 들어와 있는 동안" 계속 유지하고 싶은 연결
- 한 줄을 옮겼을 뿐인데 동작이 완전히 달라진다
- 오늘의 질문 한 줄: **"이 코드는 왜 실행돼야 하는가?"**

---

<!-- beat: b2 -->

## 결정 질문 한 줄

- **Event handler**: 사용자가 그 액션을 했기 때문에 실행
- **Effect**: 컴포넌트가 화면에 있기 때문에 실행
- 트리거의 본질이 다르다 — 인터랙션 vs 표시 상태
- 갈림길: "사용자가 했나? 화면에 있어서인가?"

---

<!-- beat: b3 -->

## Event vs Effect 비교표

| 항목 | Event Handler | Effect |
|---|---|---|
| 트리거 | 특정 인터랙션 (클릭/submit) | 컴포넌트가 표시되는 동안 |
| 반응성 | **Non-reactive** | **Reactive** (deps에 반응) |
| reactive 값 읽기 | 그 순간의 값 (스냅샷) | 값이 바뀌면 재실행 |

같은 변수도 **위치**에 따라 반응성이 달라진다.

---

<!-- beat: b4 -->

## ChatRoom — 두 자리에 같은 이름

```jsx
function ChatRoom({ roomId }) {
  const [message, setMessage] = useState('');

  function handleSendClick() {
    sendMessage(message); // Send 클릭에서만
  }

  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.connect();
    return () => c.disconnect();
  }, [roomId]); // 연결 유지
}
```

`message`는 handler에선 클릭 순간 값, Effect라면 deps가 필요해진다.

---

<!-- beat: b5 -->

## 자문자답 — 어디에 둘까?

- 검색창 입력 시 **자동완성 fetch** → handler? Effect?
- 결정 질문 적용: 타이핑(인터랙션)? 화면에 있어서?
- 정답: `query`가 바뀌면 자동 동기화 → **Effect**
- 변형: "Submit 버튼으로 form 전송" → 명백히 **handler**

---

<!-- beat: b6 -->

## 정리 — 세 줄

- ✅ Event handler = 인터랙션 응답 (**non-reactive**)
- ✅ Effect = 표시 중 동기화 (**reactive**)
- ✅ "왜 실행돼야 하나?" — 인터랙션이면 handler, 표시면 Effect
- 다음 시간 → reactive와 non-reactive가 한 Effect에 섞일 때: `useEffectEvent`
