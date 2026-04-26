# 5원칙 한눈에 + 관련 state 묶기·모순 회피

> LOs: LO-S2.1, LO-S2.2

## 개요

`useState`를 여러 개 늘어놓으면 어딘가에서 한쪽만 갱신되어 화면이 어긋난 경험, 다들 한 번씩 있죠. `isSending=true && isSent=true` 같은 "있을 수 없는 상태"가 실제로 만들어지는 순간 [slide 1]을 떠올려 봅시다. 우리가 만난 버그의 상당수는 사실 로직이 아니라 **state 구조**에서 비롯됩니다. 이번 class에서는 동기화 버그를 차단하는 5원칙을 한눈에 훑은 뒤, 첫 두 원칙(관련 state 묶기·모순 회피)을 깊이 다룹니다.

## 핵심 개념

5원칙은 ①관련 state 묶기 ②모순 회피 ③redundant 제거 ④duplication 회피 ⑤deep nesting 평탄화 [slide 2]입니다. 다섯 항목이 따로 노는 듯 보여도 결국 한 가지 질문 — *"동기화 버그를 어떻게 차단할까?"* — 의 다른 얼굴입니다. 그 정신을 한 줄로 압축한 것이 React 공식 문서의 슬로건이죠.

> "Make your state as simple as it can be — but no simpler."

**원칙①: 관련 state 묶기.** 항상 함께 갱신되는 변수는 객체로 합칩니다. 판단 기준은 *"한 변수만 바뀌는 경우가 실제로 존재하는가?"* — 없으면 묶으세요. `(x, y)` 좌표쌍은 거의 늘 함께 움직이므로 `position` 객체가 맞습니다. 다만 묶으면 갱신 시 모든 필드를 스프레드로 복사해야 하고(`setPosition({ ...position, x: 100 })`), 폼 필드처럼 **동적 키**가 늘어나는 경우엔 객체보다 Map/배열이 더 적합합니다.

**원칙②: 모순(contradiction) 회피.** 두 boolean이 동시에 true가 될 수 있다면 그건 모순입니다. boolean이 N개면 조합은 2^N개로 폭발하고, 그중 다수가 "있어선 안 될" 상태죠. 해법은 **status enum** 단일화입니다. 보낼 수 있는 합법 상태만 문자열로 나열하고, 필요한 boolean은 거기서 derive합니다. 원칙①과의 연결도 보입니다. *"두 변수가 항상 함께 변한다"* 는 사실은 결국 **하나의 변수의 다른 표현**이었던 거예요.

## 예시

`FeedbackForm`의 before 코드 [slide 5]를 같이 읽어볼까요. `isSending`, `isSent` 두 useState가 있고, submit 핸들러는 `setIsSending(true)` → 응답 도착 후 `setIsSent(true)` + `setIsSending(false)` 순서로 호출합니다. 호출 순서를 한 줄만 빠뜨려도 두 boolean이 모두 true가 되는 모순이 만들어지죠.

```jsx
// after — status enum 단일화
const [status, setStatus] = useState('typing'); // 'typing' | 'sending' | 'sent'

async function handleSubmit(e) {
  e.preventDefault();
  setStatus('sending');
  await sendMessage(text);
  setStatus('sent');
}

const isSending = status === 'sending';
const isSent    = status === 'sent';
```

JSX는 `isSending`/`isSent` 변수를 그대로 쓰므로 마크업 변경은 거의 없습니다. 핵심은 *'sending && sent' 조합이 타입 시스템상 불가능해졌다*는 것 — 컴파일 타임 보장입니다.

## 흔한 실수

- **객체로 묶고도 spread를 빠뜨림.** `setPosition({ x: 100 })`이라고만 쓰면 `y`가 사라집니다. 객체 state는 항상 `{ ...position, x: 100 }`처럼 기존 필드를 펼쳐 넣어야 합니다.
- **모순을 boolean 추가로 "보강"하기.** isSending이 꼬이니 isError, isSuccess까지 더하면 조합은 8개로 폭증합니다. 합법 상태만 4개라면 enum 4값이 정답입니다.

## 복습

함께 변하는 변수는 묶고, 모순 가능한 boolean 쌍은 enum으로 단일화하세요. 다음 class [S2.C2]에서는 redundant state 제거와 props mirroring 안티패턴으로 들어갑니다.
