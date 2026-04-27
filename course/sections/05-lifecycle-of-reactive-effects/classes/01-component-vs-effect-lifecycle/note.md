# 컴포넌트 vs Effect 라이프사이클 — 매 렌더는 자기만의 closure
> LOs: LO-S5.1

## 개요

[S3]에서 Effect는 "외부 시스템과의 동기화"라고 배웠습니다. 이번 클래스는 한 단계 더 들어가서, **컴포넌트 라이프사이클(mount→update→unmount)** 과 **Effect 라이프사이클(synchronization 시작 ↔ 중지)** 이 별개의 시계를 가진다는 멘탈모델을 단단히 합니다 [slide 1]. 채팅방 컴포넌트는 한 번 마운트된 채로 살아있어도, 사용자가 방을 옮길 때마다 Effect는 "끊고-다시 맺기"를 반복합니다.

## 핵심 개념

매 렌더는 그 시점의 props/state를 그대로 가둔 **자기만의 closure** 를 만듭니다 [slide 3]. Effect 본문에 적힌 `roomId`는 "그 렌더 시점의 roomId"이며, 다음 렌더의 Effect는 새 closure로 새로 태어납니다. 다시 말해 Effect는 콜백 한 묶음이 mount/unmount에 한 번씩 발화하는 것이 아니라, **각 렌더가 새 동기화 사이클을 일으키고 그 직전 사이클은 cleanup으로 끊어지는** 구조입니다 [slide 4]. 그래서 "Effect는 재실행될 수 있어야 한다"는 것이 React가 cleanup을 강하게 요구하는 이유입니다.

## 예시

```js
function ChatRoom({ roomId }) {
  useEffect(() => {
    const conn = createConnection(serverUrl, roomId);
    conn.connect();
    return () => conn.disconnect();
  }, [roomId]);
}
```
roomId가 `'general'` → `'travel'` → `'music'` 으로 바뀌면, 컴포넌트는 한 번도 unmount되지 않은 채로 두 번의 disconnect/connect 페어를 겪습니다 [slide 5]. 같은 컴포넌트 인스턴스 안에서 Effect만 자기 시계를 따로 돌립니다.

## 흔한 실수

- **Effect를 lifecycle hook으로 본다**: "componentDidMount 자리"라는 비유는 매 렌더의 closure를 가린다 — 차라리 "각 렌더의 동기화 결과 패치"로 부르세요.
- **cleanup을 옵션처럼 본다**: 더블 호출이 안 보인다고 cleanup 없이 두면, 방을 바꿀 때마다 좀비 연결이 쌓입니다.
- **closure 캡처를 잊는다**: 콜백 안에서 `roomId`가 "현재" 값일 거라고 가정하면, 비동기 응답이 도착했을 때 그 시점의 closure에 갇힌 옛 값이 보일 수 있습니다.

## 복습

Effect는 컴포넌트와 다른 시계를 산다 → 매 렌더는 자기 closure → React가 cleanup으로 사이클을 끊고 새 사이클을 시작한다. 다음 클래스 [S5.C2]에서는 어떤 식별자가 이 사이클의 트리거가 되는지 — reactive vs non-reactive — 를 가른 뒤, Object.is 비교로 재실행이 결정되는 흐름을 단계별로 따라갑니다.
