---
marp: true
theme: default
paginate: true
footer: "LO-S4.3"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  blockquote { color: #555; border-left: 4px solid #888; }
---

<!-- beat: b1 -->

# 다른 사람에게 보낸 댓글

### State 리셋과 조정 — key와 state-during-render

`userId`가 바뀌었는데 댓글 입력이 그대로 남아 다른 사용자에게 전송될 뻔한 버그.

> 흔한 처방 `useEffect(() => setComment(''), [userId])` — 이게 진짜 답일까?

---

<!-- beat: b2 -->
<!-- _footer: "LO-S4.3" -->

## 안티패턴 #3 — 전체 state 리셋을 Effect로

- Effect 처방의 진짜 문제 3가지
  - 한 프레임 깜빡임 (이전 값으로 한 번 렌더 후 리셋)
  - dev 더블 마운트에서 두 번 실행
  - 새 state를 추가할 때마다 리셋 누락 위험
- 더 깔끔한 답: **`key` prop**으로 인스턴스 자체를 갈아끼움
- React 입장에서는 다른 컴포넌트 → 모든 state가 자연스럽게 초기값

---

<!-- beat: b3 -->
<!-- _footer: "LO-S4.3" -->

## Before / After — Profile 리셋

```tsx
// Before — 자식 안에서 Effect로 리셋
function Profile({ userId }) {
  const [comment, setComment] = useState('');
  useEffect(() => { setComment(''); }, [userId]);
  // ... 새 state 추가할 때마다 잊지 말 것!
}

// After — 부모에서 key 한 단어
<Profile userId={userId} key={userId} />
// 자식의 useEffect는 통째로 삭제
```

> 5줄짜리 Effect → 부모의 `key` 한 단어로 대체.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S4.3" -->

## 안티패턴 #4 — 일부 state만 조정

- 전체 리셋이 과한 경우: 일부만 조정해야 할 때
- **1순위**: derived value로 — selection을 state가 아니라 `items.find(...)`로 매번 도출
- **2순위**: state-during-render — 렌더 중 prevItems 비교 후 `setSelection(null)`
- 3순위: Effect (마지막 후보)
- state-during-render가 합법인 이유: 같은 렌더 안에서 즉시 재실행, 자식 영향 없음, paint 1회 절약

---

<!-- beat: b5 -->
<!-- _footer: "LO-S4.3" -->

## Before / After — items 바뀌면 selection 무효화

```tsx
// Before — Effect, 깜빡임 1회
useEffect(() => { setSelection(null); }, [items]);

// After (state-during-render)
const [prevItems, setPrevItems] = useState(items);
if (items !== prevItems) {
  setPrevItems(items);
  setSelection(null);
}

// Best (derived) — selection을 state에서 제거
const selection =
  items.find(i => i.id === selectedId) ?? null;
```

---

<!-- beat: b6 -->
<!-- _footer: "LO-S4.3" -->

## 잠깐 — 어느 가지로 갈까?

- **Q1**. *"모달이 열릴 때마다 폼 입력을 빈 값으로"*
  → 전체 리셋 → 모달에 `key={openId}` 추가
- **Q2**. *"정렬 기준이 바뀌면 페이지 번호만 1로"*
  → 부분 조정 → derived 가능? 어렵다면 state-during-render
- 결정 규칙 한 문장: *"전부 비울 거면 key, 일부만이면 derived 우선"*

---

<!-- beat: b7 -->
<!-- _footer: "LO-S4.3" -->

## 정리 — Q4 가지 채우기

- **전체 리셋** → `key` prop 한 단어
- **부분 조정** → derived 우선, 안 되면 state-during-render
- **Effect로 setState** 처방은 깜빡임·이중 호출·확장성 문제로 마지막 후보
- 다음: 인터랙션 vs 표시 — 핸들러로 옮겨야 할 6가지 (Q3)
