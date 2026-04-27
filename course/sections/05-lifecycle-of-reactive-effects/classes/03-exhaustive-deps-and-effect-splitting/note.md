# exhaustive-deps 해결 3가지 옵션과 Effect 분리 원칙
> LOs: LO-S5.4, LO-S5.5

## 개요

ESLint `react-hooks/exhaustive-deps`가 빨간 줄을 그을 때, 가장 위험한 반응은 `// eslint-disable-next-line` 으로 덮는 것입니다 [slide 1]. 이번 클래스는 그 유혹 대신 **코드를 바꾸는 3가지 길** 을 의사결정 기준과 함께 비교하고, 더 큰 원칙으로 "한 Effect = 하나의 동기화 프로세스"를 세웁니다.

## 핵심 개념

3가지 옵션 [slide 3]:
1. **진짜 reactive면 deps에 추가** — 비용은 재실행이 더 자주 일어나는 것. 그게 정말 의도한 동기화면 정답.
2. **사실은 non-reactive면 컴포넌트 밖으로 / Effect 안으로** — 모듈 상수로 끌어올리거나, 매 렌더 변하는 객체/함수면 Effect 본문 안에서 생성해 deps에서 제거.
3. **최신 값이 필요하지만 재동기화는 싫으면 useEffectEvent** — 다음 섹션 [S6]의 도구. 비-반응형 부분만 추출.

선택 기준은 "값의 의미가 무엇이냐"입니다. 모순처럼 들릴 때는 십중팔구 **두 동기화가 한 Effect에 묶여 있어서** 기준이 충돌하는 경우입니다 [slide 5]. 이때는 옵션 2/3 이전에 **Effect를 쪼개는 것** 이 먼저입니다 — 무관한 동기화는 각자의 deps와 cleanup을 가져야 합니다.

## 예시

분리 전:
```js
useEffect(() => {
  logVisit(roomId);
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);
```
분리 후 [slide 6]:
```js
useEffect(() => logVisit(roomId), [roomId]);
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);
```
이제 분석 정책이 바뀌어 `userId`를 같이 로깅해야 한다면, 채팅 연결을 건드리지 않고 첫 번째 Effect의 deps만 늘리면 됩니다.

## 흔한 실수

- **linter suppress**: 가장 자주 보는 함정. 값이 frozen된 채로 closure가 굳어 디버깅이 끔찍해집니다 — 절대 사용 금지.
- **`logVisit + connection`을 한 Effect에 묶는다**: 변경이 한쪽에만 있어도 양쪽이 함께 재실행되어 의도한 동기화 경계가 무너집니다.
- **`ref.current` 를 deps에**: linter가 안 시켜도 손에 익어 추가하는 실수 — non-reactive라 신호가 오지 않습니다 ([S5.C2]).
- **mutable global을 deps에**: 위와 같은 이유 — 외부 store는 `useSyncExternalStore` ([S4.C5]).

## 복습

deps 경고는 코드 변경으로 푼다 → 3 옵션 중 의미에 맞는 하나 → 갈등이 있으면 Effect 자체가 두 일을 하고 있는지 의심. 다음 섹션 [S6]에서는 옵션 3의 실제 도구인 `useEffectEvent`로 "비-반응형 부분만 추출"하는 패턴을 본격적으로 다룹니다.
