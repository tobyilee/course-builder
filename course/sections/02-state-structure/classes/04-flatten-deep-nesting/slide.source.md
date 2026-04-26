---
marp: true
theme: default
paginate: true
footer: "LO-S2.5"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
---

<!-- beat: b1 -->

# deep nesting 평탄화

## 트리 데이터를 정규화하기

LO-S2.5

---

<!-- beat: b1 -->
<!-- _footer: "LO-S2.5" -->

## 5단계 트리에서 leaf 하나 지우기

- `childPlaces` 가 5단계 깊이 — leaf 삭제하려면 부모 체인 5개를 **모두 복사**
- 불변 갱신 코드가 화면 한가득 — 읽기도 디버깅도 지옥
- 오늘의 질문: 트리 모양을 그대로 두는 게 정말 최선일까?

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.5" -->

## 원칙 ⑤ 깊게 중첩된 state는 평탄화하라

```js
// before — 중첩된 트리
{ id: 0, title: 'Earth', childPlaces: [
  { id: 1, title: 'Africa', childPlaces: [...] }
]}

// after — DB 정규화 스타일 (id를 키로 한 map)
{
  0: { id: 0, title: 'Earth',  childIds: [1, 42, 46] },
  1: { id: 1, title: 'Africa', childIds: [2, 10, 19] },
  // ...
}
```

장점: 어떤 노드든 **O(1) 접근**. 갱신은 해당 노드 + 부모의 `childIds` 만.

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.5" -->

## 변환 절차와 시나리오

**변환 3단계**
1. 모든 노드를 id별로 수집
2. 각 노드의 자식 객체 배열을 `childIds` 로 교체
3. 루트에는 root id만 보관

**시나리오**
- **삭제** N → 부모의 `childIds` 에서 N 제거 + `map[N]` 삭제. 부모 체인 복사 불필요
- **이동** N → 부모A의 `childIds`에서 제거, 부모B의 `childIds`에 추가. **두 곳만** 수정
- 비용: 계층 구조를 보고 싶을 땐 매번 map+childIds로 재구성 — UI는 재귀 컴포넌트가 담당

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.5" -->

## TravelPlan — before (5단계 중첩)

```jsx
const [plan, setPlan] = useState(initialTravelPlan);
// 'Pasadena' 삭제하려면 USA → North America → Americas → Earth
// 까지 4단계 부모를 모두 새 객체로 복사 + 새 childPlaces 배열 생성
```

깊이가 깊어질수록 setState 한 번에 수십 줄의 spread 가 필요해진다.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.5" -->

## TravelPlan — after (평탄화)

```jsx
// plan: { [id]: { id, title, childIds } }
const [plan, setPlan] = useState(initialTravelPlan);

function handleComplete(parentId, childId) {
  const parent = plan[parentId];
  const nextParent = {
    ...parent,
    childIds: parent.childIds.filter(id => id !== childId),
  };
  const { [childId]: _removed, ...rest } = plan;
  setPlan({ ...rest, [parentId]: nextParent });
}
```

> Immer 옵션: `useImmerReducer` 쓰면 `delete plan[id]` 같은 mutation 스타일도 OK (필수는 아님)

---

<!-- beat: b5 -->
<!-- _footer: "LO-S2.5" -->

## 자가 진단 — 댓글 트리 평탄화

```js
// before
{ id, replies: [{ id, replies: [...] }] }

// after
byId:    { [id]: { id, text, replyIds: [...] } }
rootIds: [...]
```

- 새 답글 추가 시 변경되는 셀: `byId[newId]` 추가 + `byId[parentId].replyIds` 에 push
- **트레이드오프 자가 점검**: 깊이가 2단계뿐이고 갱신이 거의 없다면 평탄화는 과잉일 수 있음

---

<!-- beat: b6 -->
<!-- _footer: "LO-S2.5" -->

## Section S2 마무리 — 5원칙 모두 체크

- ① 묶기 / ② 모순 회피 / ③ redundant 제거 / ④ duplication 회피 / ⑤ 평탄화
- 깊은 중첩 → **byId map + childIds** 로 변경 범위 O(깊이) → O(1~2)
- 5원칙은 모두 **동기화 버그 차단**의 다른 얼굴
- 다음 Section: 컴포넌트 간 state 공유 — Lifting State Up
