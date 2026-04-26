---
marp: true
theme: default
paginate: true
footer: "LO-S5.4"
style: |
  section { font-size: 27px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 21px; }
  table { font-size: 23px; }
---

<!-- beat: b1 -->

# useState vs useReducer

## 트레이드오프와 Immer 옵션

S5.C4 · 8분

---

<!-- beat: b1 -->

## 모든 useState를 갈아엎어야 하나?

- 답: **아니다**
- 핸들러 4개+ Tasks 앱은 이득, 토글 하나는 useState로 충분
- 오늘 두 가지: **언제 갈아탈지 판단 기준** + **Immer 옵션**

---

<!-- beat: b2 -->
<!-- _footer: "LO-S5.4" -->

## 비교 4축

| 축 | useState | useReducer |
|---|---|---|
| 코드량 | **적음** | reducer + action 보일러플레이트 |
| 가독성 | 단순 갱신에 직관적 | **복잡 다중 핸들러에 우월** |
| 디버깅 | setter 호출 추적 어려움 | **reducer에 `console.log` 한 줄로 모든 전이** |
| 테스트 | 컴포넌트 마운트 필요 | **순수 함수 단위 테스트** |

---

<!-- beat: b3 -->
<!-- _footer: "LO-S5.4" -->

## 갈아타기 결정 기준

- 핵심 질문: **여러 핸들러가 같은 state를 다양하게 갱신하는가?**
- yes → useReducer · no → useState (토글·카운터·입력 한 칸)
- 한 컴포넌트 안 **혼용 OK**:

```js
function TaskApp() {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  // ...
}
```

- 신호: setState 3개+ & 핸들러 간 갱신 로직 중복

---

<!-- beat: b4 -->
<!-- _footer: "LO-S5.5" -->

## Immer — mutation 스타일 단축 표기

```js
// 일반 reducer
case 'changed':
  return tasks.map(t => t.id === action.task.id ? action.task : t);

// useImmerReducer — draft를 Proxy로 감싼다
case 'changed': {
  const i = draft.findIndex(t => t.id === action.task.id);
  draft[i] = action.task;
  break;
}
```

- 내부: draft 변경 기록 → immutable 복사본 반환
- 일반 reducer와 **의미상 동등**

---

<!-- beat: b4 -->
<!-- _footer: "LO-S5.5" -->

## Immer 트레이드오프

- **장점**: 깊게 중첩된 객체 갱신이 짧음, 배열 spread 연쇄가 사라짐
- **단점**: 추가 의존성 · Proxy 디버깅 한 겹 · "mutation 같지만 사실은 아님" 팀 합의
- 단순 배열/객체면 일반 reducer로 충분
- 깊은 중첩이면 Immer가 코드량을 절약

---

<!-- beat: b5 -->
<!-- _footer: "LO-S5.4 / LO-S5.5" -->

## 잠깐, 후보 컴포넌트 떠올리기

- 내 프로젝트에서 reducer 후보는? — setState 3개+ & 갱신 로직 중복
- 후보를 골랐다면 일반 reducer vs Immer도 함께 결정
- 단순 배열/객체 → 일반 reducer
- 깊은 중첩 → Immer로 코드량 절약

---

<!-- beat: b6 -->
<!-- _footer: "LO-S5.4 / LO-S5.5" -->

## Section 5 정리

- **4축**(코드량·가독성·디버깅·테스트)으로 비교, 다중 핸들러면 useReducer
- 한 컴포넌트 안 **혼용 OK**, 단순 state는 useState 유지
- **Immer**는 mutation 스타일 단축 표기, 일반 reducer와 의미 동등
- 다음 섹션 → **Context로 reducer를 트리에 뿌리는 패턴**
