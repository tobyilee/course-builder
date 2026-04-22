---
name: quiz-generation
description: Generate section-level quizzes (5-9 items) with Bloom balance, plausible distractors, LO mapping, and required explanations. Use when creating quiz.json after all classes in a section are complete. Triggered by the quiz-master agent.
---

# Quiz Generation — Section-Level Assessment

섹션 끝에서 **summative** 평가를 수행. class 단위가 아닌 **섹션 단위**인 이유: class는 formative(배우는 중), section은 summative(개념 연결 평가).

## 문항 수
- **5~9개**, 10개 절대 금지
- 기준 공식: `round(section_duration / 15)`, 최소 5, 최대 9
- 동일 LO에 2문항 허용 (복수 관점 평가)

## Bloom 분포 (문항 배분)

| Section 유형 | Remember | Understand | Apply | Analyze | Evaluate | Create |
|-------------|----------|------------|-------|---------|----------|--------|
| 입문 섹션 | 1~2 | 2 | 1~2 | 1 | - | - |
| 중급 섹션 | 0~1 | 1 | 2 | 2 | 1 | - |
| 고급 섹션 | 0 | 0~1 | 1 | 2 | 1~2 | 1 |

**필수:** `Apply+Analyze ≥ 2`. 단순 암기 위주 평가 금지.

## 문항 타입

### `mcq_single` (단일 선택)
- 선택지 4개 고정
- 정답 정확히 1개
- Bloom: Remember~Analyze 모두 가능

```json
{
  "id":"S1.Q1", "type":"mcq_single",
  "stem":"서버 컴포넌트가 포함되지 않는 번들은?",
  "choices":["서버 번들","클라이언트 번들","Edge 런타임","SSR 출력"],
  "correct":["B"],
  "explanation":"서버 컴포넌트는 서버에서만 실행되고 클라이언트 번들에 직렬화된 페이로드만 전달됩니다.",
  "distractor_rationales":{
    "A":"서버 번들에는 포함됩니다 — 오히려 당연",
    "C":"Edge 런타임도 서버 환경의 일종",
    "D":"SSR 출력에도 RSC 결과가 들어갑니다"
  },
  "lo_ids":["LO-1.2"], "bloom":"Understand", "difficulty":3
}
```

### `mcq_multi` (복수 선택)
- 선택지 4~5개
- 정답 2~3개, 선지문에 **정답 수 명시** ("다음 중 맞는 것 2개를 고르시오")
- 채점: 부분점수 or 올오낫싱 명시

### `true_false`
- **개념 오해 교정**용으로만 사용
- stem은 교과서적 정답이 아닌 **학습자가 헷갈리는 명제**
- Bloom은 Understand/Analyze에 한정 (Remember에는 부적합 — 너무 쉬움)

### `short_answer`
- 자기채점용, rubric 필수
```json
{
  "type":"short_answer",
  "stem":"서버 컴포넌트와 SSR의 차이를 2문장으로 설명하시오.",
  "rubric":[
    "서버 컴포넌트는 클라이언트 번들 제외 (1pt)",
    "SSR은 HTML 문자열을 렌더링 (1pt)",
    "두 기술은 동시 사용 가능 (1pt)"
  ],
  "lo_ids":["LO-1.3"], "bloom":"Analyze"
}
```

## Distractor (오답 선지) 품질

### 원칙
- **plausible** (학습자가 실제로 할 법한 오해)
- 정답과 길이·디테일 균형
- 문법적·구조적으로 정답과 동일 패턴

### 좋은 distractor 생성법
1. 학습자의 흔한 오개념 수집 (note의 Pitfalls 섹션 참조)
2. 비슷한 개념과 혼동 유도 (SSR vs RSC vs CSR)
3. 맞는 말이지만 질문에 답하지 않는 서술

### 나쁜 distractor
- "모든 것", "아무것도" (보통 오답)
- 이상하게 짧거나 긴 것 (정답이 드러남)
- 명백히 거짓 (학습 가치 없음)

## Explanation 규칙
- **모든 문항** 필수
- 정답 해설 + (mcq류) 각 오답별 왜 틀렸는지
- 최소 2문장, 최대 5문장
- 설명이 곧 미니 복습 — 투자 가치 있음

## LO Coverage
- 섹션의 모든 LO가 ≥1 문항에 등장 (critical)
- 한 문항이 여러 LO를 평가할 수 있음 (mcq_multi, short_answer에서 흔함)

## Difficulty 평가
- 1 (쉬움, 정답 명백) ~ 5 (어려움, 여러 개념 결합)
- 섹션 평균 3 근처, 5는 1~2개만

## 출력 스키마

```json
{
  "section_id": "S1",
  "items": [ /* 5~9개 */ ],
  "bloom_distribution": {"Remember":1,"Understand":2,"Apply":2,"Analyze":1},
  "lo_coverage": {"LO-1.1":["S1.Q1"],"LO-1.2":["S1.Q2","S1.Q3"],"LO-1.3":["S1.Q4"]}
}
```

## 검증 (자체 수행)
- 문항 수 5~9
- mcq_single의 correct 배열 길이 == 1
- mcq_multi의 correct 배열 길이 2~3 + stem에 개수 명시
- 모든 문항 explanation 비어있지 않음
- 섹션 LO 전체가 lo_coverage에 등장
- Bloom 분포 ≥3 레벨

## 재실행 규칙
- 문항 id 재번호 금지
- 부분 교체 시 해당 문항만 수정
- Bloom 분포 유지 (특정 레벨 추가/제거 시 주의)
