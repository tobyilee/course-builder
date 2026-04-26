# deep nesting 평탄화 — 트리 데이터를 정규화하기

> LOs: LO-S2.5

## 개요

5단계 깊이의 `childPlaces` 트리에서 leaf 노드 하나만 삭제하려 했더니 부모 체인 5개를 모조리 복사하는 코드를 짜고 있는 자신을 발견한 적, 있나요 [slide 1]? 불변 갱신 코드가 화면 한가득이고, 읽기도 디버깅도 지옥입니다. 이번 class의 질문은 도발적입니다. **트리 모양을 그대로 유지하는 게 정말 최선일까?** 답은 — 거의 항상 아닙니다. *"Make your state as simple as it can be — but no simpler"*. 이 슬로건이 가장 빛나는 자리이기도 하죠.

## 핵심 개념

**원칙⑤: 깊이 중첩된 state는 갱신이 어렵다 → 평탄화(flatten)하라** [slide 2]. 평탄화는 **DB 정규화 스타일**입니다. 객체 자체를 중첩하는 대신, id를 키로 하는 단일 map(`byId`)에 모든 노드를 모으고, 부모-자식 관계는 `childIds` 배열로만 표현합니다.

```js
// before — 5단계 중첩
{ id:0, childPlaces:[{ id:1, childPlaces:[{ id:2, childPlaces:[...] }] }] }

// after — byId map + childIds
{
  0: { id:0, title:'Earth',    childIds:[1,42,46] },
  1: { id:1, title:'Americas', childIds:[2,10,19] },
  2: { id:2, title:'USA',      childIds:[] },
  // ...
}
```

이 변환의 이득은 **갱신 범위의 축소**입니다 [slide 3]. 기존 트리에서 깊이 D의 노드 하나를 삭제하려면 부모 체인 D개를 전부 복사해야 했죠 — O(D). 평탄화 후엔 두 군데만 손대면 끝입니다.

- **삭제:** 부모의 `childIds`에서 N 제거 + `byId[N]` 키 삭제.
- **이동:** 부모A의 `childIds`에서 N 제거, 부모B의 `childIds`에 N 추가.

비용도 솔직히 봅시다. 화면에 *"계층 구조"* 를 그릴 때마다 `byId`와 `childIds`로 트리를 재구성해야 합니다. 다행히 이건 재귀 컴포넌트가 자연스럽게 해 주는 일입니다 — `<Place id={rootId} byId={plan} />` 식이죠. UI 렌더 비용 ≠ state 갱신 비용임을 분리해 생각하세요.

## 예시

`TravelPlan` 예제 [slide 4]: 'Earth → Americas → North America → USA → Pasadena' 5단계 트리. 'Pasadena'를 삭제하는 핸들러를 두 방식으로 비교합니다.

```jsx
// before — 부모 체인 4단계 복사
function handleDelete(targetId) {
  // USA를 새 객체로, North America를 새 객체로,
  // Americas를 새 객체로, Earth를 새 객체로... 줄줄이 복사
}

// after — 평탄화된 plan
const [plan, setPlan] = useState(initialPlan); // { [id]: { id, title, childIds } }

function handleDelete(parentId, targetId) {
  const next = { ...plan };
  next[parentId] = {
    ...next[parentId],
    childIds: next[parentId].childIds.filter(id => id !== targetId),
  };
  delete next[targetId];
  setPlan(next);
}
```

단일 `setPlan` 호출, 변경되는 셀은 두 개뿐입니다. **Immer 옵션**도 가볍게 짚어두죠. `useImmerReducer`를 쓰면 `delete plan[id]` 같은 mutation 스타일을 그대로 쓸 수 있어 코드가 더 짧아집니다. 단, 본 강의의 필수 학습은 아니에요 — *원리를 먼저, 도구는 나중에*.

## 흔한 실수

- **깊은 중첩 상태에서 부분 업데이트만 시도하기.** `setPlan({ ...plan, childPlaces: [...] })`처럼 한 단계만 펼치고 끝내면, 안쪽 깊은 노드의 변경은 *얕은 비교*에서 새 참조로 인식되지 않거나, 더 흔하게는 부모 체인 일부가 옛 참조를 그대로 들고 있어 stale 렌더가 납니다. 트리 갱신은 *"건드린 노드부터 루트까지 전부 새 객체"* 가 원칙인데, 그게 지옥이라서 평탄화하는 거죠.
- **평탄화를 모든 곳에 강요하기.** 깊이가 2단계뿐이고 갱신이 거의 없다면 평탄화는 과잉입니다. 트레이드오프를 측정하세요 — *"갱신 빈도 × 깊이"* 가 임계값을 넘을 때 평탄화의 이득이 명확해집니다.

## 복습

깊은 중첩은 `byId` map + `childIds` 배열로 평탄화합니다. 삭제·이동 시 변경 범위가 O(깊이)에서 O(1~2)로 줄어들죠. 이로써 Section S2의 5원칙 — 묶기·모순·redundant·duplication·평탄화 [S2.C1] [S2.C2] [S2.C3] — 이 모두 *"동기화 버그 차단"* 이라는 한 가지 질문의 다른 얼굴이었음을 확인했습니다. 다음 Section [S3.C1]에서는 컴포넌트 사이로 state를 끌어올리는 lifting 패턴으로 넘어갑니다.
