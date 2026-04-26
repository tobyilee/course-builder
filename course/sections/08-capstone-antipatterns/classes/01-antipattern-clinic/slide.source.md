---
marp: true
theme: default
paginate: true
footer: "LO-S8.1"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# 안티패턴 진단 클리닉

## 5대 코드 스멜 한 번에 잡기

- 컴파일은 되는데 자꾸 버그 나는 코드, 본 적 있죠?
- S2~S7 원칙을 **거꾸로** 적용해 진단해봅니다
- 끝나면 코드 리뷰용 5문항 체크리스트가 손에 들어옵니다

---

<!-- beat: b2 -->

## ① props mirror & ② redundant state

- **①** `useState(props.user)` — 부모 갱신을 자식이 무시
- 처방: props 직접 사용. 정말 초기값이면 `initial*` + `key`로 명시 리셋
- **②** `fullName`을 따로 `useState`로 보관
- 처방: 렌더 중 계산. **state는 입력, 파생값은 출력**
- 둘 다 회수 챕터: **S2 — redundant 제거**

---

<!-- beat: b3 -->

## ③ deep nesting & ④ nested 컴포넌트 정의

- **③** `places.children.children.children` — setState 지옥
- 처방: `byId` + `childIds`로 평탄화 (S2.5)
- **④** 컴포넌트 안에 컴포넌트 정의 → 매 렌더 새 타입 → state 리셋
- 처방: 컴포넌트는 **항상 모듈 최상단**에서 정의 (S4.4)
- 공통 교훈: **구조가 곧 동작을 결정한다**

---

<!-- beat: b4 -->

## ⑤ context 남용 & 매핑표

- **⑤** "전역이면 편하잖아?" → 작은 변경에도 트리 전체 재렌더
- 처방: theme/auth/routing처럼 **진짜 글로벌**만. 나머지는 props 또는 composition (S6.4)

| 안티패턴 | 챕터 | 한 줄 처방 |
|---|---|---|
| ① props mirror | S2 | props 직접 사용 |
| ② redundant | S2 | 렌더 중 derive |
| ③ deep nesting | S2.5 | id-맵 정규화 |
| ④ nested 정의 | S4.4 | 모듈 최상단으로 |
| ⑤ context 남용 | S6.4 | 진짜 글로벌만 |

---

<!-- beat: b5 -->

## 워크스루 — ProfilePage 5단계 수술

```jsx
// before: 5대 안티패턴 동시 발현
function ProfilePage({ user }) {
  const [u, setU] = useState(user);          // ①
  const [fullName, setFullName] = useState(  // ②
    u.first + ' ' + u.last);
  const [comments, setComments] = useState(  // ③ 깊은 트리
    user.comments);
  function Avatar() { /* ... */ }            // ④ 내부 정의
  return <ThemeCtx><AuthCtx><LangCtx>...     // ⑤ context 남용
}
// after: props 직접 / derive / byId / 모듈 최상단 / ThemeCtx만
const fullName = `${user.first} ${user.last}`;
```

---

<!-- beat: b6 -->

## 코드 리뷰 체크리스트 5문항

- [ ] `useEffect`로 props를 state에 sync하는 코드 있나? → ①
- [ ] 다른 state로부터 계산 가능한 state가 있나? → ②
- [ ] 객체 트리가 3단계 이상 깊나? → ③
- [ ] 컴포넌트가 다른 컴포넌트 함수 안에 정의되어 있나? → ④
- [ ] context가 5개 넘게 쌓여있나? → ⑤

---

<!-- beat: b7 -->

## 정리 — 진단 가능한 코드 스멜

- 5대 안티패턴: **mirror · redundant · nesting · nested-def · context 남용**
- 각 챕터 원칙으로 1:1 매핑 완료
- 다음 클래스: **거꾸로**, 0에서부터 의사결정 사슬을 직접 따라간다
