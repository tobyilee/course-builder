---
marp: true
theme: default
paginate: true
footer: "LO-S5.3"
style: |
  section { font-size: 27px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 21px; }
  table { font-size: 23px; }
---

<!-- beat: b1 -->

# Action 컨벤션과 Reducer 순수성

## 결함 진단 모드

S5.C3 · 12분

---

<!-- beat: b1 -->

## 한 달 뒤의 Tasks 앱

- 동료가 `'taskAdd'`, `'UPDATE_TASK'`, `'remove'` 식 어휘를 추가
- reducer 안에서 `fetch` 호출과 `tasks.push(...)` mutation 발견
- "좋은 reducer"를 가르는 두 축: **action 컨벤션** + **순수성**
- 오늘은 결함이 박힌 코드를 진단하며 두 축을 내재화한다

---

<!-- beat: b2 -->

## 축 1 — Action 어휘 컨벤션

- `action.type`은 **발생한 사건**을 묘사하는 **동사 과거형**
- 좋음: `'added'`, `'changed'`, `'deleted'`, `'reset_form'`
- 나쁨: `'SET_TASKS'`, `'UPDATE'`, `'handle_x'` — 구현 누설/명령형
- 팀 내 케이싱 통일 (snake_case **또는** camelCase 한 가지)
- 이 어휘가 곧 **앱의 인터랙션 사전**이 된다

---

<!-- beat: b3 -->

## 축 1 — 한 상호작용 = 한 action

```js
// 안티패턴 — 폼 리셋을 필드별로 흩뿌리기
dispatch({ type: 'set_field', field: 'name',  value: '' });
dispatch({ type: 'set_field', field: 'email', value: '' });
dispatch({ type: 'set_field', field: 'phone', value: '' });

// 권장 — 의미 단위 한 번
dispatch({ type: 'reset_form' });
```

- 디버그 로그가 의미 단위로 깔끔
- reducer가 한 번만 돌아 **중간 상태 노출 없음**

---

<!-- beat: b4 -->

## 축 2 — Reducer 순수성 3대 규칙

- **(1) 결정성**: 같은 입력 → 같은 출력
  - `Math.random()`, `Date.now()` 호출 금지
- **(2) 무부수효과**: `fetch`, `setTimeout`, 외부 시스템 호출 금지
  - 부수효과는 핸들러나 `useEffect`로 옮긴다
- **(3) 불변**: `state.push`, `state.x = ...` 금지 — 항상 새 배열/객체 반환
- 이유: React가 같은 state로 두 번 호출해도 결과 동일 → StrictMode·동시성 안전

---

<!-- beat: b5 -->

## 결함 진단 — Tasks reducer 변형

```js
case 'addTask':                          // 4. camelCase, 다른 case는 'added'
  tasks.push({                           // 1. mutation
    id: Date.now(),                      // 3. 비결정 (Date.now)
    text: action.text
  });
  fetch('/api/log', { method: 'POST' }); // 2. 부수효과
  return tasks;
```

빨간 마커 4개 — 어느 규칙 위반인지 라벨링하자

---

<!-- beat: b5 -->

## 수정안

```js
case 'added':
  return [
    ...tasks,
    { id: action.id, text: action.text, done: false }
  ];
```

- `id`는 **핸들러**에서 `nextId++`로 만들어 action에 실어 보낸다
- `fetch` 로깅은 `useEffect`로 — reducer 밖에서
- type 케이싱은 다른 case들과 통일 (`'added'`)

---

<!-- beat: b6 -->

## 셀프 체크리스트

- 내 reducer가 외부 변수를 읽는 줄이 있는가? (시각·랜덤·localStorage)
- 있으면 → **핸들러로 옮겨** dispatch 직전에 계산하고 action에 실어라
- `action.type` 목록이 **동사 과거형**으로 일관되는가?
- 명사형(`'task'`)·구현형(`'SET_'`)이 보이면 후보 교체

---

<!-- beat: b7 -->

## 정리

- **Action**: 동사 과거형 · 한 상호작용 = 한 action · 케이싱 일관
- **순수성**: 결정적 · 무부수효과 · 불변 — 셋 다 지켜야 진짜 reducer
- 다음 시간: useState vs useReducer 트레이드오프 + Immer 옵션
