---
marp: true
theme: default
paginate: true
footer: "LO-S4.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  blockquote { color: #555; border-left: 4px solid #888; }
---

<!-- beat: b1 -->

# 그 useEffect, 정말 필요할까?

### Effect 안 써도 되는 경우 — 진단 프레임

코드베이스의 `useEffect` 70%는 사실 Effect가 아니어도 된다.

> "외부 시스템이 없으면, Effect도 필요 없다."

---

<!-- beat: b2 -->
<!-- _footer: "LO-S4.1" -->

## 복습 — Effect의 정의

- Effect는 **외부 시스템과의 동기화** escape hatch
- 외부 시스템 = 서버, DOM, 타이머, 브라우저 API
- 외부가 없는데 Effect를 쓰면 발생하는 비용 3가지:
  - 불필요한 추가 렌더 (`render → Effect → setState → 재렌더`)
  - dev Strict Mode에서 두 번 실행 → 중복 부작용
  - 의존성 배열 관리 부담 → stale·무한루프 위험

---

<!-- beat: b3 -->
<!-- _footer: "LO-S4.1" -->

## 12가지 안티패턴, 5개 그룹

- **A · Derived state** — #1 props/state 갱신, #2 비싼 계산 캐싱
- **B · State 리셋/조정** — #3 전체 리셋, #4 부분 조정
- **C · 인터랙션 vs 표시** — #5 핸들러 공유, #6 POST, #7 체인, #8 초기화, #9 부모 통지, #10 부모 데이터 전달
- **D · 외부 통합** — #11 store 구독, #12 fetch race
- 다음 4개 클래스가 각 그룹을 Before/After로 채운다

---

<!-- beat: b4 -->
<!-- _footer: "LO-S4.1" -->

## 결정 트리 — 5개 질문

```text
Q1. render 중 계산 가능?       → 변수 한 줄
        ↓ 아니오
Q2. 비싼 계산?                  → useMemo
        ↓ 아니오
Q3. 사용자 인터랙션 결과?      → 핸들러
        ↓ 아니오
Q4. prop 변경 시 리셋?         → key prop / state-during-render
        ↓ 아니오
Q5. 외부 store / fetch?        → useSyncExternalStore / Effect
```

> Effect는 **마지막 leaf**에서만 정당하다.

---

<!-- beat: b5 -->
<!-- _footer: "LO-S4.1" -->

## 미니 케이스 3개 — 트리 따라가기

- **Case 1**: `firstName + lastName`
  → Q1에서 즉시 종료, **render 중 계산**
- **Case 2**: 폼 제출 시 POST
  → Q3에서 분기, **핸들러**
- **Case 3**: `navigator.onLine` 구독
  → Q5에서 분기, **useSyncExternalStore**

> 하나의 트리, 12가지 leaf로 모든 안티패턴이 흡수된다.

---

<!-- beat: b6 -->
<!-- _footer: "LO-S4.1" -->

## 잠깐 — 여러분이 풀어볼 케이스

- 시나리오: *"검색어가 바뀌면 결과 목록을 갱신하는 Effect"*
- 힌트
  - 검색어 = props/state
  - 결과 목록 = derived처럼 보이지만…
  - **fetch는 외부 시스템** (Q5)
- 정답 미리보기는 **S4.C5**에서 — 지금은 트리를 한 번 따라가 보는 것이 목적

---

<!-- beat: b7 -->
<!-- _footer: "LO-S4.1" -->

## 정리 — 오늘의 한 장

- Effect는 **외부 시스템 동기화 전용** escape hatch
- 12가지 안티패턴 → **5그룹 · 5질문** 결정 트리로 압축
- 다음 4개 클래스가 트리의 각 가지를 Before/After로 채운다
- 핵심 자세: *"먼저 트리를 따라가고, 마지막에야 Effect"*
