# Custom Hook composition과 "추출하지 말아야 할 때"

> LOs: LO-8.5, LO-8.6

## 개요

Custom Hook은 **다른 Hook 위에 쌓을 수 있다**는 점에서 강력합니다 [slide 1]. `useState`·`useEffect`로 만든 `useChatRoom` 위에 다시 `useData`를 얹는 식이죠. 하지만 같은 칼로 베이는 함정도 있어요 — "재사용성 있어 보이니까 일단 빼자"가 시작되면 코드베이스는 **얕은 wrapper Hook의 늪**이 됩니다. 이 클래스에서는 composition으로 가치를 키우는 방법과, **언제 추출을 멈춰야 하는가**의 결정 기준을 다룹니다 [S0.C1].

## 핵심 개념

### 1. Composition: 작은 Hook이 큰 Hook을 만든다

`useFormInput`은 내부에서 `useState`만 쓰고, `useChatRoom`은 `useEffect`+`useEffectEvent`를 씁니다. 이 둘을 함께 호출하는 **상위 Hook**(`useChatScreen`처럼)을 만들 수도 있습니다 [slide 2]. 핵심은 한 Hook이 **하나의 관심사**(채팅방 동기화 / 입력 상태 / 데이터 페칭)만 책임지고, 조합은 호출자가 결정한다는 점이에요. 작고 단일 책임을 가진 Hook은 테스트와 교체가 쉽습니다.

### 2. 추출 기준: "두 군데 이상 + 의도가 이름으로 드러남"

react.dev의 가이드는 명료합니다 — Custom Hook은 **중복 제거 자체가 목적이 아니라, Effect의 의도를 드러내는 게 목적**입니다 [slide 3]. 따라서 다음 둘을 동시에 만족할 때만 빼세요.

- **실제 두 곳 이상에서 동일 패턴이 반복**되거나, 한 곳이라도 `useEffect` 본문이 너무 커서 이름이 필요한 경우
- 추출한 Hook 이름이 **무엇과 동기화하는지** 또는 **무엇을 다루는지**를 분명히 말해주는 경우(예: `useChatRoom`, `useOnlineStatus`)

이름이 `useFetchEffect`나 `useDoTheThing`처럼 추상적으로 흐려지면, 그건 보통 추출 시점이 아닙니다.

### 3. 안 빼는 게 정답인 경우

- **단일 사용처**: 한 컴포넌트에서만 쓰는 5줄짜리 `useEffect`를 굳이 분리하면 파일만 늘고 추적성이 떨어집니다 [slide 4]. 두 번째 호출자가 생길 때 빼도 늦지 않아요.
- **Lifecycle wrapper**: `useMount(fn)`, `useUnmount(fn)`, `useUpdateEffect(fn)` 같이 React 라이프사이클을 흉내 내는 Hook은 추출하지 마세요. Effect를 "동기화" 모델에서 다시 "mount/update/unmount"로 끌어내려, useEffectEvent·exhaustive-deps가 풀어준 문제들을 다시 부릅니다 [S5.C1].

## 예시

채팅 화면을 두 Custom Hook의 composition으로 만들어 봅시다.

```tsx
// useFormInput: 단일 책임 — 입력 상태
function useFormInput(initial = '') {
  const [value, setValue] = useState(initial);
  return {
    value,
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setValue(e.target.value),
  };
}

// useChatScreen: composition — 두 Hook을 묶어 의도를 드러냄
function useChatScreen(roomId: string) {
  const message = useFormInput('');
  useChatRoom({
    roomId,
    serverUrl: 'https://localhost:1234',
    onReceiveMessage(msg) {
      showNotification('New: ' + msg);
    },
  });
  return { message };
}

function ChatScreen({ roomId }: { roomId: string }) {
  const { message } = useChatScreen(roomId);
  return <input value={message.value} onChange={message.onChange} />;
}
```

반대로 **추출하면 안 되는** 예시.

```tsx
// 안티패턴 1: lifecycle wrapper
function useMount(fn: () => void) {
  useEffect(() => { fn(); }, []);   // exhaustive-deps 위반을 숨김
}

// 안티패턴 2: 단일 사용처를 위한 얕은 추출
function useLogOnMount(name: string) {
  useEffect(() => { console.log('mounted', name); }, [name]);
}
// 한 컴포넌트에서만 쓰면 그냥 컴포넌트 안에 useEffect로 두는 게 낫다.
```

`useMount`는 의존성 검사를 무력화하고, `useLogOnMount`는 호출자가 한 곳뿐이라 추적만 늘립니다 [slide 5].

## 흔한 실수

- **단일 사용처 Hook 추출**: 재사용 가능"해 보여서" 빼면 파일 수만 늘고 가치는 0입니다. 두 번째 호출자가 등장하는 순간 빼세요.
- **Lifecycle wrapper Hook 작성**: `useMount`·`useUnmount`·`useUpdateEffect`는 동기화 멘탈모델을 망가뜨립니다. 애초 만들지 마세요 [slide 6].

## 복습

Custom Hook은 작고 단일 책임으로 두고 composition으로 키웁니다. 추출 기준은 "두 곳 이상 + 의도가 이름으로 드러남"이고, 단일 사용처와 lifecycle wrapper는 추출 대상이 아닙니다. 다음 섹션에서는 이 모든 원칙(refs · effects · custom hooks)을 한 캡스톤 앱에 통합해 진단해 봅니다 [S9.C1].
