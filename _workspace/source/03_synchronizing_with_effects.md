# Source: Synchronizing with Effects

## What is an Effect (and what it isn't)
**Effect** = 렌더링 자체가 일으키는 부수효과. 컴포넌트가 화면에 나타났을 때 외부 시스템과 동기화.
- ❌ 라이프사이클 훅 아님 (mount/update/unmount 비유는 오해 유발)
- ❌ 이벤트 핸들러 아님 (이벤트는 특정 사용자 액션에 응답)
- ❌ 순수 렌더 코드 아님

**핵심 비유**: "메시지 보내기"는 이벤트(버튼 클릭). "서버에 연결 유지"는 Effect(어떤 인터랙션이든 컴포넌트가 보이면 연결).

## useEffect 시그니처
```js
useEffect(() => {
  // 매 렌더 후 실행
});

useEffect(() => {
  // mount 시만
}, []);

useEffect(() => {
  // mount + 의존성 변경 시
}, [a, b]);
```

## 동기화 프레이밍
```js
function VideoPlayer({ src, isPlaying }) {
  const ref = useRef(null);
  useEffect(() => {
    isPlaying ? ref.current.play() : ref.current.pause();
  }, [isPlaying]);
  return <video ref={ref} src={src} loop playsInline />;
}
```
**왜 렌더 중이 아니라 Effect**: 렌더는 순수 계산이어야 하고, DOM은 commit 후에야 존재.

## Cleanup 패턴
```js
useEffect(() => {
  const connection = createConnection();
  connection.connect();
  return () => connection.disconnect(); // cleanup
}, []);
```

### 흔한 cleanup 패턴들
- **Connect/disconnect**: 채팅 서버, WebSocket
- **Subscribe**: `addEventListener` ↔ `removeEventListener`
- **Animation reset**: opacity, transform 원복
- **Fetch race-condition**: `let ignore = false; ... return () => { ignore = true; };`

## Strict Mode 더블 호출
개발 환경에선 일부러 마운트 두 번. 흐름:
1. Effect 실행 → "✅ Connecting..."
2. cleanup 실행 → "❌ Disconnected."
3. Effect 다시 실행 → "✅ Connecting..."

cleanup이 잘 동작하는지 검증. **production은 1, 3만**.

### ⚠️ Pitfall: ref로 더블 호출 회피하지 마라
```js
// 🚩 버그를 가린다
const ref = useRef(null);
useEffect(() => {
  if (!ref.current) {
    ref.current = createConnection();
    ref.current.connect();
  }
}, []);
```
실제 unmount cleanup이 빠지므로 navigation 후 리소스 누수.

## 일부러 Effect 안 써야 하는 경우
- 다른 state 기반 state 조정 → 핸들러 또는 render 중 계산
- 이벤트성 동작(구매 알림) → 핸들러
- 앱 초기화 → 컴포넌트 밖

## 타이밍
**Render → Commit → Effect**

```js
// 잘못
function VideoPlayer({ isPlaying }) {
  const ref = useRef(null);
  if (isPlaying) ref.current.play(); // null! 렌더 중엔 DOM 없음
}
```

## 의존성 규칙
"고를" 수 없음. Effect 안에서 읽는 모든 reactive 값(props/state/component-body)을 listing.
```js
useEffect(() => { if (isPlaying) ref.current.play(); }, [isPlaying]);
```
**예외**: ref(useRef 반환)는 stable identity — 명시 생략 가능 (포함도 무해).

## Recap
- Effect = "이 렌더 자체가 일으키는 부수효과"
- 외부 시스템과 동기화 (서버, 타이머, 구독)
- 기본은 매 렌더 후 실행 / `[]`로 mount 한 번만 / `[a]`로 a 변경 시
- 연결/리스너/타이머 → cleanup 필수
- Strict Mode 더블 호출은 의도 — cleanup 검증
- 의존성은 직접 못 고름. 코드를 바꿔라.
- 타이밍: Effect는 commit 후 (DOM 존재).
