# Strict Mode 더블 호출의 의도와 ref-회피 안티패턴

> LOs: LO-S3.4

## 개요

"`✅ Connecting...` 로그가 두 번 찍혀요. 분명 mount는 한 번이었는데?" — Stack Overflow 단골 질문입니다 [slide 1]. 많은 분이 이걸 React 버그로 의심하고, `useRef`로 두 번째 실행을 막으려 합니다. 스포일러: 이건 버그가 아니라 React가 여러분의 cleanup을 채점하는 **자동 테스트**예요. 오늘은 그 의도를 이해하고, "didMount ref"라는 흔한 잘못된 처방을 피하는 법을 배웁니다.

## 핵심 개념

**Strict Mode**는 `<StrictMode>`로 감싼 트리에서 **dev 빌드에만** 동작하는 추가 검사입니다 [slide 2]. production 빌드에는 영향이 없어요. 그중 한 가지 검사가 모든 마운트를 이렇게 시뮬레이션합니다.

> 컴포넌트를 마운트 → 즉시 unmount → 다시 마운트

그 결과 Effect 흐름은 `setup → cleanup → setup`으로 보입니다. production에서는 setup 한 번, unmount 시 cleanup 한 번이고요.

왜 일부러 두 번 호출할까요? **"내 Effect가 cleanup 없이도 우연히 동작했는지"를 들춰내기 위해서**입니다 [slide 3]. cleanup이 정확하면 setup → cleanup → setup 후에도 살아있는 연결은 1개입니다. cleanup이 빠졌거나 잘못됐으면 두 번째 setup 후 연결이 2개가 되어 로그/네트워크가 중복되죠 — 즉시 발견됩니다. 관점을 뒤집으면, "두 번 실행"은 버그 신호가 아니라 **cleanup이 있어야 멀쩡한 코드**라는 React의 채점표예요.

## 예시

cleanup이 빠진 채팅 연결 [slide 4]:

```ts
// 버그 — cleanup 없음
useEffect(() => {
  const c = createConnection();
  c.connect();
}, []);
```

Dev 콘솔: `✅ Connecting... / ✅ Connecting...` — `❌ Disconnected`가 안 보입니다. 두 connection이 동시에 살아있다는 증거예요. 수정:

```ts
useEffect(() => {
  const c = createConnection();
  c.connect();
  return () => c.disconnect();
}, []);
```

이제 콘솔: `✅ Connecting... / ❌ Disconnected. / ✅ Connecting.` 살아있는 건 마지막 1개. Strict Mode가 production 가기 전에 누수 버그를 잡아준 셈입니다.

이제 흔한 잘못된 처방을 봅시다 [slide 5].

```ts
// 안티패턴 — didMount ref로 두 번째 setup 막기
const ran = useRef(false);
useEffect(() => {
  if (ran.current) return;
  ran.current = true;
  createConnection().connect();
}, []);
```

겉보기 효과: dev 콘솔에서 `✅ Connecting...`이 한 번만 찍힙니다 — 문제 해결된 듯 보이죠. 하지만 진짜 병은 그대로입니다.

- **cleanup이 여전히 없습니다.** Strict Mode 더블 호출만 막았을 뿐.
- **`ran.current = true`가 영구 플래그가 됩니다.** 사용자가 다른 라우트로 갔다 돌아오거나 탭을 전환해 실제로 unmount/remount되는 시나리오에서, ref는 새 인스턴스에서 다시 `false`로 초기화되지만 cleanup이 없으니 옛 connection은 그대로 살아남아요. 페이지 A → B → A 복귀를 반복할수록 좀비 연결이 1, 2, 3개로 누적됩니다.

증상을 가렸을 뿐, 진짜 병(cleanup 부재)을 그대로 둔 셈입니다.

## 흔한 실수

- **Strict Mode를 만족시키려 ref 가드로 회피하기.** 위에서 봤듯 라우트 복귀나 탭 전환 시 누수로 폭발합니다. 옳은 처방은 **cleanup 자체를 견고하게** 만드는 것입니다 [slide 6].

체크리스트:

1. 시작한 모든 효과(connect, addEventListener, setInterval, fetch)에 짝이 있는가?
2. 두 번 setup해도 살아있는 리소스는 1개인가?
3. unmount → remount를 반복해도 누수가 없는가?

이 셋을 통과하면 dev의 더블 호출은 "소리 없이 지나가는 검증"이 됩니다.

- **production은 영향 없으니까 신경 끄기?** Strict Mode 자체는 production에서 안 돌지만, **cleanup 부재 버그는 실제 unmount 시 그대로 누수로 나타납니다.** dev에서 채점받지 않으면 production에서 사용자에게 청구서가 갑니다.

## 복습

- Dev의 더블 호출은 버그가 아니라 cleanup이 정확한지 검증하는 React의 채점표.
- ref guard로 두 번째 setup을 막는 건 증상 가리기 — 실제 unmount/remount 시 좀비 연결로 폭발.
- 옳은 길: cleanup을 견고하게(짝, 멱등, 누수 없음) 만들면 더블 호출은 그냥 통과한다.
- 섹션 S3 마무리. 다음 섹션([S4])에서는 "Effect를 쓰지 말아야 할 12가지 안티패턴" 진단으로 이어집니다.
