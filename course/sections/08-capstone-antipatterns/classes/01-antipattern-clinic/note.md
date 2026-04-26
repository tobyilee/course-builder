# 안티패턴 진단 클리닉 — 5대 코드 스멜 한 번에 잡기
> LOs: LO-S8.1

## 개요

지금까지 7개 챕터를 거치며 state 설계 원칙을 차곡차곡 쌓았습니다. 이번 클래스에서는 그 원칙들을 **거꾸로** 써봅니다. 한 화면에 5대 안티패턴이 동시에 박힌 "환자" 코드를 진단하고, 각 증상이 어느 챕터의 처방으로 회수되는지 1:1로 매핑합니다 [slide 1]. 끝나면 코드 리뷰에서 즉시 펼쳐 쓸 수 있는 5문항 체크리스트가 손에 남습니다.

## 핵심 개념

다섯 가지 안티패턴은 각각 다른 얼굴을 하고 있지만, 결국 **"state는 무엇이며, 어디서, 어떻게 살아야 하는가"** 라는 같은 질문에 잘못 답한 결과입니다 [slide 2].

- **① props mirroring** — 부모가 준 값을 `useState`의 초기값으로 복제. 부모가 새 값을 줘도 자식은 첫 값에 갇힙니다. → 직접 `props.user`를 쓰고, 정말 초기값만 필요하면 `initialUser` 접두사 + `key`로 명시 리셋 ([S2.C1] 원칙).
- **② redundant state** — `firstName`, `lastName`이 있는데 `fullName`을 또 `useState`로 보관. 둘 사이가 어긋나는 순간 동기화 버그가 시작됩니다. → 렌더 중 계산하는 **derived value**가 정답. state는 "입력", 파생값은 "출력".
- **③ deep nesting** — `places.children.children.children`. 한 노드 추가에도 모든 조상을 불변 갱신해야 합니다. → `byId` + `childIds`로 평탄화 ([S2.C4]).
- **④ 컴포넌트 안에 컴포넌트 정의** — 매 렌더마다 새로운 컴포넌트 *타입*이 생성되어 React는 "다른 트리"로 판단, 자식 state 전체가 리셋됩니다. → 항상 모듈 최상단에서 정의 ([S4.C3]).
- **⑤ context 남용** — "전역이면 편하니까"라며 모든 값을 context로. 작은 값 하나만 바뀌어도 트리 전체 재렌더, 의존 추적 불가. → theming/auth/routing처럼 진짜 글로벌인 것만 context, 나머지는 props 또는 composition ([S6.C3]).

핵심은 매핑입니다 [slide 4]: **①②③ → S2 구조 설계**, **④ → S4 보존/리셋**, **⑤ → S6 context 남용 판별**. 안티패턴은 진공에서 떨어지지 않습니다 — 모두 이미 배운 원칙의 그림자입니다.

## 예시

`ProfilePage`에 5대 패턴이 동시에 박혀 있다고 해봅시다 [slide 5].

```tsx
function ProfilePage({ user }) {
  const [localUser, setLocalUser] = useState(user);            // ①
  const [fullName, setFullName] = useState(`${user.first} ${user.last}`); // ②
  const [comments, setComments] = useState(nestedTree);        // ③

  function Avatar({ src }) { return <img src={src} />; }       // ④

  return (
    <ThemeContext value={theme}>
      <UserContext value={localUser}>                          // ⑤ 남용
        <Avatar src={localUser.avatar} />
        <h1>{fullName}</h1>
      </UserContext>
    </ThemeContext>
  );
}
```

리팩터링은 한 줄씩 진행합니다. `localUser` 제거 → `user.first + ' ' + user.last`를 렌더 중 계산 → `comments`를 `{byId, rootIds}`로 평탄화 → `Avatar`를 파일 최상단으로 이동 → `UserContext`를 제거하고 `Avatar`에는 `src`만 props로. 50줄짜리가 30줄로 줄고, 읽는 사람의 머리 속 모델도 그만큼 가벼워집니다.

## 흔한 실수

**"이 패턴이 보이면 이렇게 리팩터링하라"** 의 관점으로 정리합시다.

- `useEffect(() => setX(props.x), [props.x])` 형태가 보이면 거의 항상 ① props mirroring입니다. effect 자체를 지우고 props를 직접 쓰세요.
- 두 state가 항상 함께 바뀌는 코드(`setFirst` 옆에 `setFull`이 따라다님)는 ② redundant의 강한 신호. 둘 중 하나는 derived여야 합니다.
- "팀 모두가 쓰니까 context"라는 정당화는 위험합니다. consumer가 3~4개 컴포넌트뿐이라면 composition으로 충분한 경우가 대부분입니다 ([S6.C3]).

## 복습

5대 안티패턴 = ①props mirror ②redundant ③deep nesting ④nested 정의 ⑤context 남용. 각 챕터 원칙으로 1:1 매핑되는 **진단 가능한** 코드 스멜이 됐습니다. 다음 클래스([S8.C2])에서는 거꾸로, 0에서부터 의사결정 사슬을 직접 따라가 봅니다.
