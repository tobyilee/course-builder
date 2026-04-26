---
marp: true
theme: default
paginate: true
footer: "LO-S0.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  .small { font-size: 22px; color: #555; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# 코스 맵

## 7개 챕터가 어떤 통증을 푸는가

<span class="small">앞 class의 4가지 통증을 한 장의 지도로 정렬한다</span>

---

<!-- beat: b1 -->
<!-- _footer: "LO-S0.1" -->

## 한 장의 지도로 보기

- 앞 class에서 본 **4가지 통증**을 머릿속에 두고 출발
- 오늘의 약속: 7개 챕터를 통증과 **1:1로 매핑**한다
- 학습자가 자기 코드 한 줄을 어느 챕터에 걸어볼지 결정한다
- 이 지도는 강의 내내 "지금 어디에 있는지" 다시 펴볼 **북극성**

---

<!-- beat: b2 -->
<!-- _footer: "LO-S0.1" -->

## 구조 잡기 — S1·S2·S3

| 챕터 | 푸는 통증 | 핵심 도구 |
|---|---|---|
| **S1** 선언형 사고 | #1 중복 · #2 동기화 뿌리 | visual states 5단계 |
| **S2** state 구조 설계 | #1 중복 · #2 동기화 차단 | 5원칙(묶기·모순회피·평탄화…) |
| **S3** lifting state up | #3 drilling 1차 처방 | 공통 부모 + single source |

state를 **어디에 어떤 모양으로 둘지** 결정하는 영역

---

<!-- beat: b3 -->
<!-- _footer: "LO-S0.1" -->

## 동작 다듬기 — S4·S5·S6·S7

| 챕터 | 푸는 통증 | 핵심 도구 |
|---|---|---|
| **S4** 보존과 리셋 | #4 의도치 않은 리셋 | 트리 위치 + key prop |
| **S5** reducer | setState 흩어짐 | (state, action) → next |
| **S6** context | #3 drilling 2차 처방 | createContext / Provider |
| **S7** reducer + context | 분산 state 확장 | state/dispatch 분리 |

구조가 잡힌 뒤 **리셋·로직·전달 방식**을 정교화

---

<!-- beat: b4 -->
<!-- _footer: "LO-S0.2" -->

## 통증 → 챕터 실제 매핑

- "체크박스 7개를 boolean으로 들고 있다가 모순 상태가 만들어진다"
  → **S1·S2** (status enum + 5원칙)
- "같은 폼인데 탭만 바꾸면 입력이 그대로 남아 있다"
  → **S4** (key prop으로 리셋)
- 모든 통증에는 **풀리는 챕터가 정해져 있다**

---

<!-- beat: b5 -->
<!-- _footer: "LO-S0.2" -->

## Self-diagnosis — 가설을 들고 입장하기

- ① 최근 프로젝트의 state 버그/스멜 **1개**를 떠올린다
- ② 4가지 통증 중 어디에 가까운가? — 한 단어로 라벨링
- ③ 코스 맵에서 **"이건 S?에서 풀릴 것 같다"** 가설을 세운다
- 정답 검증은 강의 진행하며 자연스럽게 — 지금은 가설만!

---

<!-- beat: b6 -->
<!-- _footer: "LO-S0.1" -->

## 오리엔테이션 정리

- ① **S1·S2·S3 = 구조 잡기**, **S4~S7 = 동작 다듬기** 두 묶음으로 기억
- ② 4가지 통증은 7개 챕터 어딘가에서 **반드시** 풀린다 — 우연으로 두지 않는다
- ③ 다음 섹션부터는 **가설을 들고 입장** — 내 코드 어느 줄이 어느 챕터에 걸리는지 추적
- 자, 이제 S1 선언형 사고로 출발합니다
