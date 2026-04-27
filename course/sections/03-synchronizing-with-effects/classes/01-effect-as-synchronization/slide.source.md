---
marp: true
theme: default
paginate: true
footer: "LO-S3.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 20px; }
---

<!-- beat: b1 -->

# Effect는 라이프사이클이 아니라 동기화다

S3.C1 · LO-S3.1

- "mount/update/unmount 훅"으로 외운 분, 솔직히 손!
- 그 멘탈모델로는 의존성·더블 호출이 매번 막힌다
- 오늘은 정의 자체를 바꾼다 — Effect = **동기화**

---

<!-- beat: b2 -->

## Effect는 무엇인가 — 재정의

- **렌더링 자체가 일으키는 부수효과** (이벤트 핸들러도, 순수 렌더도 아님)
- 라이프사이클 비유는 "한 번만 실행"이라는 잘못된 직관을 만든다
- 새 정의: **컴포넌트가 화면에 떠 있는 동안 외부 시스템과의 연결을 유지하는 코드**
- 외부 시스템 = DOM 노드, 서버 connection, 타이머, 구독, 브라우저 API

---

<!-- beat: b3 -->

## 핵심 비유 — 메시지 vs 연결

- **메시지 한 통 보내기** = 이벤트 핸들러 (특정 클릭/입력에 1회 반응)
- **전화 연결 유지하기** = Effect (컴포넌트가 보이는 동안 계속 동기화)
- "언제 실행되나"가 아니라 "**무엇과 무엇을 동기화하나**"를 먼저 묻는다

---

<!-- beat: b4 -->

## 예제 — VideoPlayer 동기화

```jsx
function VideoPlayer({ src, isPlaying }) {
  const ref = useRef(null);
  // isPlaying(React state) ↔ DOM video 상태를 일치시킨다
  useEffect(() => {
    if (isPlaying) ref.current.play();
    else ref.current.pause();
  }, [isPlaying]);
  return <video ref={ref} src={src} loop />;
}
```

- 렌더 중 `ref.current.play()` 호출은 폭발 — DOM은 commit 후에야 존재
- isPlaying이 그대로면 다른 prop 변경에도 아무 일 안 일어남

---

<!-- beat: b5 -->

## 대조 — 메시지 보내기는 Effect가 아니다

- 트리거가 **사용자 클릭**이므로 `onClick`에 들어가야 정상
- useEffect에 넣으면? 재렌더마다 메시지 중복 발송
- 판별 질문: "이 동작은 **사용자 액션** 때문인가, **화면이 떠 있어서**인가?"

```jsx
// X  매 렌더마다 발송
useEffect(() => { sendMessage(); });
// O  클릭 시점에만
<button onClick={sendMessage}>Send</button>
```

---

<!-- beat: b6 -->

## 자가 진단 — Effect인가, 핸들러인가?

- "구매 완료 토스트" → **핸들러** (클릭 액션이 트리거)
- "채팅방 입장 시 서버 연결 유지" → **Effect** (보이는 동안 유지)
- "isOpen=true일 때 모달 input에 focus" → **Effect** (state ↔ DOM 동기화)

---

<!-- beat: b7 -->

## Recap — 오늘의 한 줄

- Effect = 라이프사이클 훅 X, **외부 시스템과의 동기화** O
- 메시지(이벤트) vs 연결(Effect) — "왜 실행돼야 하나"부터 묻는다
- VideoPlayer처럼 **state ↔ 외부 세계가 어긋날 때 자동으로 맞추는 도구**
- 다음 — 의존성 배열과 cleanup으로 "언제 다시 돌릴지" 결정한다
