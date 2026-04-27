---
marp: true
theme: default
paginate: true
footer: "LO-S3.4"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 20px; }
---

<!-- beat: b1 -->

# Strict Mode 더블 호출과 ref 안티패턴

S3.C3 · LO-S3.4

- "✅ Connecting..." 로그가 **두 번** 찍힌다 — mount는 한 번이었는데?
- Stack Overflow 단골 — "React 버그 아니냐"며 ref로 막으려는 분들
- 스포일러: 이건 **버그가 아니라 cleanup 채점 자동 테스트**

---

<!-- beat: b2 -->

## Strict Mode란

- `<StrictMode>` 트리에서 **dev 빌드에만** 동작 (production 영향 없음)
- 그중 하나가 "마운트 → 즉시 unmount → 다시 마운트" 시뮬레이션
- 그래서 Effect 흐름이 **setup → cleanup → setup**으로 보인다
- production은 setup 1회, unmount 시 cleanup 1회 — 가짜 cleanup은 사라진다

---

<!-- beat: b3 -->

## 왜 일부러 두 번 호출하나

- 목적: "**내 Effect가 cleanup 없이도 우연히 동작했는지**"를 들춰낸다
- cleanup이 정확하면 → setup→cleanup→setup 후에도 살아있는 연결은 **1개**
- cleanup이 빠졌으면 → 두 번째 setup 후 **연결 2개** (즉시 발견)
- 관점 전환: 더블 호출은 React의 **채점표**다

---

<!-- beat: b4 -->

## 예제 — chat connection

```jsx
// X  cleanup 없음 — dev 콘솔: ✅ ✅ (Disconnected 안 보임)
useEffect(() => {
  const c = createConnection();
  c.connect();
}, []);

// O  cleanup 추가 — 콘솔: ✅ ❌ ✅ (살아있는 건 1개)
useEffect(() => {
  const c = createConnection();
  c.connect();
  return () => c.disconnect();
}, []);
```

- Strict Mode가 production 가기 전 "cleanup 빠짐"을 잡아준 셈

---

<!-- beat: b5 -->

## 안티패턴 — didMount ref로 회피

```jsx
function ChatRoom() {
  const ran = useRef(false);
  useEffect(() => {
    if (ran.current) return;   // 🚩 두 번째 setup 차단
    ran.current = true;
    createConnection().connect(); // cleanup 없음
  }, []);
}
```

- 겉보기엔 깔끔 — "✅ Connecting..."이 한 번만 찍힌다
- 진짜 문제: cleanup 여전히 없음 + `ran.current`는 **영구 플래그**
- 라우트 복귀·탭 전환 시 unmount/remount → **좀비 연결 누적**

---

<!-- beat: b6 -->

## 옳은 처방 — cleanup 견고화 체크리스트

- 증상(로그 두 번)을 가린 게 아니라 **진짜 병**(cleanup 부재)을 두면 사고 난다
- 원칙: "Strict Mode를 만족시키지 말고, **cleanup 자체를 견고하게**"
- ✅ 시작한 모든 효과에 **짝**이 있는가?
- ✅ 두 번 setup해도 살아있는 리소스는 **1개**인가?
- ✅ unmount → remount 시도에 **누수 없는가**?

---

<!-- beat: b7 -->

## 자가 진단 — PR 리뷰

- 동료가 didMount ref PR을 올렸다 → **라우트 복귀·탭 전환 시 좀비 연결** 시나리오로 반대
- 콘솔에 ✅✅만 보이고 ❌가 없다면? → **cleanup return 누락**
- production 사용자에게 영향이 가는가? → Strict Mode는 영향 없음, 그러나 **cleanup 부재 버그는 production unmount에서 그대로 누수**

---

<!-- beat: b8 -->

## Recap — 섹션 S3 마무리

- Dev 더블 호출 = 버그 X, **cleanup 채점표** O
- ref guard로 막는 건 증상 가리기 — 실제 unmount/remount에서 폭발
- 옳은 길: cleanup을 **짝·멱등·누수 없음**으로 견고화 → 더블 호출은 조용히 통과
- 다음 섹션 S4 — **"Effect 안 써도 되는 12가지 안티패턴"** 진단으로
