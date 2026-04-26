---
marp: true
theme: default
paginate: true
footer: "LO-S1.1"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  table { font-size: 22px; }
  th, td { padding: 6px 10px; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
---

<!-- beat: b1 -->

# Visual states 열거하기

### 디자이너처럼 UI를 펼쳐보기

S1.C1 · 12분 · LO-S1.1

---

<!-- beat: b1 -->

## 명령형 vs 선언형, 어디가 아픈가

<div class="two-col">

**명령형 (운전자에게 좌·우 지시)**

```js
button.disabled = true;
spinner.show();
error.hide();
// 분기 추가 시 모두 손봐야 함
```

**선언형 (택시에 목적지만)**

- 가능한 상태를 먼저 그린다
- 각 상태의 UI를 기술한다
- React가 알아서 그린다

</div>

새 visual state 하나가 if-else 폭발을 부른다 — 오늘은 그 사슬을 끊는다.

---

<!-- beat: b2 -->

## 선언형 5단계 — 오늘은 ①②

1. **상태 열거** — 보여줄 모든 모습
2. **트리거 식별** — 누가 바꾸나
3. useState 모델링 (C2)
4. 비핵심 state 제거 (C2)
5. 핸들러 연결 (C3)

> 코드 한 줄도 짜기 전에 **디자이너 모드**로 종이에 펼친다.
> 빠진 상태(예: empty)가 그 순간 드러난다.

---

<!-- beat: b2 -->

## 트리거는 둘 — human vs computer

| 종류 | 누가 발화 | 예시 |
|---|---|---|
| **human** | 사용자 | 타이핑·클릭·hover |
| **computer** | 시스템 | 네트워크 응답·타이머 |

- 종류를 구분해야 **누가 setState를 호출할지** 명확해진다
- human → 이벤트 핸들러
- computer → 비동기 콜백 / effect 결과

---

<!-- beat: b3 -->

## 도시 퀴즈 폼의 5개 visual state

> "What city is on two continents?"

| 상태 | 화면 |
|---|---|
| **empty** | 빈 입력칸, 버튼 disabled |
| **typing** | 입력 중, 버튼 활성 |
| **submitting** | spinner, 입력 잠김 |
| **success** | "정답!" 메시지 |
| **error** | "오답" + 입력 가능 |

5개를 동시 배치 → 곧 **living styleguide** 의 출발점.

---

<!-- beat: b3 -->

## 트리거 매트릭스 — 표가 곧 설계도

| 전이 | 트리거 | 종류 |
|---|---|---|
| empty ↔ typing | 텍스트 입력 | human |
| typing → submitting | Submit 클릭 | human |
| submitting → success | 네트워크 성공 | computer |
| submitting → error | 네트워크 실패 | computer |

표를 그려두면, C3의 핸들러 작성은 **표를 코드로 옮기는 작업**이 된다.

---

<!-- beat: b4 -->

## Practice — 익숙한 위젯 한 개

택1: 좋아요 버튼 / 팔로우 버튼 / 파일 업로드 버튼

**체크리스트**

- visual state ≥ 3개 (empty/disabled 포함했나?)
- 각 전이에 human·computer 라벨
- 종이/메모장에 직접 작성

힌트(좋아요): idle / hover / liked / loading / error

---

<!-- beat: b5 -->

## Recap — 오늘 손에 쥔 두 산출물

1. **visual state 목록** — 디자이너 모드로 모두 펼쳐 그린다
2. **트리거 표** — 각 전이에 human / computer 라벨
3. 이 둘이 다음 class에서 그대로 **useState 코드**로 옮겨진다

> 다음(C2): 7개 boolean의 함정 → status enum 리팩터링
