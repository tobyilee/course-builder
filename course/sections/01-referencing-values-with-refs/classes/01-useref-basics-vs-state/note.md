# useRef 기본과 state와의 차이

> LOs: LO-S1.1, LO-S1.2

## 개요

채팅 앱에 "전송 취소" 버튼을 달아본 적 있나요? `setTimeout`이 반환한 ID를 어딘가 보관해야 `clearTimeout`으로 취소할 수 있습니다 [slide 1]. 그런데 `let timeoutID` 같은 지역 변수에 두면 매 렌더마다 `null`로 리셋되어 cancel이 항상 실패하고, `useState`에 두면 setter 호출이 또 다른 재렌더를 유발합니다. 우리에게 필요한 건 "재렌더 없이 렌더 사이를 살아남는 메모 칸" — 이게 바로 ref입니다.

## 핵심 개념

`useRef`는 `{ current }` 모양의 작은 객체를 돌려줍니다 [slide 2].

```js
import { useRef } from 'react';
const ref = useRef(0); // → { current: 0 }
ref.current = 5;       // 직접 mutation
```

세 가지 속성을 기억하세요. (1) **렌더 사이 동일 객체 유지** — React는 내부적으로 `useState({ current: initial })`로 한 번 만든 객체를 매 렌더 그대로 돌려준다고 생각하면 됩니다. (2) **직접 mutation** — setter가 없고 `ref.current = ...`로 바로 바꿉니다. (3) **재렌더 트리거 안 함** — 값이 바뀌어도 화면은 그대로입니다.

state와의 비교는 세 축으로 갈립니다 [slide 3]. 재렌더 트리거(state O / ref X), mutation 방식(state는 setter / ref는 직접), 렌더 중 읽기(state는 snapshot으로 안전 / ref는 금지, 초기화 제외). 공통점은 둘 다 렌더 사이 값이 보존된다는 것. 그래서 판별 규칙은 단 한 줄로 압축됩니다 — **화면에 보일 정보면 state, 영향 없으면 ref**.

## 예시

채팅+취소(undo) 컴포넌트로 Before/After를 봅시다 [slide 4].

```js
// Before — 매 렌더마다 timeoutID가 null로 리셋
let timeoutID = null;
function handleSend() { timeoutID = setTimeout(send, 3000); }
function handleUndo() { clearTimeout(timeoutID); } // 항상 null!

// After — ref가 렌더 사이 ID를 보존
const timeoutRef = useRef(null);
function handleSend() { timeoutRef.current = setTimeout(send, 3000); }
function handleUndo() { clearTimeout(timeoutRef.current); } // OK
```

두 핸들러는 같은 `{ current }` 객체를 바라보므로 ID가 살아 있습니다. 이 timeout ID는 화면에 표시되지 않으므로 ref가 정답입니다. 만약 "몇 초 남았는지"를 화면에 띄우려면 그 카운트는 별도 state로 두어야 합니다.

## 흔한 실수

- **표시되는 값에 ref를 쓰는 실수**: 카운터 숫자나 토글 라벨처럼 화면에 직접 보이는 값을 ref에 담으면 클릭해도 화면이 안 바뀝니다. ref는 재렌더를 트리거하지 않기 때문이죠. 이런 값은 무조건 state. 자세한 진단은 [S1.C3]에서 다룹니다.
- **렌더 중 ref.current 읽기**: 렌더 함수 본문에서 `ref.current`를 분기/출력에 사용하면 같은 입력에 다른 출력이 나올 수 있어 React가 보장하는 결정성을 깹니다. 안전한 자리는 이벤트 핸들러와 Effect 안 — 렌더가 끝난 뒤입니다.

## 복습

useRef는 `{ current }` 객체를 주고, 직접 mutation해도 재렌더가 일어나지 않으며 렌더 사이 값이 보존됩니다. state vs ref는 재렌더·mutation·렌더 중 읽기 세 축으로 갈리고, "화면에 보이면 state, 영향 없으면 ref"가 핵심 규칙입니다. 다음 class [S1.C2]에서는 ref가 빛나는 실전 시나리오 셋을 코드로 직접 작성합니다.
