---
marp: true
theme: default
paginate: true
footer: "LO-S4.1 · LO-S4.2"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  pre { font-size: 22px; }
---

<!-- beat: b1 -->

# state는 트리 위치에 묶인다

보존과 리셋의 기본 규칙

S4 · Class 1

---

<!-- beat: b1 -->
<!-- _footer: "LO-S4.1" -->

## 토글했는데 score가 살아있다?

- `isFancy` 한 번 눌렀을 뿐인데 카운터 점수가 그대로
- props가 바뀌었는데도 state가 살아남는 현상
- "state는 컴포넌트 안에 산다"는 직관, 정말일까?
- 오늘 그 직관을 바로잡는 단 두 개의 규칙을 본다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S4.1" -->

## React가 추적하는 건 '위치'다

- React는 컴포넌트 인스턴스가 아니라 **렌더 트리의 슬롯**을 추적
- JSX `<Counter />` = "이 위치에 Counter 타입이 있다"는 명세
- 리렌더 후에도 같은 위치 + 같은 타입이면 같은 state를 그대로 붙임
- 같은 변수를 두 번 써도 트리상 두 슬롯 → state도 두 개

```jsx
// 같은 코드지만 트리에서는 서로 다른 두 슬롯
<div>
  <Counter />
  <Counter />
</div>
```

---

<!-- beat: b3 -->
<!-- _footer: "LO-S4.1" -->

## 두 가지 규칙으로 끝난다

- 규칙 1 — 같은 위치 + 같은 타입 = **state 보존** (props가 달라져도)
- 규칙 2 — 같은 위치 + 다른 타입 = **state 파괴 후 재생성**
- 타입이 바뀌면 자식 트리까지 통째로 unmount
- 이 두 줄만 외워도 보존/리셋의 90%를 예측할 수 있다

---

<!-- beat: b4 -->
<!-- _footer: "LO-S4.2" -->

## 예제 1 — props만 갈아끼우기

```jsx
{isFancy
  ? <Counter isFancy={true} />
  : <Counter isFancy={false} />}
```

- 두 분기 모두 **같은 위치 + 같은 Counter 타입**
- 토글해도 score는 살아남는다 — 시각만 바뀌고 정체성은 유지
- "props 변화 = state 리셋" 같은 흔한 오해를 한 줄로 깨뜨림

---

<!-- beat: b5 -->
<!-- _footer: "LO-S4.2" -->

## 예제 2 — 타입이 바뀌면 사라진다

```jsx
{isPaused
  ? <p>See you later</p>
  : <Counter />}
```

- 같은 위치인데 한쪽은 `<p>`, 한쪽은 `<Counter />`
- 토글하는 순간 Counter는 unmount, score state도 함께 폐기
- 다시 켜도 score는 0부터 시작 — 새 컴포넌트, 새 state

---

<!-- beat: b6 -->
<!-- _footer: "LO-S4.2" -->

## 잠깐 퀴즈 — 결과를 예측해 보자

```jsx
// Before                    // After
<section><Counter/></section>  <div><Counter/></div>
```

- 부모 태그 `section` → `div`로 바꾸면 score는?
- 힌트 — 부모가 다르면 트리 구조 자체가 달라진다
- 정답: **리셋**. 다른 타입이라 하위 트리 전체가 새로 만들어짐
- 습관 만들기 — "같은 위치인가? 같은 타입인가?" 두 질문

---

<!-- beat: b7 -->
<!-- _footer: "LO-S4.1 · LO-S4.2" -->

## 정리 — 위치와 타입, 두 단어로 충분

- state는 컴포넌트 인스턴스가 아니라 **트리 위치**에 묶인다
- 같은 위치 + 같은 타입 = 보존 / 타입이 다르면 = 리셋
- 다음 class에서는 일부러 리셋하고 싶을 때 쓰는 두 전략을 본다
