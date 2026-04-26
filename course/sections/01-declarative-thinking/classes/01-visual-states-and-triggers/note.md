# visual states 열거하기 — 디자이너처럼 UI를 펼쳐보기

> LOs: LO-S1.1

## 개요

코드를 한 줄도 짜기 전에, 잠깐 디자이너 모드로 전환해 봅시다. 명령형으로 폼을 만들면 `button.disabled = true`, `spinner.show()`, `error.hide()` 같은 지시가 분기마다 흩어져, visual state 하나만 추가해도 모든 if-else를 다시 손봐야 합니다 [slide 2]. 운전자에게 좌회전·우회전을 일일이 알려주는 운전과, 택시에 목적지만 말하는 탑승의 차이라고 보면 직관적입니다. 이 class는 선언형 5단계 중 ①상태 열거와 ②트리거 식별을 다룹니다 — useState는 다음 class [S1.C2]의 몫입니다.

## 핵심 개념

**visual state**는 같은 컴포넌트가 보여줄 수 있는 서로 다른 모습입니다. 도시 퀴즈 폼이라면 `empty / typing / submitting / success / error` 다섯 가지를 모두 종이에 펼쳐 그리는 것이 출발점이죠 [slide 3]. 디자이너처럼 모든 모습을 동시에 그리면, 빠뜨리기 쉬운 `empty`나 `error` 같은 상태가 자연스럽게 드러납니다.

다음으로 각 전이를 일으키는 **트리거**를 둘로 나눕니다.

- **human 트리거** — 타이핑, 클릭, hover처럼 사용자가 직접 일으키는 입력
- **computer 트리거** — 네트워크 응답, 타이머, 외부 이벤트처럼 시스템이 일으키는 입력

이 구분이 중요한 이유는, 누가 setState를 호출할지가 명확해지기 때문입니다. human은 onChange/onClick 안에서, computer는 비동기 then/catch 안에서 호출하게 됩니다 [S1.C3].

## 예시

도시 퀴즈 폼: "What city is on two continents?" 한 줄짜리 폼입니다. 다섯 visual state를 한 페이지에 동시에 mockup으로 늘어놓는 것이 곧 *living styleguide* 패턴의 씨앗입니다 [slide 4].

상태 전이를 표로 정리하면 이렇게 됩니다.

| 전이 | 트리거 | 종류 |
|---|---|---|
| empty ↔ typing | 텍스트 입력 | human |
| typing → submitting | Submit 클릭 | human |
| submitting → success | 네트워크 성공 | computer |
| submitting → error | 네트워크 실패 | computer |

이 표가 다음 class의 setState 호출 위치를 그대로 결정합니다. 표를 그려두면 핸들러 작성은 "표를 코드로 옮기는 작업"이 되어 사고 부담이 확 줄어듭니다.

## 흔한 실수

- **상태를 머릿속으로만 떠올리기** — 그리지 않으면 `empty`나 `disabled` 같은 평범한 상태를 빠뜨립니다. 종이에 mockup을 다 그려야 빈 칸이 보입니다.
- **트리거 종류를 섞기** — "hover하면 fetch가 일어난다"처럼 human과 computer가 한 화살표에 묶이면, 핸들러 안에 어디서 setState를 호출할지 흐려집니다. 화살표를 두 단계(hover→loading, fetch완료→ready)로 분리하세요.
- **상호배타 가정 누락** — typing과 success가 동시에 가능한 표를 그리는 순간, 다음 class에서 만나게 될 boolean paradox 함정이 시작됩니다 [S1.C2].

## 복습

1. 코드 전에 visual state를 모두 그리세요 — 디자이너 모드.
2. 각 전이 옆에 human/computer 라벨을 붙이세요.
3. 이 두 산출물이 다음 class의 useState 모델링 재료가 됩니다. 다음은 7개 boolean의 함정과 status enum 리팩터링입니다.
