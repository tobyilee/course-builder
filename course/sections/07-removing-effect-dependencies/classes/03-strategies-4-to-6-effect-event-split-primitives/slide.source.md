---
marp: true
theme: default
paginate: true
footer: "LO-S7.4"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# 전략 4-6

## useEffectEvent · 분리 · 원시값 분해

LO-S7.2 / LO-S7.4 · Effect 의존성 줄이기 6 전략 (2/2)

---

<!-- beat: b1 -->
<!-- _footer: "LO-S7.2" -->

## 두 가지 흔한 비명

- slider로 duration을 만질 때마다 페이드인이 처음부터 다시 시작
- 부모 리렌더마다 채팅이 끊겼다 다시 붙음
- 공통 원인: '읽고는 싶지만 반응시키긴 싫은' 값이 deps에
- 남은 3 전략으로 정복합니다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S7.2" -->

## 전략 4 — useEffectEvent로 비반응형 분리

- Effect 안에서 '읽고 싶지만 변경에 반응 안 해도 되는' 값
- `useEffectEvent(handler)`는 항상 최신 값을 보지만 reactive 아님
- deps에 넣지 않는다 (넣을 수도 없음)
- 제약: Effect 안에서만 호출, 다른 Hook/컴포넌트에 넘기지 말 것
- 신호: "이 값이 바뀌어도 동기화는 다시 안 해도 돼"

---

<!-- beat: b3 -->
<!-- _footer: "LO-S7.4" -->

## Welcome 애니메이션 — duration 케이스

```jsx
// Before: slider 만질 때마다 fade가 리셋
useEffect(() => {
  const a = new FadeInAnimation(ref.current);
  a.start(duration);
}, [duration]);

// After: duration은 useEffectEvent 안으로
const onAppear = useEffectEvent(a => a.start(duration));
useEffect(() => {
  const a = new FadeInAnimation(ref.current);
  onAppear(a);
}, []);
```

값을 읽긴 했지만 재실행 트리거에선 빠진다 — '거울 옆 메모지'

---

<!-- beat: b4 -->
<!-- _footer: "LO-S7.2" -->

## 전략 5 — 무관한 동기화는 Effect를 분리

- 신호: deps `[a, b]`에서 a 변경시 b 동기화도 같이 재실행되는 게 어색
- 예: country fetch + city fetch가 한 Effect → city 바뀔 때 country도 재실행
- 분리하면 각 Effect의 deps가 깨끗해지고 트리거가 정확해짐
- 원칙: **하나의 Effect = 하나의 동기화 목적**

---

<!-- beat: b5 -->
<!-- _footer: "LO-S7.4" -->

## 전략 6 — 객체 prop을 원시값으로 분해

```jsx
// Before — 부모 리렌더마다 새 객체 → 자식 deps 매번 달라짐
<ChatRoom options={{ serverUrl, roomId }} />
// 자식: useEffect(..., [options])

// After — 원시값 prop으로 평탄화
<ChatRoom roomId={roomId} serverUrl={serverUrl} />
// 자식: useEffect(..., [roomId, serverUrl])
```

- 원시값은 같은 값이면 `Object.is` 비교에서 안정
- 신호: "부모가 리렌더만 해도 자식 Effect 재실행됨"

---

<!-- beat: b6 -->
<!-- _footer: "LO-S7.4" -->

## ChatRoom 통합 — 전략 2 + 6 조합

```jsx
function ChatRoom({ roomId, serverUrl }) { // 원시값 prop
  useEffect(() => {
    const options = { serverUrl, roomId }; // Effect 안에서 생성
    const c = createConnection(options);
    c.connect();
    return () => c.disconnect();           // cleanup 잊지 말기
  }, [roomId, serverUrl]);
}
```

객체 참조 문제는 보통 전략 2 + 6이 함께 등장

---

<!-- beat: b7 -->
<!-- _footer: "LO-S7.2" -->

## 미니 자문자답 — 적용 전략은?

- (a) theme 토글마다 채팅 재연결 (theme은 알림 색상에만 사용) → ?
- (b) Effect 하나가 socket 연결 + 분석 로깅을 같이 함 → ?
- (c) 부모가 `onChange={() => ...}` 인라인 함수 prop → ?

힌트: 4 = useEffectEvent, 5 = 분리, 6 = 원시값 분해

---

<!-- beat: b8 -->
<!-- _footer: "LO-S7.4" -->

## 정리 — 6 전략 라인업

- ① 정적값 외부화 · ② Effect 안 생성 · ③ updater (이전 class)
- ④ useEffectEvent — 비반응형 로직 추출
- ⑤ Effect 분리 — 무관한 동기화는 떼어낸다
- ⑥ 원시값 분해 — 객체 prop을 평탄화
