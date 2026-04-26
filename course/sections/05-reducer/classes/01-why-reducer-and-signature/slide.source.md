---
marp: true
theme: default
paginate: true
footer: "LO-S5.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# 왜 Reducer인가

## useReducer 시그니처와 도입 동기

S5.C1 · 10분

---

<!-- beat: b1 -->

## 흩어진 setState의 통증

- 프라하 여행 Tasks 앱 — 추가/수정/삭제/체크 핸들러 4개
- 각 핸들러마다 `setTasks(...)` 호출이 흩어져 있음
- 버그가 나면 어느 setState가 범인인지 추적이 어렵다
- 오늘 배울 useReducer는 갱신 로직을 **한 곳**으로 모은다

---

<!-- beat: b2 -->

## Reducer란 무엇인가

- **정의**: `(state, action) => nextState` 형태의 **순수 함수**
- `action`은 "무엇이 일어났는가"를 묘사하는 평범한 객체
- 예: `{ type: 'added', id: 3, text: 'Visit Charles Bridge' }`
- 컴포넌트 외부 함수 → **테스트·재사용 가능**
- 이름의 유래: `Array.prototype.reduce` — 누적기 패턴

---

<!-- beat: b3 -->

## useReducer 시그니처

```js
const [state, dispatch] = useReducer(reducer, initialState);
```

- 반환은 `[현재 state, dispatch]` 쌍 — useState와 같은 구조
- `dispatch(action)` → React가 `reducer(state, action)` 호출
- 핸들러는 이제 `dispatch({ type: 'added', ... })`만 외친다
- 라이프사이클은 useState와 동일

---

<!-- beat: b4 -->

## 같은 핸들러, 두 가지 모습

```js
// useState — '어떻게'가 핸들러 안에
function handleAddTask(text) {
  setTasks([...tasks, { id: nextId++, text, done: false }]);
}

// useReducer — '무엇이 일어났는가'만 알린다
function handleAddTask(text) {
  dispatch({ type: 'added', id: nextId++, text });
}
```

핵심: **'무엇(action)'과 '어떻게(reducer)'의 분리**

---

<!-- beat: b5 -->

## 잠깐, 안 보고 말해보기

- useReducer 시그니처: `(reducer, initialState) → ?`
- reducer 형태: `(state, action) → ?`
- reducer는 어떤 함수? — **순수 함수**
- dispatch가 하는 일은? — **action을 React에 전달**

빈칸이 떠오르면 다음 슬라이드로

---

<!-- beat: b6 -->

## 정리

- **Reducer** = `(state, action) => nextState` 순수 함수
- **useReducer**(reducer, initialState) → `[state, dispatch]`
- 다음 시간: 기존 Tasks 앱을 **3단계로 마이그레이션**
