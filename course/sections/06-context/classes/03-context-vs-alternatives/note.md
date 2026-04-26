# context를 쓸 때와 쓰지 말 때 — props·composition과 비교

> LOs: LO-S6.4

## 개요
context를 한 번 배우면 모든 prop을 context로 옮기고 싶어집니다. 그 결과는 **Provider 10겹 중첩**과 "이 값이 어디서 오는지 코드로 추적 불가능한" 코드베이스죠 [slide 2]. context는 강력한 도구이지만, **첫 도구가 되어선 안 됩니다**. 이 class에서는 꺼내기 전에 검토할 두 대안 — 명시적 props와 composition — 을 코드로 비교하고, context가 정당한 사례를 정리합니다.

## 핵심 개념
결정 트리는 단순합니다 [slide 3].

1. **명시적 props 전달** — 1~2단만 내려가는 데이터라면 props가 항상 우선입니다. 데이터 흐름이 코드에 그대로 보이므로 리팩터링과 디버깅이 쉽습니다. [S3.C1]에서 본 single source of truth 원칙도 자연스럽게 지켜집니다.
2. **children/JSX composition** — 중간 컴포넌트를 건너뛰어 prop이 흐를 거리 자체를 단축하는 기법입니다. `<Layout posts={posts}/>` 대신 `<Layout><Posts posts={posts}/></Layout>`로 쓰면 `Layout`은 더 이상 `posts`를 알 필요가 없습니다.
3. **그래도 멀다면 context** — 두 대안을 적용했는데도 거리가 남으면 그제서야 context 후보입니다.

결정 트리거를 한 문장으로: **"props로 흐를 거리를 짧게 만들었는데도 멀다면 context"** [slide 4].

context가 정당한 사례에는 공통 특성이 있습니다 — **(1) 많은 분산 컴포넌트**가 **(2) 깊이 무관하게** **(3) 자주 바뀌지 않는** 값을 공유한다는 점입니다. 대표 예가 theming(다크모드/색상 스킴), authentication(현재 로그인 사용자), routing(현재 경로/파라미터, 라우터 라이브러리가 내부적으로 사용), 글로벌 설정/feature flag입니다 [slide 6].

## 예시
가장 흔한 안티패턴은 `Layout` 같은 shell 컴포넌트가 자기와 무관한 데이터를 받아 자식에게 분배하는 모양입니다 [slide 5].

```js
// BEFORE — drilling
function Layout({ posts, user, theme }) {
  return (
    <div className={theme}>
      <Header user={user} />
      <Sidebar user={user} />
      <Content posts={posts} />
    </div>
  );
}

// AFTER — composition
function Layout({ children, theme }) {
  return <div className={theme}>{children}</div>;
}

// App.js
<Layout theme={theme}>
  <Header user={user} />
  <Sidebar user={user} />
  <Content posts={posts} />
</Layout>
```

`Layout`의 props가 3개에서 1개(+`theme`)로 줄었고, `posts`/`user`는 더 이상 거치지 않습니다. 중간 컴포넌트가 사라진 게 아니라 "데이터를 모르는 상태"로 바뀐 게 포인트입니다 — context 없이도 drilling이 해소됐습니다.

## 흔한 실수
- **composition으로 충분한 데이터를 context로 끌어올림**. shell 컴포넌트의 props를 `children`으로 비우기만 해도 풀리는 문제를 굳이 Provider로 감싸면 추적 가능성만 잃습니다.
- **value로 매 렌더 새 객체 리터럴**을 넘겨 모든 consumer를 재렌더시키기. [S6.C2]에서 봤듯 `<Ctx value={{a, b}}>` 패턴은 `useMemo`나 분리된 context로 안정화하세요.
- **"전역 = context"라고 단순화**하기. Redux/Zustand 같은 외부 store와 React context는 목적이 다릅니다 — context는 의존성 주입(DI) 채널이고, 자주 바뀌는 거대 상태에는 [S7]에서 다룰 reducer + context 조합이나 외부 라이브러리가 더 적합합니다.

## 복습
검토 순서는 **props → composition → context**입니다. theming/auth/routing/글로벌 설정처럼 분산된 다수 컴포넌트가 공유하는 값에 context를 쓰고, 1~2단 prop이나 composition으로 풀리는 문제는 그대로 두세요. 다음 [S7.C1]에서는 context와 reducer를 결합해 dispatch까지 트리에 꽂는 패턴으로 넘어갑니다.
