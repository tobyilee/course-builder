---
marp: true
theme: default
paginate: true
footer: "LO-S7.5"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 20px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# 실전 케이스 스터디

## 6 전략 조합 선택과 트레이드오프 평가

LO-S7.5 · Effect 의존성 줄이기 마무리

---

<!-- beat: b1 -->

## 오늘의 환자 — 재연결이 너무 많은 ChatRoom

- 메시지가 도착할 때마다 재연결
- 부모가 리렌더할 때마다 재연결
- isMuted 토글마다 재연결
- 어느 전략 조합이 최적이고, 그 비용은?

---

<!-- beat: b2 -->

## 평가 절차와 트레이드오프 3축

- **절차**: 증상 → 원인 → 후보 전략 → 조합 평가 → 결정
- **가독성**: 코드를 읽는 사람의 비용
- **캡슐화**: 자식이 자율적인지, 부모에 의존하는지
- **마이그레이션 비용**: 기존 호출부를 얼마나 건드려야 하는지

황금률: '코드를 바꿔 deps를 정직하게' — 어느 코드를 바꿀지가 결정

---

<!-- beat: b3 -->

## ChatRoom Before — 증상 진단

```jsx
function ChatRoom({ options, isMuted }) {
  useEffect(() => {
    const c = createConnection(options);
    c.on('message', m => {
      setMessages([...messages, m]);
      if (!isMuted) playSound();
    });
    c.connect();
    return () => c.disconnect();
  }, [options, messages, isMuted]); // ← 셋 다 매번 바뀜
}
```

- options(객체 prop) · messages(누적) · isMuted(비반응) — 셋 다 재연결 유발

---

<!-- beat: b3 -->

## ChatRoom After — 전략 3·4·6 조합

```jsx
function ChatRoom({ roomId, serverUrl, isMuted }) {  // ⑥ 원시값
  const onMessage = useEffectEvent(m => {            // ④ EffectEvent
    if (!isMuted) playSound();
  });
  useEffect(() => {
    const c = createConnection({ serverUrl, roomId });
    c.on('message', m => {
      setMessages(prev => [...prev, m]);             // ③ updater
      onMessage(m);
    });
    c.connect();
    return () => c.disconnect();
  }, [roomId, serverUrl]);
}
```

진짜 재연결이 필요한 시점에만 재연결

---

<!-- beat: b4 -->

## 트레이드오프 비교표

| 전략 | 가독성 | 캡슐화 | 마이그레이션 비용 |
|---|---|---|---|
| ③ updater | ★★★ | ★★★ | 거의 0 — 최우선 후보 |
| ④ useEffectEvent | ★★ | ★★★ | 낮음 (실험적 API 위험) |
| ⑥ 원시값 분해 | ★★★ | ★★ | 높음 — 부모 호출부 수정 |
| (대안) ② Effect 안 생성 | ★ | ★★★ | 0 — 추상화는 잃음 |

선택 기준: '재연결이 의미상 필요한 시점'을 정의하고 deps를 그것과 일치시키기

---

<!-- beat: b5 -->

## 시나리오 자문자답 — Form 컴포넌트

```jsx
<Form onSubmit={(d) => save(d)}
      initialValues={{ name: '', age: 0 }} />
```

- 부모 리렌더마다 Form이 reset 됨 — 어느 조합?
- initialValues(객체 prop) → ⑥ 또는 ②
- onSubmit(인라인 함수) → ④ useEffectEvent로 wrap
- 호출부 적으면 ⑥, 많으면 ④+② — 합리적 근거가 핵심

---

<!-- beat: b6 -->

## 섹션 종합 — 문제 → 해결 매핑

| 문제 신호 | 해결 전략 |
|---|---|
| deps 너무 많음 | ① 외부화 / ② Effect 안 생성 |
| 무한 루프 | ③ updater |
| 읽기만 하고 싶음 | ④ useEffectEvent |
| 매 렌더 재생성 | ② / ⑥ |
| 여러 동기화 묶임 | ⑤ 분리 |
| suppress 유혹 | 절대 금지 — 위 6개 사용 |

다음 — S8 Custom Hook으로 6 전략을 도메인 의미로 묶습니다
