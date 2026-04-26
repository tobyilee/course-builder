---
marp: true
theme: default
paginate: true
footer: "LO-S8.2"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 19px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# mini Kanban 의사결정 사슬

## 0에서 reducer+context까지, 4번의 결정

- 컬럼 3개 + 카드 이동/추가/삭제 — Todo보다 한 단계 큰 케이스
- 결정 ① state shape → ② 위치 → ③ reducer → ④ context 분리
- 강의 전체를 한 그림으로 묶는 마지막 화이트보드 세션

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.5" -->

## 결정 ① state shape — 트리 vs 정규화

```ts
// 트리: 직관적이지만 카드 이동 = deep update 지옥
columns[0].cards[2] // 접근은 쉬움
// moveCard: 두 컬럼의 cards 배열을 동시에 spread × spread...

// 정규화: 카드 이동 = 두 줄 변경
cards   = { byId: { c1: {...}, c2: {...} }, allIds: [...] }
columns = { byId: { col1: { cardIds: ['c1','c3'] } } }
```

- 핵심 동작이 "카드 이동"이면 **정규화 압승** (S2.5)
- id 보관 트레이드오프: stale 위험 vs 동기화 단순성 (S2.3)

---

<!-- beat: b3 -->
<!-- _footer: "LO-S3.3" -->

## 결정 ② state 위치 — 누가 들고 있나

- 카드 이동 = **두 컬럼이 동시에** 바뀜 → 공통 부모 필요
- single source of truth: `Board`가 cards/columns 모두 보유
- 자식(Column, Card)엔 **props로 내려준다**
- App까지 올릴 필요는 아직 없음 — 라우팅/auth 끼면 그때 재평가
- 근거: **S3.3 가장 가까운 공통 부모로 lifting**

---

<!-- beat: b4 -->
<!-- _footer: "LO-S5.4" -->

## 결정 ③ setState 흩어짐 → reducer

```ts
// before: Board 안에 setState 6개가 흩어짐
addCard, removeCard, moveCard,
renameCard, addColumn, removeColumn  // 곧 한계

// after: dispatch 한 줄 + 순수 함수
dispatch({ type: 'card_moved', from, to, cardId });

function kanbanReducer(state, action) {
  switch (action.type) {
    case 'card_moved': return { ...state, columns: ... };
    case 'card_added': return ...;
  }
}
```

- 상호작용 5개 넘고 여러 state 동시 갱신 → **reducer 승** (S5.4)

---

<!-- beat: b5 -->
<!-- _footer: "LO-S7.2" -->

## 결정 ④ prop drilling 임계 → context 분리

- Card의 삭제 버튼이 dispatch를 4단계 통과해서 받는다 → 한계
- **state context와 dispatch context를 분리** (불필요 재렌더 방지, S7.1)
- 단일 파일 응집 패턴 (S7.2):

```tsx
// KanbanProvider.tsx
const StateCtx = createContext(null);
const DispatchCtx = createContext(null);
export function KanbanProvider({ children }) {
  const [state, dispatch] = useReducer(kanbanReducer, initial);
  return <StateCtx value={state}><DispatchCtx value={dispatch}>
    {children}</DispatchCtx></StateCtx>;
}
export const useKanban = () => useContext(StateCtx);
export const useKanbanDispatch = () => useContext(DispatchCtx);
```

---

<!-- beat: b6 -->

## 최종 구조 30초 투어

- `KanbanProvider` 1파일 — reducer + 두 context + 두 훅 응집
- `Board`는 `useKanban()`으로 read
- `Card` 삭제 버튼은 `useKanbanDispatch()`로 직접 dispatch — **drilling 0단계**
- 새 도메인(Auth, Theme) 추가? **같은 패턴 복제** (S7.3)
- Redux/Zustand는? 미들웨어/devtools 필요할 때 (S7.4)

---

<!-- beat: b7 -->

## 자문자답 — 내 앱은 어디쯤?

- 정규화를 미루고 있나? → 결정 ①에서 막혀있다
- lifting 위치가 애매한가? → 결정 ②
- setState가 6개 넘게 흩어져 있나? → 결정 ③
- props drilling 4단계 이상? → 결정 ④
- 다음 PR에서 이 4단계 사슬을 그대로 따라가보자

---

<!-- beat: b8 -->

## 강의 끝 — 같은 언어로 사고하기

- **shape (S2.5) → 위치 (S3.3) → reducer (S5.4) → +context (S7.1~7.2)**
- 4번의 결정 모두, 강의 7개 챕터 원칙으로 정당화됨
- 코드 리뷰와 신규 설계 양쪽에서 같은 어휘로 말할 수 있다
- 수고하셨습니다 — 이제 진짜 시작입니다
