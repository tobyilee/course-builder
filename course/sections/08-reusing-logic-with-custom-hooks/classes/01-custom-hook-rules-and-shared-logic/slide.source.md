---
marp: true
theme: default
paginate: true
footer: "LO-S8.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
---

<!-- beat: b1 -->

# Custom Hook의 규칙

## use 접두사와 '로직만 공유' 원칙

두 컴포넌트의 똑같은 5줄, 한 줄로 줄이고 싶다

---

<!-- beat: b1 -->

## 같은 코드가 두 번 — 줄이고 싶다

```jsx
// StatusBar
const [isOnline, setIsOnline] = useState(true);
useEffect(() => {
  const on = () => setIsOnline(true);
  const off = () => setIsOnline(false);
  window.addEventListener('online', on);
  window.addEventListener('offline', off);
  return () => { /* cleanup */ };
}, []);
// SaveButton에도 똑같은 5줄...
```

목표: `const isOnline = useOnlineStatus();` 한 줄로

---

<!-- beat: b2 -->

## 'use' 접두사는 약속이다

- Custom Hook = React Hook을 호출하는 **함수** (컴포넌트 아님)
- 이름은 반드시 `use` + 대문자로 시작 — `useOnlineStatus`, `useChatRoom`
- 강제 이유 ① ESLint가 use* 함수 안에서만 다른 Hook 호출 허용
- 강제 이유 ② top-level 호출 규칙 검사 활성화
- 강제 이유 ③ 읽는 사람에게 "안에 state/effect 있을 수 있음" 신호

---

<!-- beat: b2 -->

## use를 붙여도 되는가? (✅/❌)

```jsx
// ✅ Hook을 호출함 — use OK
function useAuth() {
  return useContext(AuthContext);
}

// ❌ Hook 호출 없음 — 그냥 함수여야 함
function useSorted(items) {
  return items.slice().sort();
}
// → sortItems(items) 로 이름 바꾸기
```

`use`는 "내가 Hook을 부른다"는 약속이지, "특별한 함수다"가 아니다

---

<!-- beat: b3 -->

## 핵심 — 로직 공유, state는 공유 X

```text
              window 'online'/'offline' 이벤트 (외부)
                    │            │
                    ▼            ▼
   ┌─────── useOnlineStatus() (도면) ───────┐
   │                                          │
   ▼                                          ▼
 StatusBar                               SaveButton
 [isOnline #A]                           [isOnline #B]   ← 독립 slot
```

같은 청사진(blueprint), 두 채의 집 — 도면은 공유, 집은 별개

---

<!-- beat: b4 -->

## useOnlineStatus 구현

```jsx
function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);
  useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener('online', on);
    window.addEventListener('offline', off);
    return () => {
      window.removeEventListener('online', on);
      window.removeEventListener('offline', off);
    };
  }, []);
  return isOnline;
}
```

호출처: `const isOnline = useOnlineStatus();` — 끝

---

<!-- beat: b5 -->

## 잠깐, 직접 답해보세요

- Q1. `useCounter()`를 두 컴포넌트에서 호출했더니 카운트가 따로 셈. 왜?
  → 호출마다 독립 state. 공유하려면 부모에서 한 번 호출 후 props로
- Q2. `useSorted(items) { return items.slice().sort(); }` — `use` OK?
  → ❌ Hook 호출 없음. `sortItems`로 이름 변경

---

<!-- beat: b6 -->

## 오늘의 3줄

- **use 접두사** = "Hook을 호출한다"는 신호. 호출 안 하면 일반 함수
- Custom Hook은 **stateful 로직**을 공유, **state 자체는 공유 X**
- state 공유가 필요하면 **lifting/Context** — Hook 추출과는 다른 도구
