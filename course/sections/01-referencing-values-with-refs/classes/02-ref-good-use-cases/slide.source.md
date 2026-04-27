---
marp: true
theme: default
paginate: true
footer: "LO-S1.3"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  pre { line-height: 1.35; }
---

<!-- beat: b1 -->

# Ref의 좋은 사용 사례

timeout · 디바운싱 · 비동기 최신 값

S1 · Class 2

---

<!-- beat: b1 -->
<!-- _footer: "LO-S1.3" -->

## 오늘은 손에 익히는 시간

- 지난 시간 규칙: **비-렌더 데이터는 ref**
- 실전에서는 "비-렌더인지" 판단이 헷갈린다
- 빈출 시나리오 셋을 코드로 직접 작성
  - Stopwatch (state + ref 분리)
  - 디바운싱 (인스턴스별 격리)
  - 비동기 콜백 최신 값 (state ↔ ref 동기화)

---

<!-- beat: b2 -->
<!-- _footer: "LO-S1.3" -->

## Stopwatch — 표시 값과 ID 분리

```js
function Stopwatch() {
  const [startTime, setStartTime] = useState(null);
  const [now, setNow] = useState(null);      // 표시 → state
  const intervalRef = useRef(null);          // ID  → ref

  function handleStart() {
    setStartTime(Date.now());
    setNow(Date.now());
    clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => setNow(Date.now()), 10);
  }
  function handleStop() { clearInterval(intervalRef.current); }
}
```

화면에 보이는 것만 state, ID는 cancel 핸들일 뿐 → ref

---

<!-- beat: b3 -->
<!-- _footer: "LO-S1.3" -->

## 디바운싱 — 인스턴스별 격리

```js
// 모듈 전역: 모든 버튼이 timeout을 공유 → 충돌
let timeoutID;

// 컴포넌트 안: 인스턴스마다 자기 { current }
function DebouncedButton({ onClick, timeout }) {
  const timeoutRef = useRef(null);
  return <button onClick={() => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClick, timeout);
  }}>...</button>;
}
```

버튼 A의 디바운싱이 버튼 B를 건드리지 않는다.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S1.3" -->

## 비동기 콜백에서 최신 값 읽기

```js
const [text, setText] = useState('');
const textRef = useRef(text);

function handleChange(e) {
  setText(e.target.value);
  textRef.current = e.target.value; // 거울 동기화
}
function handleSend() {
  setTimeout(() => alert(textRef.current), 3000); // 최신
}
```

- state snapshot은 setTimeout 클로저에 갇혀 stale
- ref는 최신 값을 동기적으로 들고 있다

---

<!-- beat: b5 -->
<!-- _footer: "LO-S1.3" -->

## 셋의 공통점 — 직접 답해보기

- 그 데이터가 바뀌면 화면이 다시 그려져야 하는가? → **NO**
- 컴포넌트 인스턴스마다 따로 가져야 하는가? → **YES**
- timeout/interval ID는 표시용인가, 그저 cancel 핸들인가? → **핸들**

공식: **비-렌더 + 인스턴스별 + 렌더 사이 보존 = ref**

---

<!-- beat: b6 -->
<!-- _footer: "LO-S1.3" -->

## Recap

- **Stopwatch** — 표시는 state, 인터벌 ID는 ref
- **디바운싱** — 전역 변수는 충돌, ref는 인스턴스별 격리
- **비동기 최신 값** — state와 ref를 같이 두고 동기 유지
- 다음 class — 이걸 잘못 쓰면? (안티패턴 진단)
