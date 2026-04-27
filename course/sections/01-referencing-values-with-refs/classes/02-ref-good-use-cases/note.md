# Ref의 좋은 사용 사례 — timeout, 디바운싱, 최신 값

> LOs: LO-S1.3

## 개요

지난 시간 [S1.C1]에서 "비-렌더 데이터는 ref"라는 규칙을 손에 넣었습니다. 그런데 막상 코드를 짜다 보면 "이 데이터가 정말 비-렌더인가?"가 헷갈립니다 [slide 1]. 오늘은 빈출 시나리오 셋 — Stopwatch, 디바운싱, 비동기 콜백 최신 값 — 을 직접 작성하면서 매번 "왜 state가 아니라 ref인가"를 짚어봅니다.

## 핵심 개념

ref가 정답인 자리에는 공통점이 있습니다. (1) 그 값이 바뀌어도 화면이 다시 그려질 필요가 없고, (2) 컴포넌트 인스턴스마다 따로 가져야 하며, (3) 렌더 사이 보존되어야 합니다. 이 셋이 만나면 ref입니다 [slide 5]. 특히 setTimeout/setInterval ID는 그 자체로 의미가 없는 단순 "cancel용 핸들"이라서 화면과 무관 — 전형적 ref 후보죠.

state와 ref를 **함께** 쓰는 경우도 있습니다. 표시 값이면서 비동기 콜백에서 최신을 읽어야 한다면, 같은 데이터를 state(렌더용)와 ref(콜백용)에 동기화해 양쪽 요구를 모두 만족시킵니다.

## 예시

**1. Stopwatch — 분리 패턴** [slide 2]

```js
const [startTime, setStartTime] = useState(null);
const [now, setNow] = useState(null);     // 화면에 보임 → state
const intervalRef = useRef(null);          // ID는 안 보임 → ref

function handleStart() {
  setStartTime(Date.now()); setNow(Date.now());
  clearInterval(intervalRef.current);
  intervalRef.current = setInterval(() => setNow(Date.now()), 10);
}
function handleStop() { clearInterval(intervalRef.current); }
```

**2. 디바운싱 — 인스턴스별 격리** [slide 3]

```js
function DebouncedButton({ onClick, children }) {
  const timeoutRef = useRef(null); // 인스턴스마다 자기 ref
  return <button onClick={() => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClick, 1000);
  }}>{children}</button>;
}
```

전역 `let timeoutID`로 두면 버튼 A의 새 timeout이 버튼 B의 ID를 덮어쓰지만, ref는 컴포넌트 인스턴스마다 자기만의 `{ current }`를 가져 충돌이 없습니다.

**3. 비동기 콜백 최신 값** [slide 4]

```js
const [text, setText] = useState('');
const textRef = useRef(text);
function handleChange(e) {
  setText(e.target.value);
  textRef.current = e.target.value; // 거울처럼 동기 유지
}
function handleSend() {
  setTimeout(() => alert(textRef.current), 3000); // 최신 값!
}
```

state만 쓰면 setTimeout 콜백은 클로저에 갇힌 옛 snapshot을 읽습니다. ref를 함께 두면 콜백은 항상 최신 값을 봅니다.

## 흔한 실수

- **전역 변수로 timeout 관리**: 모듈 최상단의 `let timeoutID`는 모든 인스턴스가 공유하므로 인스턴스 간 cancel이 충돌합니다. 동일 컴포넌트가 두 곳에 렌더되는 순간 버그가 됩니다.
- **ref 동기화를 잊는 실수**: 비동기 최신 값 패턴에서 `setText`는 호출했는데 `textRef.current = ...`를 빼먹으면, 콜백은 여전히 옛 값을 봅니다. setter와 ref 대입은 항상 같이 다닌다고 외워두세요.

## 복습

Stopwatch는 표시 값(state)과 인터벌 ID(ref)를 분리해 한 컴포넌트에서 공존시킵니다. 디바운싱은 인스턴스별 격리가 필요하므로 ref만이 정답이고, 비동기 최신 값은 state+ref 동기화로 양쪽 모두 만족시킵니다. 다음 [S1.C3]에서는 이 패턴들을 잘못 적용했을 때 생기는 안티패턴과 그 처방을 봅니다.
