# useEffectEvent의 제약과 안티패턴

> LOs: LO-6.5 (useEffectEvent를 사용하는 컴포넌트/Hook 경계 안에서만 호출하는 규칙을 적용한다), LO-6.6 (deps·전달·명명에 관한 안티패턴을 진단하고 교정한다)

## 개요

`useEffectEvent`는 강력한 만큼 **좁은 도구**입니다 [S6.C2]. 잘못 쓰면 stale closure, 의존성 누락, 추적 불가능한 사이드이펙트가 다시 살아납니다. 이 클래스는 react.dev가 명시하는 네 가지 제약과, 그것을 어긴 코드의 모양을 정리합니다 [slide 2]. 다시 강조하면 — **`useEffectEvent`는 React 실험적 API**이며, stable이 되기 전까지 시그니처가 바뀔 수 있습니다 [slide 3].

## 핵심 개념

**제약 1 — "선언된 컴포넌트/Hook 안에서만 호출한다."** `useEffectEvent`로 만든 함수는 그것을 정의한 컴포넌트나 custom Hook의 effect 안에서만 호출돼야 합니다. **다른 컴포넌트나 Hook에 prop·인자로 넘기면 안 됩니다** [slide 4]. 넘기는 순간 그 함수의 "최신 값을 닫고 있는 동시에 reactive 하지 않다"는 보증이 의미를 잃고, 호출 시점이 정의 컴포넌트의 렌더 사이클과 어긋나 stale 한 동작이 생길 수 있습니다.

```tsx
// 안티패턴
function Parent() {
  const onClick = useEffectEvent(() => doSomething(state));
  return <Child onClick={onClick} />; // 넘기면 안 됨
}
```

**제약 2 — "의존성 배열에 넣지 않는다."** `useEffectEvent`로 wrap 한 함수의 정체성은 매 렌더마다 달라지지만, ESLint 규칙은 이를 deps에서 자동으로 제외합니다. 직접 deps에 적어 넣으면 effect가 매 렌더마다 재실행되어 useEffectEvent를 도입한 의미가 사라집니다 [slide 6].

```tsx
// 안티패턴
useEffect(() => {
  onConnected();
}, [roomId, onConnected]); // onConnected를 넣지 말 것
```

**제약 3 — "Event handler 대용으로 쓰지 않는다."** 평범한 `onClick` 같은 핸들러는 그냥 함수면 됩니다. `useEffectEvent`는 **Effect 내부에서 호출되는 non-reactive 조각** 전용입니다 [slide 7]. 핸들러 자리에 굳이 쓰면 추가적인 React 내부 추적 비용만 들고 의미상 혼란을 줍니다.

**제약 4 — "라이프사이클 이름을 붙이지 않는다."** `onMount`, `onUpdate`, `onUnmount` 같은 이름은 Effect를 라이프사이클 훅처럼 다시 사고하게 만듭니다 [S5.C1 참고]. 이름은 **도메인 사건**으로: `onConnected`, `onVisit`, `onTimerFinished` [slide 5].

## 예시

다음은 네 제약을 동시에 어긴 안티패턴과 교정본입니다.

```tsx
// Before — 모든 함정 모음
function ChatRoom({ roomId, theme }) {
  const onMount = useEffectEvent(() => {        // (4) 라이프사이클 명명
    showNotification("연결됨!", theme);
  });
  return <Connector onConnect={onMount} />;     // (1) 다른 컴포넌트로 전달
}

function Connector({ onConnect, roomId }) {
  useEffect(() => {
    const c = createConnection(roomId);
    c.on("connected", onConnect);
    c.connect();
    return () => c.disconnect();
  }, [roomId, onConnect]);                      // (2) deps에 포함
}

// After — 제약을 지킨 형태
function ChatRoom({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {    // 도메인 이름
    showNotification("연결됨!", theme);
  });

  useEffect(() => {                              // 같은 컴포넌트 안에서 호출
    const c = createConnection(roomId);
    c.on("connected", () => onConnected());
    c.connect();
    return () => c.disconnect();
  }, [roomId]);                                  // useEffectEvent는 deps 제외
}
```

After 버전은 `useEffectEvent`를 정의한 컴포넌트 안의 effect에서만 호출하고, deps에 포함하지 않으며, 도메인 사건명을 씁니다. 외부에 함수가 필요하다면 — 그 함수는 useEffectEvent가 아니라 보통 함수거나, 별도의 reactive value로 다뤄야 합니다 [slide 6].

## 흔한 실수

**Lint를 끄지 못해서 useEffectEvent로 우회하는 패턴.** "deps에 안 넣고 싶은 값이 있다 → useEffectEvent에 wrap" 으로 곧장 넘어가지 마세요. 먼저 C1의 질문으로 돌아가 — *"이 값이 변했을 때 정말 재동기화가 필요 없는가?"* — 를 확인해야 합니다. 답이 "필요 없다"일 때만 useEffectEvent가 정당합니다. 그게 아니면 lint suppress와 다를 바 없는, 더 비싼 우회입니다 [slide 7].

**useEffectEvent를 prop으로 흘려보내는 패턴.** 부모에서 `useEffectEvent`로 만든 콜백을 자식에 prop으로 넘기는 코드는 "재사용처럼 보이지만 추적 불가능한 동작"을 만듭니다. 자식에서 그 콜백이 언제, 어떤 closure로 호출될지 보장되지 않습니다. 콜백이 진짜로 자식에서 필요하면 — **자식이 자신의 useEffectEvent를 갖거나, 그냥 평범한 함수 prop**으로 두는 게 옳습니다 [slide 7]. 실제 환경의 시그니처는 React 실험 빌드 버전에 따라 다를 수 있으니 검증 후 사용하세요.

## 복습

`useEffectEvent`는 — 정의 컴포넌트 내부에서, deps 밖에서, 도메인 이름으로, Effect 호출용으로 — 네 조건을 모두 만족할 때만 그 가치가 살아납니다. 다음 섹션에서는 이 도구를 포함한 **6가지 의존성 감축 전략**을 종합합니다 [S7.C1 예고].
