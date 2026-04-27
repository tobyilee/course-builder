# useEffect 시그니처, 의존성 배열, cleanup 패턴

> LOs: LO-S3.2, LO-S3.3

## 개요

지난 클래스([S3.C1])에서 Effect를 "동기화"로 재정의했죠. 그런데 동기화에는 두 개의 다이얼이 있습니다 — **언제 다시 맞출지**(의존성 배열)와 **이전에 맞춘 걸 어떻게 거둘지**(cleanup) [slide 1]. 이 두 다이얼을 잘못 돌리면 메모리 누수, 좀비 구독, 메시지 중복 발송 같은 production 사고로 곧장 이어집니다.

## 핵심 개념

`useEffect(setup, deps?)` — 첫 인자는 동기화를 시작하는 함수, 두 번째 인자는 "언제 다시 실행할지"의 다이얼입니다 [slide 2]. deps의 세 가지 형태를 표로 새겨두세요.

| deps 형태 | 실행 시점 |
|---|---|
| 생략 | 매 렌더 후 (대부분 잘못된 신호) |
| `[]` | 마운트 시 1회 (dev에선 2회로 보임 — [S3.C3] 주제) |
| `[a, b]` | 마운트 + `a` 또는 `b`가 `Object.is` 기준으로 바뀔 때 |

여기서 가장 중요한 건 **deps는 내가 "고르는" 값이 아니라는 점**입니다. Effect 안에서 읽는 모든 reactive 값(props, state, 컴포넌트 본문에서 파생된 값)을 그대로 적은 것이어야 해요. ESLint `react-hooks/exhaustive-deps`가 이걸 강제합니다.

cleanup은 동기화의 나머지 절반입니다 [slide 4]. setup이 return하는 함수가 cleanup이 되고, 두 시점에 호출됩니다.

1. 컴포넌트 unmount 시
2. **다음 setup 직전** — deps가 바뀌어 재실행되기 전

규칙은 단순합니다: 시작한 효과를 **정확히 같은 손으로** 거둬가야 합니다. connect/disconnect, addEventListener/removeEventListener, startAnim/resetAnim — 모두 한 쌍의 패턴입니다.

## 예시

네 가지 cleanup 패턴을 손에 익히세요.

**패턴 1 — 채팅 connection** [slide 5]
```ts
useEffect(() => {
  const conn = createConnection(roomId);
  conn.connect();
  return () => conn.disconnect();
}, [roomId]);
```
방을 옮기면 cleanup이 옛 방을 끊고 새 방을 연결합니다. cleanup이 빠지면? 방을 옮길 때마다 옛 연결이 살아남아 "메시지가 자꾸 두 번씩 도착하는 그 버그"가 됩니다.

**패턴 2 — DOM 리스너** [slide 6]
```ts
useEffect(() => {
  const onScroll = () => setY(window.scrollY);
  window.addEventListener('scroll', onScroll);
  return () => window.removeEventListener('scroll', onScroll);
}, []);
```
`removeEventListener`는 **같은 함수 참조**여야 동작합니다. 익명 함수를 두 번 만들어 넘기면 절대 떼어지지 않아요.

**패턴 3 — 애니메이션 리셋**: 시작 시 `opacity = 1`, cleanup에서 `cancelAnimationFrame(id)` 또는 원래 스타일로 복구.

**패턴 4 — fetch race condition** [slide 7]
```ts
useEffect(() => {
  let ignore = false;
  fetch(`/api?q=${query}`)
    .then(r => r.json())
    .then(data => { if (!ignore) setData(data); });
  return () => { ignore = true; };
}, [query]);
```
검색어가 빠르게 바뀌면 늦은 응답이 빠른 응답을 덮어쓸 수 있죠. 이전 query의 cleanup이 `ignore = true`로 만들어 늦게 도착한 응답을 폐기합니다. `AbortController`로 fetch 자체를 abort하는 변형도 같은 의도예요 — "이전 동기화의 결과를 무시한다."

## 흔한 실수

- **`setInterval`만 두고 `clearInterval`을 빼먹기.** `useEffect(() => { setInterval(tick, 1000); }, [])`는 unmount 시 타이머가 살아남고, dev Strict Mode에서는 두 개가 동시에 도는 좀비 인터벌이 됩니다. 항상 `const id = setInterval(...); return () => clearInterval(id);`.
- **deps 잘못 추론.** "이 값은 안 바뀔 것 같으니 빼자"는 위험합니다. linter 경고를 suppress하지 말고, 정말 reactive하지 않다면 컴포넌트 밖으로 꺼내거나(`const TICK = 1000`), Effect 구조 자체를 바꾸세요. 의존성 줄이기 전략은 [S7]에서 본격적으로 다룹니다.

## 복습

- deps는 동기화 빈도의 **다이얼**: 생략 / `[]` / `[a,b]` = 매 렌더 / 마운트 1회 / 값 변경 시.
- cleanup은 동기화의 다른 절반 — 시작한 효과를 정확히 같은 손으로 거둔다.
- 4가지 패턴: connect/disconnect, add/removeEventListener, animation reset, fetch ignore-flag.
- 다음 클래스([S3.C3])에서는 dev에서 Effect가 두 번 실행돼 보이는 Strict Mode의 의도와, ref로 회피하면 왜 더 큰 사고로 번지는지 살펴봅니다.
