# Source: Passing Data Deeply with Context

## 문제: prop drilling
같은 prop을 중간 컴포넌트들 사이로 단지 전달만 하기 위해 줄줄이 props로 내려보내는 패턴. 깊은 트리에서 매우 번거롭다.

## 3단계 패턴

### 1. Context 생성
```js
// LevelContext.js
import { createContext } from 'react';
export const LevelContext = createContext(1); // 기본값
```

### 2. Consumer — useContext로 읽기
```js
import { useContext } from 'react';
import { LevelContext } from './LevelContext.js';

function Heading({ children }) {
  const level = useContext(LevelContext);
  switch (level) {
    case 1: return <h1>{children}</h1>;
    case 2: return <h2>{children}</h2>;
    // ...
  }
}
```
- `useContext`는 훅이라 컴포넌트 최상단에서만 호출 (조건/루프 안 X)
- 어떤 깊이의 자손이든 읽을 수 있음

### 3. Provider — 값 공급
```js
function Section({ level, children }) {
  return (
    <section>
      <LevelContext value={level}>
        {children}
      </LevelContext>
    </section>
  );
}
```

## 같은 컴포넌트가 consume + provide
```js
function Section({ children }) {
  const level = useContext(LevelContext);
  return (
    <section>
      <LevelContext value={level + 1}>
        {children}
      </LevelContext>
    </section>
  );
}
// <Section><Section><Section><Heading>... 자동 level 증가
```

## 특성
- 중간 컴포넌트는 context를 모르고도 통과
- 가장 가까운 Provider의 값을 읽음
- 여러 context는 서로 독립

## Context 쓰기 전 대안 검토

### 1. Props 명시 전달
```js
<Layout posts={posts} user={user} theme={theme} />
```
데이터 흐름이 명시적이라 리팩터링·유지보수 좋음.

### 2. children/JSX 전달 (composition)
```js
// 대신
<Layout posts={posts} />
// 이렇게
<Layout><Posts posts={posts} /></Layout>
```
중간 컴포넌트 수를 줄이고, props가 흐를 거리를 짧게.

## Context 적합한 사례
✅ **Theming** — 다크모드/색상 스킴
✅ **Authentication** — 현재 로그인 사용자
✅ **Routing** — 현재 라우트 (대부분 라우터 라이브러리가 내부적으로 사용)
✅ **복잡한 분산 state** — useReducer + context 조합
✅ **글로벌 설정** — 앱 전반 옵션

## ⚠️ 안 쓰는 게 좋은 사례
- 1~2 레벨만 내려가는 단순 prop
- 가까운 컴포넌트끼리만 쓰는 데이터
- composition으로 해결 가능한 경우

## Recap
- `createContext(default)` → context 객체
- `useContext(MyCtx)` → 값 읽기
- `<MyCtx value=…>` → Provider
- 가장 가까운 Provider 값을 사용 (없으면 default)
- 깊은 트리, 다수 분산 컴포넌트 = context 적합
- 단순 prop 전달엔 props/composition 우선
