---
name: curriculum-design
description: Design course-level and section-level curriculum scaffolding. Use when writing Learning Objectives, choosing Bloom's Taxonomy levels, splitting a topic into sections, or breaking sections into classes. Triggered by curriculum-architect and section-designer agents.
---

# Curriculum Design

ADDIE Analyze+Design 단계를 수행하는 스킬. 주제 분석 → 학습자 분석 → LO 작성 → 섹션/class 분할의 4단계를 책임진다.

## 왜 이 규칙들이 있는가
LO가 모호하면 slide/note/transcript/quiz 네 저자가 서로 다른 강의를 만든다. LO는 **공유 진실**이므로 측정 가능해야 하고, Bloom 레벨로 태깅되어야 하며, 한 번 발행되면 재번호 되지 않아야 한다.

## Bloom's Taxonomy (revised 2001)

6레벨, 각 레벨에 권장 동사:

| 레벨 | 의미 | 권장 동사 (ko) | 권장 동사 (en) |
|------|------|--------------|--------------|
| Remember | 사실·용어 회상 | 나열한다, 정의한다 | list, define, name |
| Understand | 의미 설명·요약 | 설명한다, 요약한다 | explain, summarize, describe |
| Apply | 새 상황에 사용 | 적용한다, 구현한다 | apply, implement, use |
| Analyze | 구성요소 식별·관계 분석 | 분석한다, 비교한다 | analyze, compare, differentiate |
| Evaluate | 판단·논증 | 평가한다, 정당화한다 | evaluate, justify, critique |
| Create | 새로운 산출물 설계 | 설계한다, 합성한다 | design, synthesize, compose |

**금지 동사:** "안다", "이해한다", "배운다" (측정 불가, 모호). 대신 해당 인지 활동의 구체 행동 동사 사용.

## LO 작성 템플릿
```
LO-<section_num>.<index>: <학습자는> <Bloom 동사> <대상> <조건/기준>
```
예:
- `LO-1.2`: 학습자는 RSC 페이로드의 직렬화 순서를 설명할 수 있다 (Understand)
- `LO-2.1`: 학습자는 서버 컴포넌트와 클라이언트 컴포넌트를 비교하여 적절한 선택 기준을 제시할 수 있다 (Analyze)

## Bloom 분포 규칙
- **Course 전체**: 최소 4개 레벨 커버, Remember+Understand는 합쳐서 ≤40%
- **Section 당**: 최소 3개 레벨 커버
- **Class 당**: 1~2개 LO, 보통 동일 Bloom 레벨 또는 인접 레벨

## 섹션 분할 휴리스틱

### 개수
- `section_count = round(target_duration_min / 25)`
- 최소 2, 최대 8 (너무 많으면 학습 피로)

### 순서
- 의존성 위상 정렬
- 동일 depth에서는 Remember → Understand → Apply 순 (Bloom 기반 스캐폴딩)

### 단일 주제 원칙
"React 기초"는 OK, "React + Redux + Testing"은 NO — 이런 경우 섹션 3개로 분리.

## Class 분할 휴리스틱

### 개수
- `classes_per_section = round(section_duration / 12)` (10~15분 기준)
- 보통 2~4개

### Class 경계 결정 기준
1. 개념적 경계 (하나의 개념이 끝나는 지점)
2. 실습 전환 (이론 → 예제 사이)
3. 인지 부하 한계 (한 class = 한 번의 "아하")

## 대상 학습자별 튜닝

| audience | LO 비중 | 전제조건 | 용어 |
|---------|---------|---------|------|
| beginner | Remember/Understand 60% | 최소화 | 용어마다 정의 |
| intermediate | Apply/Analyze 60% | 명시만 | 도메인 용어 자유 |
| advanced | Analyze/Evaluate/Create 70% | 상세 | 최신 논문/이슈 참조 |

## 체크리스트 (완료 전 자가검사)

- [ ] 모든 LO가 Bloom 동사로 시작하는가
- [ ] Bloom 레벨 분포가 Course ≥4, 각 Section ≥3인가
- [ ] LO id가 `LO-<sec>.<idx>` 포맷을 따르는가
- [ ] 각 섹션의 모든 LO가 class에 할당되었는가 (orphan LO 없음)
- [ ] 각 class가 1~2 LO만 가지고 있는가
- [ ] 섹션 개수와 총 duration이 target에 ±15% 이내인가

## 재실행 시 규칙
- LO id 재번호 금지 — 추가는 뒤에 붙이고, 삭제는 `deprecated: true` 마킹
- 순서 변경은 허용하되 id는 유지

## 참고
- Bloom 레벨별 quiz 문항 타입은 `quiz-generation` 스킬 참조
- beat 배분은 `class-planning` 스킬 참조
