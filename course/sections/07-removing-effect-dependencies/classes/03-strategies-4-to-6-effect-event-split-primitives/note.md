# useEffectEvent와 Effect 분리 — non-reactive를 떼어내기

> LOs: LO-7.5 (useEffectEvent로 Effect 안의 non-reactive 로직을 추출해 의존성을 줄인다), LO-7.6 (서로 무관한 동기화는 Effect를 분리한다)

## 개요

[S7.C2]까지 다룬 외부화·내부화·updater는 "값"을 어디 두느냐의 문제였습니다. 이번 클래스는 한 단계 더 깊은 질문을 던집니다 — *"이 값이 Effect 안에서 읽히긴 하지만, 이 값이 바뀌었다고 동기화를 다시 해야 하는가?"* 답이 '아니오'라면 그 부분은 Effect의 **반응 대상이 아닌데도 안에 있는 코드**입니다. useEffectEvent로 떼어내면 됩니다 [slide 1]. 그리고 한 Effect 안에 무관한 두 동기화가 섞여 있다면, 의존성을 줄이는 가장 단단한 방법은 그 둘을 **다른 Effect로 쪼개는 것**입니다. 두 전략 모두 [S6.C1]의 useEffectEvent 기초와 [S5.C2]의 "각 Effect는 하나의 동기화" 원칙을 실전으로 옮깁니다.

## 핵심 개념

**reactive vs non-reactive 재판정.** Effect 안에서 읽히는 props/state는 기본적으로 reactive입니다. 그러나 *읽긴 하지만 바뀐다고 재동기화하면 안 되는* 값이 종종 있습니다 — 알림 토스트의 현재 theme, 로깅용 userId, 분석 이벤트의 현재 라우트 같은 "최신 값을 보고 싶을 뿐" 케이스입니다. 이런 값은 useEffectEvent로 감싼 콜백 안에 가두면 됩니다 [slide 2].

**useEffectEvent의 역할.** `useEffectEvent`는 **항상 최신 props/state를 보면서 의존성에는 안 잡히는** 함수를 만들어 줍니다. 채팅방에 연결되면 토스트를 띄우는 코드를 보겠습니다.

```tsx
function ChatRoom({ roomId, theme }: Props) {
  const onConnected = useEffectEvent(() => {
    showToast('Connected!', theme); // 항상 최신 theme
  });

  useEffect(() => {
    const conn = createConnection(SERVER_URL, roomId);
    conn.on('connected', () => onConnected());
    conn.connect();
    return () => conn.disconnect();
  }, [roomId]); // theme은 의존성에서 빠짐 — theme 토글로 재연결되지 않음
}
```

theme이 바뀌어도 채팅 재연결은 일어나지 않고, 다음 connect 이벤트에서는 최신 theme으로 토스트가 뜹니다 [slide 3]. 핵심 제약은 [S6.C1]에서 본 대로 — useEffectEvent로 만든 함수는 **Effect 안에서만 호출**해야 하며, 외부로 넘기거나 의존성 배열에 넣지 말 것.

**Effect 분리.** 의존성이 많아지는 또 한 가지 원인은 한 Effect에 두 가지 동기화를 우겨넣는 것입니다. 예를 들어 "로그인 사용자 가져오기"와 "방 연결"을 한 Effect에 두면 의존성이 `[userId, roomId]`가 되고, userId가 바뀔 때 멀쩡한 채팅 연결까지 끊깁니다. 두 동기화는 **목적이 다르므로** 두 Effect로 나눕니다 [slide 4]. "각 Effect는 하나의 독립적인 동기화"라는 [S5.C2] 원칙의 직접 적용입니다.

## 예시

국가 → 도시 → 지역 cascading select를 무심코 한 Effect에 묶는 안티패턴:

```tsx
// Before — 한 Effect에 country/city 동기화 두 가지 + 의존성 폭증
useEffect(() => {
  fetch(`/api/cities?country=${country}`).then(r => r.json()).then(setCities);
  fetch(`/api/areas?city=${city}`).then(r => r.json()).then(setAreas);
}, [country, city]); // country가 바뀌면 areas도 헛 호출
```

```tsx
// After — 두 Effect로 분리, 각자 자기 의존성만 본다
useEffect(() => {
  fetch(`/api/cities?country=${country}`).then(r => r.json()).then(setCities);
}, [country]);

useEffect(() => {
  fetch(`/api/areas?city=${city}`).then(r => r.json()).then(setAreas);
}, [city]);
```

각 Effect가 자기 동기화 단위만 책임지므로 cleanup·race-condition 처리도 더 단순해집니다.

## 흔한 실수

**한 Effect에 country + city 같은 무관한 동기화를 묶기.** "어차피 둘 다 비동기 fetch니까 같이 두자"는 직관은 의존성을 합집합으로 키우고, 한쪽 변경이 다른 쪽까지 재실행시킵니다. 분리하면 의존성이 줄어들 뿐 아니라 cleanup race도 깔끔해집니다 [slide 5].

**useEffectEvent로 감싼 함수를 Effect 밖에서 호출하기.** 버튼 onClick에 직접 붙이거나 다른 컴포넌트로 넘기면 React가 동작을 보장하지 않습니다. useEffectEvent는 *Effect의 일부*여야 합니다 — 이 제약을 어기면 stale 동작·경고가 발생합니다.

## 복습

- "이 값이 변하면 정말 다시 동기화해야 하는가?" 답이 '아니오'면 useEffectEvent로 감쌉니다.
- 한 Effect 안에 무관한 두 동기화가 있다면 분리합니다 — 의존성과 cleanup이 같이 깔끔해집니다.
- 마지막 남은 패턴은 prop으로 받은 객체를 어떻게 다룰까 — [S7.C4]에서 마무리합니다.
