---
marp: true
theme: default
paginate: true
footer: "LO-S5.2"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
---

<!-- beat: b1 -->

# 3단계 마이그레이션

## useState → useReducer 라이브 리팩터링

S5.C2 · 15분 · 프라하 Tasks 앱

---

<!-- beat: b2 -->

## 로드맵 미리보기

- **Step 1** (≈3분): 핸들러의 `setTasks(...)` → `dispatch({ type, ...payload })`
- **Step 2** (≈5분): `switch(action.type)` 분기하는 reducer를 컴포넌트 밖에
- **Step 3** (≈30초): `useState` 한 줄을 `useReducer`로 교체
- 순서가 중요 — Step 1이 정한 **action 어휘**를 Step 2 reducer가 분기

---

<!-- beat: b3 -->

## Step 1 — setTasks → dispatch

```js
// 4개 핸들러에서 set 호출을 dispatch로
function handleAddTask(text) {
  dispatch({ type: 'added', id: nextId++, text });
}
function handleChangeTask(task) {
  dispatch({ type: 'changed', task });
}
function handleDeleteTask(taskId) {
  dispatch({ type: 'deleted', id: taskId });
}
```

이 단계엔 reducer가 없어 코드는 잠시 깨져 있다 — **action 어휘 확정**이 목적

---

<!-- beat: b4 -->

## Step 2 — tasksReducer 작성

```js
function tasksReducer(tasks, action) {
  switch (action.type) {
    case 'added':
      return [...tasks, { id: action.id, text: action.text, done: false }];
    case 'changed':
      return tasks.map(t => t.id === action.task.id ? action.task : t);
    case 'deleted':
      return tasks.filter(t => t.id !== action.id);
    default:
      throw Error('Unknown action: ' + action.type);
  }
}
```

---

<!-- beat: b4 -->

## Step 2 — 작성 규칙

- 컴포넌트 **밖** 함수 — props/state 의존 금지, 인자만 받음
- 각 case는 **새 배열/객체** 반환 — 절대 mutate 금지
- `default`에 `throw Error(...)` — 오타 즉시 발견
- Step 1의 dispatch 어휘와 case 이름이 1:1 매칭

---

<!-- beat: b5 -->

## Step 3 — 한 줄 교체

```js
// before
import { useState } from 'react';
const [tasks, setTasks] = useState(initialTasks);

// after
import { useReducer } from 'react';
const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
```

- 나머지 컴포넌트는 그대로 — `tasks` 읽기·자식 props 전달 동일
- UI 동작이 이전과 **100% 같아야 정상** — 다르면 mutation 의심

---

<!-- beat: b6 -->

## 잠깐, 머릿속으로 Step 1만

- 여러분의 컴포넌트에서 `setState`가 3개 이상인 곳을 떠올려보자
- 각 setState 호출에 어떤 `action.type`을 붙일까? — **동사 과거형**으로
- 예: `'added'`, `'updated'`, `'removed'` — 3~5개 어휘가 나오면 OK
- 어휘가 안 잡히면 핸들러가 너무 많은 일을 한다는 신호

---

<!-- beat: b7 -->

## 정리

- **3단계**: setState→dispatch · reducer 작성 · useReducer 교체
- 기계적 변환이라 결과 동작은 동일 — 다르면 **mutation 점검**
- 다음 시간: action 어휘 짓기 + reducer 순수성 결함 진단
