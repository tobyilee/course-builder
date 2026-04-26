# 핸들러 연결과 5단계 프로세스 마무리 — 처음부터 컴포넌트 설계하기

> LOs: LO-S1.3

## 개요

지금까지 visual state 표 [S1.C1]도 그렸고, status enum으로 state도 줄였습니다 [S1.C2]. 그런데 막상 코드를 채우려 하면 막힙니다. 왜일까요? 트리거 표는 정적인 그림이고, 핸들러는 그 화살표를 *시간 순서로 발화*시키는 일이기 때문입니다 [slide 2]. 다행히도 작업은 기계적입니다 — 표의 화살표 하나하나가 곧 setState 한 줄에 대응합니다. 이 class는 5단계의 마지막 ⑤단계를 채우고, ①~⑤를 한 번에 적용해 새 컴포넌트를 처음부터 설계해 봅니다.

## 핵심 개념

5단계 회상 — ① 상태 열거 → ② 트리거 식별 → ③ useState 모델링 → ④ 비핵심 제거 → ⑤ 핸들러 연결.

⑤단계 규칙은 단순합니다 [slide 3].

- **human 트리거** → onChange / onClick 같은 DOM 핸들러 안의 setState
- **computer 트리거** → 비동기 작업의 then / catch 안의 setState

비동기 패턴의 기본형은 이렇습니다: `setStatus('submitting')` → `await` 호출 → 성공이면 `setStatus('success')`, 실패면 `setStatus('typing') + setError(err)`. 여기서 사고 순서가 곧 설계 순서가 됩니다 — 트리거 표의 행 수와 핸들러 안의 분기 수가 일치하면 누락 없이 구현된 것입니다.

## 예시

도시 퀴즈 폼 완성 코드의 핵심부 [slide 4]:

```js
async function handleSubmit(e) {
  e.preventDefault();
  setStatus('submitting');                 // typing → submitting
  try {
    await submitForm(answer);
    setStatus('success');                  // submitting → success
  } catch (err) {
    setStatus('typing');                   // submitting → error
    setError(err);
  }
}
```

JSX 측에서는 파생값을 직접 계산해 씁니다.

```jsx
<textarea disabled={status === 'submitting'} ... />
<button disabled={answer.length === 0 || status === 'submitting'}>
  Submit
</button>
{error !== null && <p className="Error">{error.message}</p>}
```

`disabled` 두 곳 모두 useState가 아니라 식으로 계산한다는 점이 핵심입니다 — [S1.C2]의 파생값 규칙이 그대로 살아있습니다.

**보너스 — Living styleguide [slide 5]:**

```jsx
['empty','typing','submitting','success','error']
  .map(s => <Form initialStatus={s} key={s} />)
```

다섯 visual state를 한 페이지에 동시 렌더해 두면, 디자인 회귀와 PR 리뷰가 *눈으로* 끝납니다.

## 흔한 실수

- **트리거 표 없이 바로 코드부터** — 표를 건너뛰면 catch 분기에서 `setError`만 호출하고 `setStatus`를 잊는 식의 누락이 생깁니다. 표의 행 수 = setState 호출 개수가 일치하는지 점검하세요.
- **핸들러 안에서 파생값까지 set** — `setStatus('typing')` 옆에 `setIsError(true)`까지 넣는 순간 [S1.C2]의 paradox가 부활합니다. error의 존재만으로 충분합니다.
- **async 안에서 stale closure** — try/catch가 길어지면 `status` 같은 값을 핸들러 진입 시점 기준으로 읽고 있다는 점을 잊기 쉽습니다. 분기 결정은 `await` *전*에 끝내는 편이 안전합니다.

## 복습

5단계는 사고법입니다. 표를 그렸다면 핸들러는 거의 받아쓰기에 가깝습니다. 다음 섹션 [S2.C1]은 state '구조'를 다듬는 5가지 원칙 — 묶기 / 모순회피 / redundant 제거 / duplication 회피 / 평탄화로 이어집니다.
