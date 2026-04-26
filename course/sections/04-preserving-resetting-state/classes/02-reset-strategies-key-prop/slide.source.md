---
marp: true
theme: default
paginate: true
footer: "LO-S4.3"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 22px; }
---

<!-- beat: b1 -->

# 의도된 리셋

다른 위치 vs key prop, 두 전략

S4 · Class 2

---

<!-- beat: b1 -->

## 스코어보드 버그 — Sarah가 10점?

- Taylor 점수 10 → **Next player** 클릭
- Sarah로 전환했는데 점수 10이 그대로 남아 있다
- 지난 시간 규칙(같은 위치+같은 타입=보존)이 이번엔 발목을 잡는다
- 의도적으로 리셋하려면 어떻게 하지?

---

<!-- beat: b2 -->

## 전략 1 — 다른 위치로 렌더하기

```jsx
{isPlayerA && <Counter person="Taylor" />}
{!isPlayerA && <Counter person="Sarah" />}
```

- 분기 두 개를 만들어 트리상 **서로 다른 슬롯**에 배치
- 한 시점엔 하나만 마운트되지만 위치 자체가 다르므로 state도 분리
- 한계 — 분기가 미리 정해진(A/B 같은 이산적) 경우에만 깔끔하다

---

<!-- beat: b3 -->

## 전략 2 — `key` prop으로 정체성 부여

- 같은 위치라도 `key`가 바뀌면 React는 **다른 컴포넌트**로 본다
- `<Counter key="Taylor" />` 와 `<Counter key="Sarah" />` = 다른 정체성
- key가 바뀌면 이전 state는 폐기되고 새로 처음부터 시작
- key는 **같은 부모 안에서만** 유일하면 됨 (글로벌 유일 X)
- 리스트의 key와 같은 메커니즘 — 의도는 "명시적 리셋"

---

<!-- beat: b4 -->

## 스코어보드 리팩터링 — 한 줄이면 끝

```jsx
// Before — 분기 두 개
{isPlayerA && <Counter person="Taylor" />}
{!isPlayerA && <Counter person="Sarah" />}

// After — key 한 줄
<Counter
  key={isPlayerA ? 'Taylor' : 'Sarah'}
  person={isPlayerA ? 'Taylor' : 'Sarah'}
/>
```

- Next 버튼 → key 바뀜 → score 자동으로 0
- 결과는 같지만 코드가 "**state를 리셋하라**"고 직접 말한다

---

<!-- beat: b5 -->

## 실전 — 채팅 폼이 안 비워지는 버그

```jsx
// 연락처를 바꿔도 입력 중이던 메시지가 그대로 남는다
<Chat contact={to} />

// 한 줄 추가로 to.id별 독립된 입력창이 된다
<Chat key={to.id} contact={to} />
```

- 원인 — 같은 위치 + 같은 Chat 타입이라 textarea state 보존
- 해법 — `key={to.id}`로 to 바뀔 때마다 폼이 새로 마운트
- key가 "연락처별 독립 입력창"이라는 도메인 의미를 표현

---

<!-- beat: b6 -->

## 미니 연습 — 탭 폼 리셋

- 탭 UI에서 탭을 바꿀 때마다 폼 입력을 초기화하려면?
- 정답 — `<Form key={activeTabId} />`
- 추가 질문 — 두 전략 중 어느 쪽이 더 적절한가?
- 선택 기준 — 분기가 미리 정해졌나(전략 1) vs 동적 정체성인가(전략 2)

---

<!-- beat: b7 -->

## 정리 — 리셋의 두 도구

- 의도된 리셋 = **다른 위치로 렌더** 또는 **다른 key 부여**
- key는 같은 부모 안에서만 유일하면 충분
- 다음 class — 트리 위치 모델의 두 함정을 본다
