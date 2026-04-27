# ref={...}로 DOM 만지기 — focus·scroll·measure·play

> LOs: LO-S2.1, LO-S2.2

## 개요

검색 페이지를 열자마자 입력창에 커서가 들어가 있으면 좋겠다고 생각해 본 적 있나요? 이 단순해 보이는 동작은 React의 선언형 모델만으로는 표현되지 않습니다 [slide 1]. 텍스트, 색, 조건부 렌더는 JSX로 충분히 그릴 수 있지만 `focus()`, `scrollIntoView()`, `video.play()`, `getBoundingClientRect()` 같은 **명령형 브라우저 API**는 "지금, 이 노드에 대해" 직접 호출해야 합니다. 이런 순간을 위해 React가 남겨둔 escape hatch가 바로 `ref={...}` 패턴이며, 이번 시간에는 그 사용법과 함께 "언제 ref를 읽어도 되는가"라는 타이밍 모델을 함께 잡습니다.

## 핵심 개념

**ref로 DOM 노드를 잡는 절차는 두 줄이면 끝납니다.** `useRef(null)`로 ref 객체를 만들고, JSX에서 `<input ref={inputRef} />`처럼 노드에 부착합니다 [slide 2]. 그러면 React가 commit phase에서 `inputRef.current = <실제 DOM node>`를 채워 넣어 줍니다. 이후로는 `inputRef.current.focus()`처럼 표준 DOM API를 직접 호출하면 됩니다.

여기서 반드시 잡고 가야 하는 것은 **ref가 부착되는 타이밍**입니다 [slide 3]. React가 한 번의 업데이트를 처리하는 흐름은 크게 두 단계로 나뉩니다.

- **render phase**: 컴포넌트 함수가 호출되어 JSX를 반환하기만 한 상태. 이 시점에 `ref.current`는 아직 `null`입니다.
- **commit phase**: React가 실제 DOM을 만들거나 갱신하면서 `ref.current`에 노드를 꽂아 넣습니다. 업데이트 때는 노드 교체 직전에 `null`로 초기화했다가 다시 설정합니다.

따라서 ref는 **이벤트 핸들러나 Effect "안에서만"** 안전하게 읽을 수 있습니다. 렌더 본문에서 `ref.current.focus()`를 부르면 첫 렌더에서는 `null.focus()`로 터지고, 운 좋게 마운트 이후 재렌더라도 React의 commit 흐름과 어긋나는 부수 효과가 됩니다. "내가 ref를 만지는 위치는 commit 이후인가?"라는 한 줄 질문을 머릿속에 박아두면 이후 모든 ref 코드의 안전성을 스스로 판정할 수 있습니다.

또 한 가지, **하나의 ref는 하나의 노드**에 대응합니다. 동적으로 늘어나는 리스트 항목 각각을 잡고 싶다면 `Map`이나 콜백 ref 패턴이 별도로 필요하다는 점을 기억해 두세요.

## 예시

세 가지 전형적인 사용처를 살펴봅니다 [slide 4]. 모두 **이벤트 핸들러 또는 Effect 안에서** ref를 읽는다는 공통점에 주목하세요.

```jsx
// 1) 검색창 자동 포커스 — 클릭 핸들러
function SearchBox() {
  const inputRef = useRef(null);
  return (
    <>
      <input ref={inputRef} />
      <button onClick={() => inputRef.current.focus()}>Focus</button>
    </>
  );
}

// 2) 카드로 부드럽게 스크롤 — 클릭 핸들러
cardRef.current.scrollIntoView({
  behavior: 'smooth',
  block: 'nearest',
  inline: 'center',
});

// 3) 선언형 state + 명령형 호출 — Effect
useEffect(() => {
  isPlaying ? videoRef.current.play() : videoRef.current.pause();
}, [isPlaying]);
```

세 번째 예제가 특히 흥미롭습니다. `isPlaying`이라는 **선언형 state**가 진실의 원천이고, ref는 단지 그 상태를 브라우저 비디오 요소에 "전달"하는 통로일 뿐입니다. ref는 state를 대체하지 않고, state가 닿지 못하는 곳을 메꾸는 도구라는 점을 잊지 마세요.

## 흔한 실수

- **렌더 도중 `.focus()` 호출**: `return <input ref={inputRef} />` 위쪽에서 `inputRef.current.focus()`를 부르는 코드. 첫 렌더에서는 `null`이라 즉시 크래시합니다. 마운트 시 자동 포커스가 필요하면 `useEffect(() => { inputRef.current.focus(); }, [])`로 옮기세요.
- **render 중 `console.log(ref.current)`로 디버깅**: 항상 `null`로 보여서 "왜 ref가 안 붙지?"라고 헷갈리기 쉽습니다. commit 이후를 보려면 Effect나 핸들러로 옮겨 찍어야 합니다.

## 복습

`useRef` + `ref={...}`로 DOM 노드를 잡아 focus·scroll·play·measure 같은 명령형 작업을 수행합니다. 타이밍은 render에서 `null`, commit 이후에만 채워지므로 핸들러나 Effect 안에서만 읽습니다. 다음 시간에는 `setState` 직후 새 DOM을 즉시 측정해야 할 때 쓰는 `flushSync`, 그리고 직접 DOM 조작이 위험한 이유를 봅니다 [S2.C2].
