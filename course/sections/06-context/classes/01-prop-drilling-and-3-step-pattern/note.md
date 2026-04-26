# prop drilling 문제와 createContext / Provider / useContext 3단계

> LOs: LO-S6.1, LO-S6.2

## 개요
`App → Page → Layout → Sidebar → UserBadge` 같은 5단 트리에서 `currentUser`는 사실 가장 안쪽 `UserBadge`만 쓰는데, 중간 4개 컴포넌트가 그저 props를 통과시키느라 시그니처가 더러워집니다 [slide 2]. 다크모드를 추가하면 같은 4개를 또 수정해야 하죠. 이 통증의 이름이 **prop drilling**입니다. 이 class에서는 그 통증의 정체를 정의하고, 해소 도구인 `createContext` / `<Provider value=…>` / `useContext` 3단계 패턴을 [S3.C1]에서 배운 lifting과 다른 각도에서 만나봅니다.

## 핵심 개념
**prop drilling**은 중간 컴포넌트가 단지 통과시키기 위해 prop을 받는 패턴입니다. 데이터 흐름이 위에서 아래로 직렬이라 깊이가 깊어질수록 비용이 곱셈으로 늘어납니다. **context**는 이를 해결하기 위해 React가 제공하는 "트리에 직접 꽂는 백채널"입니다 — Provider가 값을 공급하면 임의의 자손이 점프해서 읽어갑니다 [slide 3].

3단계는 단순합니다 [slide 4]:

1. **`createContext(defaultValue)`** — context 객체를 생성합니다. 인자는 Provider가 위에 없을 때 fallback으로 반환되는 의미 있는 기본값이어야 합니다.
2. **`<MyContext value={...}>`** — Provider로 자손에게 값을 공급합니다. 매 렌더 새 값을 줄 수 있습니다 (React 19+ 단축 문법).
3. **`useContext(MyContext)`** — 자손이 가장 가까운 Provider 값을 읽어옵니다. 훅이므로 컴포넌트 최상단에서만, 조건/루프 밖에서 호출해야 합니다.

핵심 효과는 **중간 컴포넌트가 context의 존재조차 몰라도 통과**한다는 점입니다. props 시그니처가 깨끗해지고, 새 데이터를 추가할 때 중간 컴포넌트를 건드릴 필요가 사라집니다.

## 예시
react.dev 원전과 동일한 `Heading + Section` 예제로 props 버전과 context 버전을 나란히 봅니다 [slide 5].

```js
// LevelContext.js
import { createContext } from 'react';
export const LevelContext = createContext(1);

// Heading.js
import { useContext } from 'react';
import { LevelContext } from './LevelContext.js';
export function Heading({ children }) {
  const level = useContext(LevelContext);
  switch (level) {
    case 1: return <h1>{children}</h1>;
    case 2: return <h2>{children}</h2>;
    case 3: return <h3>{children}</h3>;
    default: return <h4>{children}</h4>;
  }
}

// Section.js
export function Section({ level, children }) {
  return (
    <section>
      <LevelContext value={level}>{children}</LevelContext>
    </section>
  );
}
```

`Heading`의 시그니처에서 `level` prop이 사라진 게 보이시나요? 호출부도 `<Section level={1}><Heading>title</Heading></Section>`처럼 `Heading`에 `level`을 더는 적지 않습니다. 중간에 어떤 wrapper를 끼워도 `LevelContext`를 import할 필요가 없습니다.

## 흔한 실수
- **1~2단짜리 prop을 context로 해결**하려는 충동. 가까운 부모-자식 사이는 props가 더 명시적이고 디버깅이 쉽습니다. 결정 기준은 [S6.C3]에서 정리합니다.
- **`useContext`를 조건문이나 루프 안에서 호출**하기. 훅 규칙 위반으로 React가 호출 순서를 추적하지 못해 런타임 오류가 납니다. 항상 컴포넌트 함수 최상단에서 호출하세요.
- **`createContext()`에 의미 없는 `null`/`undefined`만 넣기**. Provider 누락 시 fallback이 사용되는데, 의미 있는 기본값을 두면 디버깅과 테스트가 훨씬 수월합니다.

## 복습
prop drilling은 깊은 트리에서 곱절로 아픕니다. `createContext(default) → <Ctx value=…> → useContext(Ctx)` 3단계로 중간 컴포넌트를 건너뛰어 데이터를 꽂아 넣으세요. 다음 [S6.C2]에서는 같은 컴포넌트가 동시에 consume + provide 하면 `level`이 어떻게 자동으로 증가하는지 봅니다.
