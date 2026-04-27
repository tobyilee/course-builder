# Custom Hook 설계 — useChatRoom과 useEffectEvent 래핑

> LOs: LO-8.3, LO-8.4

## 개요

Custom Hook을 쓰는 진짜 이유는 단순한 코드 절약이 아니라, **Effect의 의도를 이름으로 드러내는** 데 있습니다 [slide 1]. `useEffect(() => { ... })`만 보면 "여긴 뭘 동기화하지?"를 본문을 읽고 추론해야 하지만, `useChatRoom({ serverUrl, roomId, onReceiveMessage })`로 추출해 두면 호출자는 "채팅방과 동기화" 한 줄로 의도를 읽습니다. 이 클래스에서는 채팅방 Hook을 만들면서, `useEffectEvent`로 **non-reactive 이벤트 핸들러를 감싸는 패턴**을 익힙니다 [S6.C1].

## 핵심 개념

### 1. Hook 인터페이스: 입력은 reactive, 출력은 의도

좋은 Custom Hook은 컴포넌트 쪽 reactive 값(여기서는 `roomId`, `serverUrl`)을 **인자로 받고**, 내부에서 그것을 의존성 배열에 그대로 넣습니다 [slide 2]. `roomId`가 바뀌면 Hook은 자동으로 옛 방을 떠나고 새 방에 연결합니다 — 호출자는 그 메커니즘을 몰라도 됩니다.

### 2. 이벤트 콜백은 `useEffectEvent`로 분리

`onReceiveMessage` 같은 콜백은 매 렌더마다 새 함수 참조가 됩니다. 그대로 `useEffect` 의존성에 넣으면 **메시지가 올 때마다가 아니라, 매 렌더마다 채팅방을 재연결**하는 참사가 일어나요 [slide 3]. 그렇다고 의존성에서 빼면 stale closure에 갇힙니다.

해법은 `useEffectEvent`입니다. Effect 내부에서 호출되지만 reactive하지 않은 부분을 잘라내, 항상 **최신 props/state**를 보면서도 의존성 배열에는 들어가지 않도록 합니다.

### 3. 반환은 "필요한 것만"

Hook은 내부 구현(예: connection 객체)을 그대로 노출하지 말고, 호출자가 진짜 필요한 값(예: `sendMessage` 함수)만 돌려주세요 [slide 4]. 인터페이스가 좁을수록 나중에 내부를 바꿔도 호출 코드가 깨지지 않습니다.

## 예시

```tsx
// useChatRoom.ts
import { useEffect } from 'react';
import { experimental_useEffectEvent as useEffectEvent } from 'react';
import { createConnection } from './chat';

type Options = {
  serverUrl: string;
  roomId: string;
  onReceiveMessage: (msg: string) => void;
};

export function useChatRoom({ serverUrl, roomId, onReceiveMessage }: Options) {
  // 1) 콜백을 Effect Event로 감싸 non-reactive로 만든다
  const onMessage = useEffectEvent((msg: string) => {
    onReceiveMessage(msg);
  });

  // 2) reactive 의존성은 serverUrl, roomId 뿐
  useEffect(() => {
    const connection = createConnection({ serverUrl, roomId });
    connection.on('message', (msg) => onMessage(msg));
    connection.connect();
    return () => connection.disconnect();
  }, [serverUrl, roomId]);
}
```

호출 측은 이렇게 깔끔해집니다.

```tsx
function ChatRoom({ roomId }: { roomId: string }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');
  useChatRoom({
    roomId,
    serverUrl,
    onReceiveMessage(msg) {
      showNotification('New: ' + msg);  // 매 렌더마다 새 함수여도 OK
    },
  });
  // ...
}
```

여기서 핵심은 `roomId`나 `serverUrl`이 바뀔 때만 재연결되고, `onReceiveMessage` 함수 참조가 바뀐다고 재연결되지 않는다는 점입니다 [slide 5]. 즉 Effect의 동기화 단위(채팅방 연결)와 이벤트 처리 단위(메시지 수신 시 알림)를 깔끔히 갈랐어요 [S6.C2].

## 흔한 실수

- **`onReceiveMessage`를 `useEffectEvent`로 감싸지 않기**: 그러면 둘 중 하나입니다 — 의존성에 넣어 매 렌더 재연결되거나, 의존성에서 빼서 stale closure로 옛 콜백이 호출됩니다. 어느 쪽도 정답이 아닙니다.
- **`useMount`/`useUnmount` 같은 lifecycle wrapper로 둔갑**: `useEffect(fn, [])`을 `useMount(fn)`으로 감싸면 "동기화" 의미가 사라지고 클래스 컴포넌트의 `componentDidMount` 사고로 퇴행합니다. react.dev는 이를 명시적 안티패턴으로 경고합니다 [slide 6]. Hook은 **무엇과 동기화하는지**가 이름에 드러나야 합니다.

## 복습

좋은 Custom Hook은 reactive 값은 인자로 받아 의존성에 그대로 흘리고, 비-reactive 콜백은 `useEffectEvent`로 잘라내며, 내부 객체는 숨기고 필요한 API만 반환합니다. 다음 클래스에서는 **언제 추출하지 말아야 하는가** — 단일 사용처와 lifecycle wrapper 함정 — 를 다룹니다 [S8.C3].
