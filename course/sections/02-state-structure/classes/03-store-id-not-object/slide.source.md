---
marp: true
theme: default
paginate: true
footer: "LO-S2.3"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
---

<!-- beat: b1 -->

# duplication 회피

## 객체 대신 id를 저장하라

LO-S2.3

---

<!-- beat: b1 -->
<!-- _footer: "LO-S2.3" -->

## Pretzels 가격을 바꿨는데 'Selected'는 옛값?

- 장바구니에서 `Pretzels` 가격을 $2 → $5로 수정
- 리스트의 가격은 갱신됐지만 하단 'Selected' 패널은 $2 그대로
- 원인: state에 **객체 자체**(`selectedItem`)를 박아두고 list 갱신과 분리됨
- 오늘의 질문: 같은 데이터를 두 군데 보관하는 순간 **무엇이 깨지는가?**

---

<!-- beat: b2 -->
<!-- _footer: "LO-S2.3" -->

## 원칙 ④ 같은 정보를 두 state에 넣지 말 것

```jsx
// X — 진실의 원천이 두 개 (items, selectedItem)
const [items, setItems]               = useState(initialItems);
const [selectedItem, setSelectedItem] = useState(items[0]);

// O — id만 저장, list로부터 derive
const [items, setItems]           = useState(initialItems);
const [selectedId, setSelectedId] = useState(0);
const selectedItem = items.find(i => i.id === selectedId);
```

duplication = 동기화 버그의 정의. **SSOT** (single source of truth) 의 실천법.

---

<!-- beat: b3 -->
<!-- _footer: "LO-S2.3" -->

## 트레이드오프 — 객체 vs id

| 보관 방식 | 장점 | 단점 |
|---|---|---|
| **객체 자체** | 즉시 접근, find 비용 0 | list 변경 시 stale, JSON 직렬화 시 중복 |
| **id 만** | 항상 최신, 메모리 절약 | 매 렌더 `find()`, 삭제 시 id 정리 필요 |

결정 기준: **list가 변하지 않으면** 객체도 OK. **변할 가능성이 1%라도 있으면** id가 안전.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.3" -->

## travel-snack — before / after

```jsx
// before — 체크박스 토글 시 selectedItem이 stale
const [items, setItems]               = useState(initialItems);
const [selectedItem, setSelectedItem] = useState(items[0]);

function handleToggle(id, checked) {
  setItems(items.map(i =>
    i.id === id ? { ...i, packed: checked } : i
  ));
  // selectedItem은 갱신 안 함 → 패널이 stale
}
```

---

<!-- beat: b4 -->
<!-- _footer: "LO-S2.3" -->

## travel-snack — after (id 저장 + derive)

```jsx
const [items, setItems]           = useState(initialItems);
const [selectedId, setSelectedId] = useState(0);

const selectedItem = items.find(i => i.id === selectedId);
// items의 어떤 필드를 바꿔도 패널이 즉시 따라옴
```

엣지 케이스: 선택된 아이템이 **삭제되면** `find` 가 `undefined` → `selectedId` 초기화 또는 빈 상태 UI 필요

---

<!-- beat: b5 -->
<!-- _footer: "LO-S2.3" -->

## 자가 진단 — 트리거 1개를 찾아라

```jsx
const [user, setUser] = useState(users[0]);
// ... 어딘가에서
users.map(u => u.name = await fetchName(u.id));
```

- `users` 가 갱신되어도 `user` 는 **옛 객체** → id 저장 + derive로 변경
- list가 1만 개라 `find()` 가 부담? → **Map 인덱싱** 또는 `useMemo`. 단, **측정 후 최적화**

---

<!-- beat: b6 -->
<!-- _footer: "LO-S2.3" -->

## Recap — id를 저장하라

- duplication = 동기화 버그. **같은 데이터는 한 곳에만**
- 객체 자체보다 **id 저장 + derive** 가 SSOT 실천법
- 엣지: 삭제 시 selectedId 정리, 큰 list는 Map/메모로 보강
- 다음 class: **깊게 중첩된 트리**를 정규화로 평탄화
