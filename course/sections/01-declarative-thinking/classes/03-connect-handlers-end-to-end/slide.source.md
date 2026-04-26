---
marp: true
theme: default
paginate: true
footer: "LO-S1.3"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 18px; }
  pre { line-height: 1.35; }
  table { font-size: 22px; }
  th, td { padding: 6px 10px; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
---

<!-- beat: b1 -->

# 핸들러 연결과 5단계 마무리

### 처음부터 컴포넌트 설계하기

S1.C3 · 11분 · LO-S1.3

---

<!-- beat: b1 -->

## 표는 그렸는데, 코드는 왜 막힐까

- 트리거 표 = **정적인 그림**
- 핸들러 = 그 화살표를 **시간 순서로 발화**시키는 일
- 다행: 표의 **화살표 하나 = setState 한 줄** 1:1 매핑
- 오늘 목표
  - 5단계 마지막 ⑤단계(핸들러 연결) 채우기
  - 1~5단계를 한 번에 적용해 새 컴포넌트 설계

---

<!-- beat: b2 -->

## 5단계 회상 — 마지막 ⑤가 오늘

| 단계 | 내용 |
|---|---|
| ① | 상태 열거 |
| ② | 트리거 식별 |
| ③ | useState 모델링 |
| ④ | 비핵심 제거 |
| **⑤** | **핸들러 연결** ← 오늘 |

규칙: 트리거 표의 **각 행** = 이 이벤트에서 이 set 호출, 1:1 매핑.

---

<!-- beat: b2 -->

## 트리거 종류별 핸들러 패턴

- **human 트리거** → DOM 핸들러 안의 setState
  - `onChange`, `onClick`, `onBlur` …
- **computer 트리거** → 비동기 결과의 setState
  - `then` / `catch`, `await`, effect 정리

```js
// 비동기 패턴 핵심
setStatus('submitting');
try   { await submit(answer); setStatus('success'); }
catch (err) { setStatus('typing'); setError(err); }
```

표의 행 수 = 핸들러의 분기 수면 **누락 0**.

---

<!-- beat: b3 -->

## Form 코드 워크스루 — handleSubmit

```jsx
async function handleSubmit(e) {
  e.preventDefault();
  setStatus('submitting');           // typing → submitting
  try {
    await submitForm(answer);
    setStatus('success');            // submitting → success
  } catch (err) {
    setStatus('typing');             // submitting → error UI
    setError(err);                   // (status='typing' + error!=null)
  }
}
```

각 줄 옆 주석 = 트리거 표의 한 행. **표 → 코드** 그대로.

---

<!-- beat: b3 -->

## JSX — 파생값을 렌더에서 직접 계산

```jsx
<form onSubmit={handleSubmit}>
  <textarea
    value={answer}
    onChange={e => setAnswer(e.target.value)}
    disabled={status === 'submitting'}
  />
  <button disabled={answer.length === 0 || status === 'submitting'}>
    Submit
  </button>
  {error !== null && <p className="error">{error.message}</p>}
  {status === 'success' && <h2>That is right!</h2>}
</form>
```

`isEmpty`·`isError` 같은 파생값은 useState 없이 **그 자리에서**.

---

<!-- beat: b3 -->

## 보너스 — Living styleguide

```jsx
const statuses = ['empty','typing','submitting','success','error'];
return statuses.map(s => (
  <Form key={s} initialStatus={s} />
));
```

- 5개 visual state를 **한 페이지에 동시 렌더**
- 디자인 회귀 검증·리뷰가 쉬워진다
- C1 의 mockup 그리드가 **실제 컴포넌트로** 살아남는 그림

---

<!-- beat: b4 -->

## Mini Capstone — 5단계를 처음부터

택1: **(A) 인라인 코멘트 위젯** / **(B) 파일 업로드 버튼**

1. visual state 4~5개 펼치기 (human/computer 라벨)
2. 순진한 boolean으로 모델링
3. 3대 질문으로 status enum + 파생값으로 줄이기
4. 핸들러 1~2개에서 setStatus 만으로 전이 표현

> 점검: 내 state 개수 = status 종류 + 본질 입력값 ?

---

<!-- beat: b5 -->

## Recap — 사고법으로서의 5단계

1. **5단계는 사고법** — 상태 → 트리거 → useState → 비핵심 제거 → 핸들러
2. 핸들러는 **트리거 표 → set 호출** 의 기계적 작업이 된다
3. **Living styleguide** 로 모든 visual state 동시 렌더 → 회귀·리뷰 쉽다

> 다음 섹션(S2): state 구조의 5원칙 — 묶기·모순회피·redundant 제거·duplication 회피·평탄화
