# Source: Reacting to Input with State

## You will learn
- 선언형 vs 명령형 UI 프로그래밍 차이
- 컴포넌트가 가질 수 있는 시각적 상태(visual states) 열거
- 코드에서 시각적 상태 간 전이 트리거하기

## 명령형 vs 선언형 (Imperative vs Declarative)

명령형 = "버튼 disable, spinner show, error hide …" 처럼 매 단계 직접 명령. 차에서 운전자에게 "여기서 좌회전, 다음 신호에서 우회전" 알려주는 것에 비유.

선언형(React) = "이 visual state에서는 이 UI" 라고 선언만 하고 React가 알아서 갱신. 택시에 타서 "여기로 가주세요"만 말하는 것에 비유.

명령형의 함정:
- 새 visual state 추가 시 모든 분기를 수정해야 함
- 상호배타적 상태가 paradox로 빠질 수 있음
- 디버깅 시 어느 분기에서 UI가 깨졌는지 추적 어려움

## Form 예제 — 5개 visual states

`empty` | `typing` | `submitting` | `success` | `error`

상태 전이 트리거:
- 텍스트 입력(human) → empty ↔ typing
- Submit 클릭(human) → typing → submitting
- 네트워크 성공(computer) → submitting → success
- 네트워크 실패(computer) → submitting → error

## 5단계 프로세스

1. **시각적 상태 식별** — 가능한 모든 UI 모양을 디자이너처럼 열거
2. **트리거 결정** — 각 전이를 일으키는 human/computer 입력 명시
3. **`useState`로 모델링** — 가능하면 최소 변수로
4. **비핵심 state 제거** — 모순/중복/파생 변수 제거
5. **이벤트 핸들러 연결** — set 호출로 전이 발생

## 비핵심 state 제거 질문 3개
1. 모순(paradox)을 만드나? → 둘 다 true가 가능한 boolean 쌍을 합쳐 status enum으로.
2. 다른 변수에서 같은 정보를 얻을 수 있나? → 중복 제거 (`isEmpty` ↔ `answer.length === 0`).
3. 다른 변수의 역으로 얻을 수 있나? → `isError` ↔ `error !== null`.

## 코드 — Before (7개 변수)
```js
const [answer, setAnswer] = useState('');
const [error, setError] = useState(null);
const [isEmpty, setIsEmpty] = useState(true);
const [isTyping, setIsTyping] = useState(false);
const [isSubmitting, setIsSubmitting] = useState(false);
const [isSuccess, setIsSuccess] = useState(false);
const [isError, setIsError] = useState(false);
```

## 코드 — After (3개)
```js
const [answer, setAnswer] = useState('');
const [error, setError] = useState(null);
const [status, setStatus] = useState('typing'); // 'typing' | 'submitting' | 'success'
```

## 완성 컴포넌트
```js
import { useState } from 'react';

export default function Form() {
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('typing');

  if (status === 'success') return <h1>That's right!</h1>;

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus('submitting');
    try {
      await submitForm(answer);
      setStatus('success');
    } catch (err) {
      setStatus('typing');
      setError(err);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={answer}
        onChange={e => setAnswer(e.target.value)}
        disabled={status === 'submitting'}
      />
      <button disabled={answer.length === 0 || status === 'submitting'}>Submit</button>
      {error !== null && <p className="Error">{error.message}</p>}
    </form>
  );
}
```

## Living styleguide 패턴
모든 visual state를 한 페이지에 동시 렌더하면 회귀 검증과 디자인 검토가 쉬워진다:
```js
let statuses = ['empty','typing','submitting','success','error'];
{statuses.map(s => <Form status={s} key={s} />)}
```

## Recap
- 선언형 = 각 시각적 상태에 대한 UI 기술; 명령형 = 매 전이를 직접 지시
- 5단계: 상태 열거 → 트리거 식별 → useState 모델링 → 비핵심 제거 → 핸들러 연결
- status enum으로 boolean paradox 회피
- 파생값은 state 아닌 render 시 계산
