---
marp: true
theme: default
paginate: true
footer: "LO-S6.3"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# Effect Event의 제약과 안티패턴

## 외부에 노출 금지

LO-S6.3 · 강력한 만큼 사용처가 좁다

---

<!-- beat: b1 -->

## 너무 편해서 아무 데나 쓰고 싶지만…

- 지난 시간의 `useEffectEvent` — 강력하다
- 잘못 쓰면 React가 **추적하지 못하는 코드**가 된다
- 흔한 시도: `useTimer(onTick, 1000)` 처럼 외부로 넘기기
- 오늘은 **"쓰지 말아야 할 곳"** 을 명확히 긋는다

---

<!-- beat: b2 -->

## 제약 3가지

- 🚫 **Effect 안에서만 호출** — 렌더 중·핸들러에서 호출 금지
- 🚫 **다른 컴포넌트/Hook에 인자로 전달 금지**
- 🚫 **Effect deps에 포함 금지** (어차피 매 렌더 새로 생성 → 무한 루프)

> Effect Event는 **reactive 흐름에서 분리된 섬** —
> 외부로 새어나가면 추적 불가.

**사용처 동거 원칙**: 정의한 곳에서만 쓴다.

---

<!-- beat: b3 -->

## 안티패턴 → 리팩터링 (Timer)

```jsx
// ❌ Before: Timer가 onTick을 외부로 넘김
function Timer() {
  const [count, setCount] = useState(0);
  const onTick = useEffectEvent(() => setCount(c => c + 1));
  useTimer(onTick, 1000); // 다른 Hook에 전달 — 위반
}
```

```jsx
// ✅ After: useTimer 안에 useEffectEvent를 동거
function useTimer(callback, delay) {
  const onTick = useEffectEvent(() => callback());
  useEffect(() => {
    const id = setInterval(() => onTick(), delay);
    return () => clearInterval(id);
  }, [delay]); // onTick은 deps에 X
}
function Timer() {
  useTimer(() => setCount(c => c + 1), 1000); // 깔끔
}
```

---

<!-- beat: b4 -->

## Naming — 'on + 사건'

| ✅ 권장 | ❌ 지양 |
|---|---|
| `onMessage` | `onMount` |
| `onTick` | `onUpdate` |
| `onVisit` | `onAfterRender` |
| `onConnected` | `onEffect` |

- "suppress 대신 `useEffectEvent`" — non-reactive로 만들 부분은 **명시적 추출**
- lifecycle 어휘는 **잘못된 멘탈 모델**을 유도
- 이름은 **"무슨 사건이 일어났나"** 를 가리키도록

---

<!-- beat: b5 -->

## 자문자답 — 어디가 잘못인가?

```jsx
function Parent({ onSearch }) {
  const onSearchEvent = useEffectEvent(onSearch);
  useChild(onSearchEvent); // ❓
}
```

- 진단: **"다른 Hook에 인자로 전달"** 제약 위반
- 수정: `useChild(onSearch)` → 자식 Hook 내부에서 wrap

```jsx
function useChild(onSearch) {
  const onSearchEvent = useEffectEvent(onSearch); // 사용처 동거
  useEffect(() => { /* onSearchEvent() */ }, [/* ... */]);
}
```

체크리스트: ① Effect 안에서만? ② 외부 전달 X? ③ deps 제외? ④ 이름이 사건 형?

---

<!-- beat: b6 -->

## 정리 — 제약 + S6 마무리

- ✅ 제약 3: Effect 안에서만 / 외부 전달 금지 / deps에 안 넣기
- ✅ 처방: **사용처(Hook)에 `useEffectEvent`를 동거**
- ✅ Naming: `on + 사건` ✓ / lifecycle 어휘 ✗

⚠️ **실험적(experimental) API** — production 사용 신중,
채택 시점에 따라 **import 경로가 달라질 수 있음**

> S6 흐름: **결정 질문 → useEffectEvent 추출 → 제약 준수**
