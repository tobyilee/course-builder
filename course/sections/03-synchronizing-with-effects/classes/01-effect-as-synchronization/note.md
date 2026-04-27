# Effect는 라이프사이클이 아니라 동기화다

> LOs: LO-S3.1

## 개요

"useEffect는 mount/update/unmount 훅이다." 이 한 줄이, 우리가 Effect 앞에서 매번 막히는 이유입니다 [slide 1]. 이 멘탈모델로는 "왜 dev에서 두 번 실행되지?", "의존성에 뭘 넣어야 하지?", "왜 이게 무한 루프야?" 같은 질문에 답할 수 없습니다. 클래스 라이프사이클(`componentDidMount`)에서 넘어온 비유가 강력해서 잘 안 떨어지는데, 오늘은 정의 자체를 바꿉니다 — Effect는 라이프사이클이 아니라 **동기화**입니다.

## 핵심 개념

Effect는 **렌더링 자체가 일으키는 부수효과**입니다 [slide 2]. 이벤트 핸들러도, 순수 렌더 코드도 아닌 세 번째 카테고리예요. 더 실용적인 정의로 옮겨봅시다.

> "컴포넌트가 화면에 떠 있는 동안 외부 시스템과의 연결을 유지하는 코드"

여기서 세 가지 속성이 따라옵니다.

- **외부 시스템이란?** React가 관리하지 않는 모든 것 — DOM 노드, 서버 connection, 타이머, 구독, 브라우저 API(`localStorage`, `IntersectionObserver`).
- **"유지"라는 동사가 핵심.** 한 번 실행되고 끝이 아니라, 컴포넌트가 살아있는 내내 React 상태와 외부 세계가 어긋나지 않게 맞추는 일입니다.
- **트리거가 시간이 아니라 값의 불일치.** "언제 실행되나"가 아니라 "무엇과 무엇을 동기화하나"가 먼저입니다 [slide 3].

판별 비유 하나만 손에 쥐고 가세요. 친구에게 **메시지 한 통 보내기**는 이벤트 — 클릭 한 번에 1회 실행. **전화 연결을 유지하기**는 Effect — 통화가 살아있는 동안 계속 양쪽 상태를 일치시키죠. "왜 이 코드가 실행돼야 하나?"라는 질문에 "사용자가 이 액션을 했기 때문"이면 핸들러, "컴포넌트가 화면에 보이기 때문"이면 Effect입니다.

## 예시

가장 깨끗한 동기화 예시는 비디오 플레이어입니다 [slide 4]. prop `isPlaying`이라는 React 상태와 `<video>` DOM 요소의 재생 상태를 일치시키고 싶어요.

```tsx
function VideoPlayer({ src, isPlaying }: Props) {
  const ref = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (isPlaying) ref.current?.play();
    else ref.current?.pause();
  }, [isPlaying]);

  return <video ref={ref} src={src} loop playsInline />;
}
```

여기서 두 가지를 음미해 봅시다.

1. **렌더 중에는 `ref.current.play()`를 호출할 수 없습니다.** 그 시점엔 DOM이 아직 commit 전이라 `ref.current`는 `null`이에요. Effect는 commit이 끝난 뒤에 실행되므로 DOM이 존재합니다.
2. **트리거는 "토글 클릭"이 아니라 "isPlaying과 DOM 상태의 불일치"입니다.** 부모가 다른 prop을 바꿔 재렌더해도 `isPlaying`이 그대로면 deps가 변하지 않으니 Effect는 조용히 지나갑니다. 정확히 어긋날 때만 맞추는 거예요.

대조군으로, "전송" 버튼을 눌러 메시지를 보내는 동작은 Effect가 **아닙니다** [slide 5]. 트리거가 사용자 클릭이니까요. 이걸 `useEffect`에 넣으면 다른 prop 변경으로 재렌더될 때마다 메시지가 또 발송됩니다 — production에서 만나면 식은땀 나는 버그죠.

## 흔한 실수

- **렌더 중에 외부 시스템을 호출하기.** 위 예제처럼 `if (isPlaying) ref.current.play()`를 `useEffect` 밖에 두면 `null` 참조 또는 commit 전 호출로 폭발합니다. 외부 동기화는 commit 후로 미루세요.
- **이벤트성 동작을 Effect에 넣기.** "구매 완료 알림 토스트"는 클릭 핸들러에 넣어야 합니다. Effect에 넣으면 마운트되거나 무관한 deps가 바뀔 때마다 토스트가 다시 뜹니다.

판별 질문: "이 동작은 사용자 액션 때문인가, 아니면 화면이 떠 있어서인가?"

## 복습

- Effect = 외부 시스템과의 **동기화**, 라이프사이클 훅이 아님.
- 비유: 메시지 1통(이벤트) vs 연결 유지(Effect). "왜 실행돼야 하나"부터 묻기.
- VideoPlayer가 보여주듯, React 상태 ↔ 외부 세계가 어긋날 때마다 자동으로 맞추는 도구.
- 다음 클래스([S3.C2])에서는 이 동기화를 정확히 **언제 다시 돌릴지** 정하는 의존성 배열과, 이전 동기화를 끊는 cleanup으로 들어갑니다.
