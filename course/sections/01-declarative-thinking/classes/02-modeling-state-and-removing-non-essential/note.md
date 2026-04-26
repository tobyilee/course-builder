# useState로 모델링하고 비핵심 state 제거하기 — boolean paradox에서 status enum으로

> LOs: LO-S1.2, LO-S1.4

## 개요

지난 class [S1.C1]에서 그린 다섯 visual state를 그대로 useState로 옮기면 어떤 일이 벌어질까요? 가장 직관적인 선택은 boolean 7개를 두는 것입니다 — `isEmpty, isTyping, isSubmitting, isSuccess, isError`. 그런데 `isTyping=true`이면서 `isSuccess=true`가 동시에 될 수 있다면? 코드는 그 조합을 표현할 수 있지만, UI상으로는 절대 존재할 수 없는 *paradox* 상태입니다 [slide 2]. 실전 버그도 여기서 나옵니다 — 네트워크 실패 후 `isError=true`인데 `isSubmitting=false` 처리를 깜빡 잊으면 spinner와 에러가 함께 떠 버립니다.

## 핵심 개념

선언형 5단계 중 ③ useState 모델링과 ④ 비핵심 state 제거를 다룹니다. 핵심 도구는 **3대 질문**입니다 [slide 3].

1. **모순(paradox)을 만드나?** — 항상 정확히 하나만 true여야 하는 boolean들은 하나의 **status enum**으로 합치세요.
2. **다른 변수에서 같은 정보를 얻을 수 있나?** — 매 렌더 계산 가능한 값은 state가 아닙니다 (`isEmpty` ↔ `answer.length === 0`).
3. **다른 변수의 역(逆)인가?** — 역수 관계 역시 계산값이지 state가 아닙니다 (`isError` ↔ `error !== null`).

이 세 질문을 통과한 변수만이 진짜 **state**입니다. 사용자나 시간이 바꾸는 *입력값*만 useState에 담고, 거기서 매 렌더 계산되는 **파생값(computed at render)** 은 그냥 변수로 두세요. 후자를 useState에 넣는 순간, 두 변수를 손으로 동기화하는 책임이 생기고 그 책임은 거의 항상 깨집니다.

## 예시

도시 퀴즈 폼의 Before — 7개 useState [slide 4]:

```js
const [answer, setAnswer] = useState('');
const [error, setError] = useState(null);
const [isEmpty, setIsEmpty] = useState(true);
const [isTyping, setIsTyping] = useState(false);
const [isSubmitting, setIsSubmitting] = useState(false);
const [isSuccess, setIsSuccess] = useState(false);
const [isError, setIsError] = useState(false);
```

질문 ①을 적용 — `isTyping/isSubmitting/isSuccess`는 상호배타이므로 status enum으로 합칩니다. 에러 분기는 `status='typing' + error!==null`로 표현하면 충분합니다. 질문 ②로 `isEmpty`를, 질문 ③으로 `isError`를 제거합니다.

After — 단 3개:

```js
const [answer, setAnswer] = useState('');
const [error, setError] = useState(null);
const [status, setStatus] = useState('typing'); // 'typing'|'submitting'|'success'
```

진짜 이득은 줄 수가 아니라, *paradox 상태가 타입상 만들어지지 않는다*는 점입니다.

## 흔한 실수

- **boolean paradox** — `isTyping`과 `isSuccess`처럼 동시에 true가 되면 안 되는 boolean들을 그대로 두면 동기화 버그가 시간 문제로 터집니다. 상호배타 boolean은 즉시 enum으로.
- **파생값을 state로 저장** — `isEmpty = answer.length === 0`을 useState에 넣어두면, `setAnswer`와 `setIsEmpty`를 매번 함께 호출해야 하고 한 번이라도 빠지면 두 값이 어긋납니다. 렌더 시 그냥 계산하세요.
- **props mirroring** — 부모가 내려준 prop을 useState 초기값으로 복사하는 패턴도 같은 함정입니다. prop이 바뀌어도 내부 state는 안 바뀌어 화면이 멈춥니다. 자세한 진단은 다음 섹션 [S2.C1]에서 다룹니다.

## 복습

state는 최소로, 나머지는 render 시 계산. status enum은 존재 불가능한 상태를 타입 차원에서 막는 강력한 도구입니다. 다음 class [S1.C3]는 마지막 ⑤단계 — 트리거 표를 핸들러 코드로 옮깁니다.
