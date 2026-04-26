---
marp: true
theme: default
paginate: true
footer: "LO-S6.4"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 24px; }
---

<!-- beat: b1 -->

# Context, 언제 쓰고 언제 안 쓸까

## props · composition과 비교

S6.C3 · 13분

---

<!-- beat: b1 -->
<!-- _footer: "LO-S6.4" -->

## Provider 지옥의 함정

- context를 배우면 모든 prop을 옮기고 싶어진다
- 결과 — 어디서 값이 오는지 추적 불가능한 코드
- **Provider 10겹 중첩**으로 진입점이 사라진다
- context는 강력하지만 **첫 도구가 되어선 안 된다**
- 오늘은 꺼내기 전 검토할 **두 대안**을 배운다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S6.4" -->

## 결정 사다리 — props → composition → context

- **1단계 props** — 1~2 레벨이면 그대로, 흐름이 코드에 보인다
- **2단계 composition** — `<Layout><Posts posts={posts}/></Layout>`로 거리 단축
- **3단계 context** — 둘 다 적용했는데도 여전히 멀 때
- 트리거 — *"props로 흐를 거리를 줄였는데도 멀다"* = context

---

<!-- beat: b3 -->
<!-- _footer: "LO-S6.4" -->

## BEFORE — Layout이 모든 걸 안다

```js
function Layout({ posts, user, theme }) {
  return (
    <div className={theme}>
      <Header user={user} />
      <Sidebar user={user} />
      <Content posts={posts} />
    </div>
  );
}
```

Layout은 자기 일(레이아웃)과 무관한 `posts`까지 들고 다닌다

---

<!-- beat: b3 -->
<!-- _footer: "LO-S6.4" -->

## AFTER — composition으로 해소

```js
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

Layout은 이제 `posts`/`user`를 **모른다** — context 없이 drilling 해소

---

<!-- beat: b4 -->
<!-- _footer: "LO-S6.4" -->

## Context가 정당한 사례

- **Theming** — 다크모드, 색상 스킴
- **Authentication** — 현재 로그인 사용자
- **Routing** — 현재 경로/파라미터 (라우터가 내부 사용)
- **분산 reducer state** — useReducer + context 조합
- **글로벌 설정** — feature flag, 앱 전반 옵션

공통 — *분산된 다수 컴포넌트* + *깊이 무관* + *자주 안 바뀜*

---

<!-- beat: b5 -->
<!-- _footer: "LO-S6.4" -->

## 케이스 진단 — props / composition / context?

- **A** — Form이 자식 Input에 `disabled`를 1단계만 내려보냄
- **B** — 다크모드 토글이 Header/Sidebar/Card/Footer 색을 바꿈
- **C** — Page가 PostList에 posts 전달, PostList는 Layout으로만 감싸여 있다

각 케이스에 *"drilling 거리를 단축할 수 있는가"*를 적용해 보자

---

<!-- beat: b6 -->
<!-- _footer: "LO-S6.4" -->

## 정리

- **검토 순서** — 먼저 props, 다음 composition, 그래도 멀면 context
- **정당한 사례** — theming · auth · routing · 글로벌 설정
- 다음 section 예고 — **context + reducer**로 dispatch까지 트리에 꽂는 패턴
