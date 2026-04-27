# 자식에게 ref 넘기기 — forwardRef → React 19 ref prop, 그리고 useImperativeHandle

> LOs: LO-S2.5

## 개요

자체 디자인 시스템의 `<MyInput />`을 만들었습니다. 부모 폼이 제출 직후 이 입력창에 커서를 다시 두려고 `<MyInput ref={inputRef} />`라고 적었습니다 — 그런데 동작하지 않습니다 [slide 1]. 콘솔에는 "function components cannot be given refs" 같은 경고가 뜨거나, ref가 그냥 `null`인 채로 남습니다. 왜일까요? React에서 **ref는 자동 prop이 아니기 때문**입니다. 이번 시간에는 React 18까지의 `forwardRef`, React 19의 ref-as-prop, 그리고 노출 표면을 좁히는 `useImperativeHandle`까지 — 자식에게 ref를 넘기는 세 가지 모델을 비교합니다.

## 핵심 개념

**ref는 일반 prop이 아닙니다.** [slide 2] `key`, `ref`는 React가 가로채서 별도로 처리하는 특수 키이므로, 자식 함수 컴포넌트의 `props` 인자에는 들어오지 않습니다. React 18 이전 시대에는 이를 `forwardRef`로 우회했습니다.

```jsx
const MyInput = forwardRef(function MyInput(props, ref) {
  return <input ref={ref} {...props} />;
});
```

`(props, ref)` 시그니처를 명시 노출하는 한 단계 보일러플레이트가 디자인 시스템 전반에 깔리던 시절이 길었습니다.

**React 19부터는 `ref`가 일반 prop처럼 동작합니다** [slide 3]. 함수 시그니처에서 그냥 분해해 받으면 됩니다.

```jsx
function MyInput({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}

function MyForm() {
  const inputRef = useRef(null);
  return <MyInput ref={inputRef} />;
}
```

`forwardRef` 래핑이 사라지면서 디자인 시스템 코드가 한결 단순해집니다. 기존 코드는 codemod로 자동 전환할 수 있고, 라이브러리 호환성을 위해 한동안은 두 패턴이 공존합니다 — 어느 쪽을 만나도 의도를 읽을 수 있어야 합니다.

세 번째 도구는 **`useImperativeHandle`**입니다 [slide 4]. ref를 그냥 자식 input에 넘기면 부모는 `.focus()`뿐 아니라 `.value`, `.blur()`, `.select()`, `.setSelectionRange()` 같은 input의 **모든 DOM API**에 접근하게 됩니다. 캡슐화 균열입니다 — 자식이 의도한 명령형 표면이 입력 DOM 전체로 새어 나갑니다. 이를 좁히려면 부모에게 노출되는 객체를 직접 설계합니다.

```jsx
function MyInput({ ref }) {
  const realInputRef = useRef(null);
  useImperativeHandle(ref, () => ({
    focus() { realInputRef.current.focus(); },
  }));
  return <input ref={realInputRef} />;
}
```

이제 부모는 `.focus()`만 호출할 수 있습니다. 노출이 좁을수록 자식의 내부 구현(예: `<input>`을 `<textarea>`로 바꾸기, contenteditable로 갈아끼우기)을 깰 위험이 줄어듭니다.

## 예시

캡슐화 감각을 높이는 의사결정 매트릭스입니다 [slide 5].

| 시나리오 | 권장 도구 |
|---|---|
| 새 프로젝트, React 19 | ref-as-prop으로 충분 |
| React 18 사용자도 지원하는 라이브러리 | `forwardRef` 유지 (호환성 우선) |
| `<Modal>`이 부모에게 `open()/close()`만 주고 portal 내부 구조는 숨기고 싶음 | `useImperativeHandle`로 facade 설계 |
| 디자인 시스템 `<Button>`에 단순히 ref만 위임 | `useImperativeHandle` 불필요, 그냥 위임 |

facade 설계의 한 가지 실전 예시는 비디오 플레이어 래퍼입니다.

```jsx
function VideoPlayer({ ref, src }) {
  const videoRef = useRef(null);
  useImperativeHandle(ref, () => ({
    play() { videoRef.current.play(); },
    pause() { videoRef.current.pause(); },
    // .currentTime, .volume 등은 의도적으로 노출하지 않음
  }));
  return <video ref={videoRef} src={src} />;
}
```

부모는 재생/정지만 시킬 수 있고, 볼륨이나 currentTime은 props로 받아 내부에서 관리하도록 강제됩니다 — 이것이 의도한 명령형 API의 좁히기입니다.

## 흔한 실수

- **`useImperativeHandle` 없이 자식 input을 그대로 노출**: 부모가 `.value`로 직접 입력값을 읽거나 `.select()`로 선택을 조작하기 시작하면, 나중에 자식 구현을 바꿀 때 부모 코드가 줄줄이 깨집니다. 노출 API는 **의도적으로 설계**해야 합니다.
- **모든 자식에 `useImperativeHandle` 도입**: 단순 ref 위임이면 충분한 곳까지 facade를 두면 보일러플레이트만 늘어납니다. "캡슐화가 진짜로 깨질 때만" 도입하세요.
- **React 19 환경에서 `forwardRef`를 새로 도입**: 마이그레이션 맥락이 아니라면 ref-as-prop이 더 깔끔합니다.

## 복습

ref는 자동 prop이 아니므로 React 18에서는 `forwardRef`, React 19에서는 ref-as-prop으로 노출합니다. `useImperativeHandle`은 자식이 부모에게 주는 명령형 API를 의도적으로 좁히는 캡슐화 도구입니다. S2 전체로 정리하면 — ref는 "기본이 아닌 마지막 수단"이며, **타이밍**(commit 이후 읽기 [S2.C1])과 **노출 표면**([S2.C3])을 모두 설계해야 합니다. 다음 섹션은 ref가 아닌 또 다른 escape hatch — Effect로 외부 시스템과 동기화하기입니다.
