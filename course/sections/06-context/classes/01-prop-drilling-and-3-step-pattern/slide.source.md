---
marp: true
theme: default
paginate: true
footer: "LO-S6.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# Prop Drilling을 멈추는 3단계

## createContext / Provider / useContext

S6.C1 · 14분

---

<!-- beat: b1 -->
<!-- _footer: "LO-S6.1" -->

## 5단 트리의 통증

- App → Page → Layout → Sidebar → UserBadge
- `currentUser`는 UserBadge만 쓰는데 4개를 통과
- 다크모드 추가 = 같은 4개를 또 수정
- 중간 컴포넌트 시그니처가 점점 더러워진다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S6.1" -->

## Prop Drilling vs Context

- **Prop drilling** — 통과만 하려고 prop을 받는 패턴
- props는 위→아래 **직렬 흐름**
- context는 Provider→자손으로 **점프**
- 중간 컴포넌트는 context를 몰라도 통과
- 비유: '컴포넌트 트리에 직접 꽂는 백채널'

---

<!-- beat: b3 -->
<!-- _footer: "LO-S6.2" -->

## 3단계 패턴

```js
// 1. 생성 — Provider 없을 때 fallback
const LevelContext = createContext(1);

// 2. 공급 — 매 렌더 새 값 가능
<LevelContext value={level}>{children}</LevelContext>

// 3. 소비 — 가장 가까운 Provider 값
const level = useContext(LevelContext);
```

`useContext`는 훅 — 최상단 호출, 조건/루프 안 금지

---

<!-- beat: b4 -->
<!-- _footer: "LO-S6.2" -->

## Heading 예제 — context 버전

```js
// LevelContext.js
export const LevelContext = createContext(1);

// Heading.js
export function Heading({ children }) {
  const level = useContext(LevelContext);
  switch (level) {
    case 1: return <h1>{children}</h1>;
    case 2: return <h2>{children}</h2>;
    case 3: return <h3>{children}</h3>;
    default: return <h4>{children}</h4>;
  }
}
```

---

<!-- beat: b4 -->
<!-- _footer: "LO-S6.2" -->

## Section이 값을 공급한다

```js
export function Section({ level, children }) {
  return (
    <section>
      <LevelContext value={level}>
        {children}
      </LevelContext>
    </section>
  );
}

// 사용
<Section level={1}>
  <Heading>Title</Heading>   {/* level prop 없음! */}
</Section>
```

---

<!-- beat: b5 -->
<!-- _footer: "LO-S6.2" -->

## 잠깐, 답해보기

- Provider 없이 `useContext(LevelContext)`를 부르면? → **default**
- `<LevelContext value={2}>` 안에 `<LevelContext value={4}>` 중첩하면 안쪽 Heading은? → **h4**
- 왜 `createContext(1)`처럼 의미 있는 default가 좋을까?

답은 다음 class에서 자연스럽게 드러난다

---

<!-- beat: b6 -->
<!-- _footer: "LO-S6.1" -->

## 정리

- **Prop drilling** — 깊은 트리일수록 통증이 커진다
- **3단계** — `createContext(default)` → `<Ctx value=…>` → `useContext(Ctx)`
- 다음 class — 같은 컴포넌트가 **consume + provide** 하면 level이 자동 증가한다
