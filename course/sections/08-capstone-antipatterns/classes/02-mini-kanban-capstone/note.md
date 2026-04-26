# 통합 케이스 스터디 — mini Kanban 앱 의사결정 사슬
> LOs: LO-S8.2

## 개요

앞 클래스([S8.C1])에서는 망가진 코드를 진단했습니다. 이번엔 반대 방향입니다 — **0에서 시작해 4번의 의사결정만으로 reducer + context 구조에 도달**하는 길을 직접 걸어봅니다 [slide 1]. 소재는 Todo보다 한 단계 큰 mini Kanban: 컬럼 3개(Todo/Doing/Done)와 카드 이동·추가·삭제. 각 결정이 강의 어느 챕터의 원칙으로 정당화되는지 한 호흡에 묶으며 강의 전체를 마무리합니다.

## 핵심 개념

네 단계는 순서가 중요합니다. 앞 결정이 뒤 결정의 전제를 깔아주기 때문입니다 [slide 2].

- **결정 ① state shape** — 카드를 `columns[0].cards[2]`처럼 트리에 둘지, `cards = {byId, allIds}` + `columns = {byId: {cardIds: []}}`로 정규화할지. Kanban의 핵심 동작은 "카드 이동"이고, 트리 구조에서는 두 컬럼을 동시에 deep update해야 합니다. 정규화하면 `cardIds` 배열 두 개만 갱신하면 끝 — 변경 라인 수가 압도적으로 적습니다. 근거: [S2.C4] deep nesting 평탄화.
- **결정 ② state 위치** — `Card`? `Column`? `Board`? `App`? 카드 이동은 두 컬럼이 동시에 바뀌므로, **두 컬럼의 가장 가까운 공통 부모**인 `Board`가 owner여야 합니다. App까지 올릴 필요는 아직 없습니다 — 라우팅/auth가 끼면 그때 다시 평가. 근거: [S3.C3] lifting state up.
- **결정 ③ setState 흩어짐 vs reducer** — `Board`에 `addCard`, `removeCard`, `moveCard`, `renameCard`, `addColumn`, `removeColumn`… `setState` 호출 6개가 흩어집니다 [slide 4]. 상호작용이 5개를 넘고 여러 state를 동시에 갱신한다면 `(state, action) => nextState`로 통합할 시점입니다. 보너스: reducer는 순수 함수라 입력→출력만으로 단위 테스트가 됩니다. 근거: [S5.C4].
- **결정 ④ prop drilling 임계점** — `Card`의 삭제 버튼이 `dispatch`를 4단계 통과해 받습니다. 여기가 context 도입 시점인데, **state context와 dispatch context를 분리**합니다. 분리하면 dispatch만 쓰는 컴포넌트는 state 변경 시 재렌더되지 않습니다. 근거: [S7.C1] 분리 이유 + [S7.C2] 단일 파일 응집.

네 결정의 결과물은 `KanbanProvider` 한 파일입니다 — `useReducer` + `<KanbanStateContext>` + `<KanbanDispatchContext>` + `useKanban` / `useKanbanDispatch` 커스텀 훅이 한 군데 모입니다.

## 예시

최종 골격을 30초만 살펴봅시다 [slide 6].

```tsx
// KanbanProvider.tsx — 단일 파일 응집 (S7.2)
const StateCtx = createContext(null);
const DispatchCtx = createContext(null);

function reducer(state, action) {
  switch (action.type) {
    case 'card_moved': /* cardIds 두 배열만 수정 */
    case 'card_added': /* byId + 한 컬럼 cardIds */
    case 'card_removed': /* ... */
  }
}

export function KanbanProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initial);
  return (
    <StateCtx value={state}>
      <DispatchCtx value={dispatch}>{children}</DispatchCtx>
    </StateCtx>
  );
}
export const useKanban = () => useContext(StateCtx);
export const useKanbanDispatch = () => useContext(DispatchCtx);
```

`Board`는 `useKanban()`으로 read만 하고, `Card`의 삭제 버튼은 `useKanbanDispatch()`로 직접 dispatch — drilling 0단계입니다. 새 도메인(Auth, Theme)이 붙으면 같은 패턴을 복제하면 됩니다 ([S7.C2]). Redux/Zustand 같은 외부 라이브러리는 미들웨어/devtools가 정말 필요해질 때 도입을 검토하면 됩니다 ([S7.C2]).

## 흔한 실수

순서를 건너뛰면 비싸집니다. **결정 ①을 미루고 ③ reducer로 직행**하는 경우가 가장 흔한데, 트리 구조 위에 reducer를 얹어도 case마다 deep update가 그대로 남아 reducer가 누더기가 됩니다. 또 하나, **처음부터 ④ context로 직행**하는 함정도 잦습니다. prop drilling이 실제로 아프기 전(보통 3단계 미만)까지는 props가 더 명시적이고 추적도 쉽습니다 — 근거 없는 조기 추상화는 비용입니다.

## 복습

4단계 의사결정 사슬: **state shape([S2.C4]) → 위치([S3.C3]) → reducer([S5.C4]) → reducer+context([S7.C1]~[S7.C2])**. 각 결정의 근거는 강의 7개 챕터 원칙으로 모두 정당화됩니다. 강의 끝. 이제 코드 리뷰와 신규 설계 양쪽에서 같은 언어로 사고합시다.
