# duplication 회피 — 객체 대신 id를 저장하라

> LOs: LO-S2.3

## 개요

장바구니에서 'Pretzels' 가격을 $2에서 $5로 수정했는데, 하단 'Selected' 패널은 여전히 $2를 보여주는 미스터리 [slide 1]. 코드에 동기화 호출이 빠진 걸까요? 더 깊이 들어가 보면, 원인은 *"selectedItem 객체 자체를 state에 박아두고 list 갱신과 분리시켰다"*는 **구조적 결정**입니다. 오늘의 질문은 이렇습니다. **같은 데이터를 두 군데 보관하는 순간 무엇이 깨지는가?**

## 핵심 개념

**원칙④: 같은 정보를 두 state에 넣지 말 것** [slide 2]. duplication은 그 자체가 동기화 버그의 정의에 가깝습니다. 흔한 실수는 이거죠.

```jsx
const [items, setItems] = useState(initialItems);
const [selectedItem, setSelectedItem] = useState(items[0]); // ❌
```

이제 'items'도 state, 'selectedItem'도 state. **진실의 원천이 두 개**가 되었습니다. items의 한 필드만 갱신해도 selectedItem은 옛 객체 참조를 그대로 들고 있어 stale이 됩니다.

**처방: id만 보관하고 매 렌더에서 list로부터 derive.**

```jsx
const [selectedId, setSelectedId] = useState(0);
const selectedItem = items.find(i => i.id === selectedId);
```

이 패턴은 **SSOT(single source of truth)** 원칙의 가장 단순한 실천법입니다. 데이터의 진짜 주인은 `items` 배열 하나뿐이고, `selectedId`는 그 배열을 가리키는 *포인터*에 불과하죠. 이 사고는 [S2.C1]의 슬로건과도 이어집니다.

**트레이드오프** [slide 3]도 솔직히 봅시다.

- **객체 보관** — 장점: 즉시 접근, find 비용 0. 단점: list 변경 시 stale, JSON 직렬화 시 데이터 중복.
- **id 보관** — 장점: 항상 최신, 메모리 절약. 단점: 매 렌더 `find()` 비용, item 삭제 시 selectedId 정리 필요.

결정 기준은 단순합니다. **list가 변할 가능성이 1%라도 있으면 id가 안전.** 정적 list라면 객체 보관도 괜찮습니다.

## 예시

travel-snack 예제 [slide 4]의 before/after를 비교해 봅시다.

```jsx
// before — 두 state, 동기화 깨짐
const [items, setItems] = useState(initialItems);
const [selectedItem, setSelectedItem] = useState(items[0]);

function handleToggle(id, packed) {
  setItems(items.map(i => i.id === id ? { ...i, packed } : i));
  // selectedItem은 옛 객체 그대로 → stale
}

// after — id만 보관
const [items, setItems] = useState(initialItems);
const [selectedId, setSelectedId] = useState(0);
const selectedItem = items.find(i => i.id === selectedId);
```

이제 `items`의 어떤 필드를 바꿔도 패널은 즉시 따라옵니다. 단, **엣지 케이스** 하나는 챙겨야 합니다. 선택된 아이템이 삭제되면 `find`가 `undefined`를 반환합니다. `selectedId`를 초기화하거나 *"선택된 아이템 없음"* 빈 상태 UI를 준비하세요.

## 흔한 실수

- **selectedItem 객체 보존을 *"성능 최적화"* 라고 정당화하기.** find 한 번이 부담될 만큼 큰 list(예: 1만 행)라면 `Map`으로 인덱싱하거나 `useMemo`를 쓰는 게 정답이지, 객체를 박아두는 게 정답이 아닙니다. *측정 후 최적화* 순서를 지키세요.
- **list 갱신 시 selectedItem도 같이 setState 해서 동기화하기.** 동작은 하지만, 똑같은 일을 *두 군데서* 하고 있다는 게 문제입니다. 새 갱신 경로가 추가되는 순간 다시 깨집니다. 구조로 차단하지 못한 동기화는 결국 어디선가 새어나옵니다.

## 복습

duplication은 동기화 버그의 다른 이름입니다. 같은 데이터는 한 곳에만 두고, 객체 자체보다 **id 저장 + derive**로 SSOT를 실천하세요. 다음 class [S2.C4]에서는 깊게 중첩된 트리를 정규화로 평탄화합니다.
