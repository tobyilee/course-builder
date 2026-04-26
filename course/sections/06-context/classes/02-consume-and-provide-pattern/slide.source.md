---
marp: true
theme: default
paginate: true
footer: "LO-S6.3"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# Consume + Provide

## Section 깊이가 곧 level이 되는 패턴

S6.C2 · 13분

---

<!-- beat: b1 -->
<!-- _footer: "LO-S6.3" -->

## level을 손으로 적는 통증

- 지난 시간 — `<Section level={1}>` 매번 명시
- 중첩이 깊어질수록 사람이 카운트 → 실수
- `<Section level={1}><Section level={2}>...` 끝없이
- **목표**: level prop을 완전히 제거한다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S6.3" -->

## 핵심 아이디어

- Section이 LevelContext를 `useContext`로 **읽고**
- `+1` 한 값을 다시 Provider로 **공급**
- consume(읽기) + provide(공급)가 한 컴포넌트 안에 동시에
- `useContext`가 보는 값은 **나를 감싼 가장 가까운 Provider**
- 내가 만든 Provider는 내 **자식**이 본다

---

<!-- beat: b3 -->
<!-- _footer: "LO-S6.3" -->

## Section 리팩터

```js
export function Section({ children }) {
  const level = useContext(LevelContext); // consume
  return (
    <section>
      <LevelContext value={level + 1}>   {/* provide */}
        {children}
      </LevelContext>
    </section>
  );
}
```

`createContext(0)` → 첫 Section은 0을 읽고 **1**을 공급 → 첫 Heading은 **h1**

---

<!-- beat: b3 -->
<!-- _footer: "LO-S6.3" -->

## 자동 h1 → h2 → h3

```jsx
<Section>
  <Heading>Title</Heading>      {/* h1 */}
  <Section>
    <Heading>Sub</Heading>       {/* h2 */}
    <Section>
      <Heading>SubSub</Heading>  {/* h3 */}
    </Section>
  </Section>
</Section>
```

Heading 코드는 **한 줄도 안 바뀜** — context의 캡슐화 효과

---

<!-- beat: b4 -->
<!-- _footer: "LO-S6.3" -->

## 가장 가까운 Provider 규칙

- 자손이 `useContext` 호출 → 위로 올라가며 첫 Provider에서 멈춤
- 여러 context는 서로 **독립** — Theme/Level 공존해도 간섭 없음
- 각 context마다 자기만의 Provider chain
- 값이 바뀌면 그 context를 읽는 컴포넌트만 재렌더
- 주의 — 매 렌더 새 객체를 value로 넘기면 모든 consumer 리렌더

---

<!-- beat: b5 -->
<!-- _footer: "LO-S6.3" -->

## 잠깐, 답해보기

- `<Section><Heading>A</Heading><Section><Heading>B</Heading></Section></Section>` → A, B는?
- `createContext(0)` 대신 `createContext(1)`로 바꾸면?
- 중간에 `<div>`를 끼우면 카운트가 끊길까, 유지될까?

머릿속 트리에 level 라벨링을 직접 해보자

---

<!-- beat: b6 -->
<!-- _footer: "LO-S6.3" -->

## 정리

- **Consume + Provide** — 같은 컴포넌트가 읽고, 변형해서 다시 공급
- **가장 가까운 Provider 규칙** — Section 깊이 = level
- 다음 class — context는 강력하지만 **남용 금지**, props·composition을 먼저 보자
