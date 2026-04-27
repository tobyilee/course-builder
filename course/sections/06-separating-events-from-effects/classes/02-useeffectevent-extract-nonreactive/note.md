# useEffectEvent로 non-reactive 로직 분리하기

> LOs: LO-6.3 (Effect 안에서 reactive 동기화와 non-reactive 알림/로깅을 구분한다), LO-6.4 (useEffectEvent로 non-reactive 부분을 추출해 불필요한 재동기화를 제거한다)

## 개요

직전 클래스에서 "왜 실행돼야 하나?"로 event와 effect를 갈랐습니다 [S6.C1]. 그런데 현실 코드는 깔끔하지 않습니다 — 하나의 effect 안에 **두 종류의 로직**이 섞여 있는 경우가 많죠. 예를 들어 채팅방에 connect 하는 로직(reactive)과 "연결됨!" 토스트를 현재 theme 색으로 띄우는 로직(non-reactive)이 한 effect 안에 들어가면, theme 토글만 눌러도 채팅이 끊겼다 다시 붙는 끔찍한 일이 벌어집니다 [slide 2]. 이 클래스는 그 섞임을 푸는 실험적 API — **`useEffectEvent`** — 의 사용법을 익힙니다.

> 주의: `useEffectEvent`는 React **실험적 API**입니다. 채택 여부와 import 경로(`react`의 canary/실험 빌드)는 학습 시점에 따라 다를 수 있습니다 [slide 3].

## 핵심 개념

**문제의 형태부터 봅시다.** Effect의 의존성 배열은 거짓말을 하지 않으니, effect 안에서 읽는 모든 reactive value는 deps에 들어가야 합니다(ESLint exhaustive-deps). 그런데 그러면 **재동기화가 필요 없는 값**까지 deps에 들어가면서 effect가 과하게 재실행됩니다.

```tsx
useEffect(() => {
  const conn = createConnection(roomId);
  conn.on("connected", () => {
    showNotification("연결됨!", theme); // theme이 바뀌면 재연결?
  });
  conn.connect();
  return () => conn.disconnect();
}, [roomId, theme]); // theme 때문에 재연결 발생
```

**`useEffectEvent`의 역할은 "Effect 안에서 호출되지만 reactive 하지 않아야 하는 코드"를 한 함수로 묶는 것**입니다. wrap 된 함수는 **항상 최신 props/state를 보지만, 그 값들이 변해도 effect를 재실행시키지 않습니다** — 즉 deps에 넣을 필요가 없고, 넣어서도 안 됩니다 [slide 5].

```tsx
import { experimental_useEffectEvent as useEffectEvent } from "react";

function ChatRoom({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {
    showNotification("연결됨!", theme); // 항상 최신 theme 본다
  });

  useEffect(() => {
    const conn = createConnection(roomId);
    conn.on("connected", () => onConnected());
    conn.connect();
    return () => conn.disconnect();
  }, [roomId]); // theme 사라짐
}
```

theme을 토글해도 채팅은 끊기지 않고, 그러면서도 알림은 항상 현재 theme으로 뜹니다. **"reactive 하게 동기화할 부분"과 "그 안에서 한 번 호출되는 non-reactive 효과"를 분리한다** — 이게 본질입니다 [slide 7].

## 예시

타이머가 끝날 때 현재 점수를 표시하는 게임 컴포넌트를 봅시다.

```tsx
function Game({ duration, score }) {
  const onFinish = useEffectEvent(() => {
    alert(`최종 점수: ${score}`);   // score가 바뀐다고 타이머 재시작 X
  });

  useEffect(() => {
    const id = setTimeout(() => onFinish(), duration);
    return () => clearTimeout(id);
  }, [duration]); // 진짜 재동기화가 필요한 값만
}
```

`score`는 매 플레이마다 바뀌지만, score가 바뀔 때마다 타이머를 다시 걸 이유는 없습니다. 그렇다고 `score`를 deps에서 빼고 본문에서 직접 읽으면 lint가 정당하게 화를 냅니다 — closure가 stale 해지니까요. `useEffectEvent`로 감싸면 **최신 값 + 비-반응성**을 동시에 얻습니다 [slide 7].

판단 절차는 이렇습니다 [slide 8]: (1) effect를 적고 deps에 넣어야 할 reactive value를 모두 적는다 → (2) 그 중 "이 값이 변했다고 재동기화를 해야 하나?"를 묻는다 → (3) "아니오"인 값을 사용하는 코드 조각을 `useEffectEvent`로 떼어낸다.

## 흔한 실수

**Lint 경고를 끄려고 useEffectEvent를 쓰는 것**은 본말전도입니다. `// eslint-disable-next-line` 으로 deps를 숨기는 것과, "이 값은 정말 reactive 하지 않다"고 판단해 useEffectEvent로 추출하는 것은 다릅니다. **suppress의 우회로**가 아니라 **의미 분리의 도구**로 써야 합니다 [slide 8]. 판단이 헷갈리면 항상 C1의 결정 질문으로 돌아가세요 — "재동기화가 필요한 값인가?"

**useEffectEvent를 `onMount` / `onUpdate` 같은 이름으로 짓는 것**도 흔한 실수입니다. 그렇게 부르는 순간 라이프사이클 사고로 회귀하게 됩니다. 이름은 **"무엇을 하는 effect인가"** — `onConnected`, `onTimerFinished`, `logVisit` 처럼 도메인 사건으로 짓습니다 [slide 8].

## 복습

Effect 안에 reactive 동기화와 non-reactive 알림이 섞여 있을 때, 후자를 `useEffectEvent`로 떼어내면 deps가 깔끔해지고 재동기화가 필요한 진짜 이유만 남습니다. 다음 클래스에서는 이 강력한 도구의 **제약** — 어디까지 넘기면 안 되는가 — 를 다룹니다.
