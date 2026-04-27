---
marp: true
theme: default
paginate: true
footer: "LO-S5.4"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 21px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# exhaustive-deps 해결과 Effect 분리

## 빨간 줄에 응급처치 말고 코드를 바꾸자

LO-S5.4 · LO-S5.5

---

<!-- beat: b1 -->

## ESLint 빨간 줄 — 두 가지 응급처치

- `React Hook useEffect has a missing dependency: 'roomId'`
- ❌ `// eslint-disable-next-line` 으로 덮기
- ❌ 무지성으로 deps에 그냥 추가
- 둘 다 틀렸다 — 정답은 **코드를 바꾸는 것**, 그 길은 세 갈래

---

<!-- beat: b2 -->
<!-- _footer: "LO-S5.4" -->

## 세 가지 옵션 — 결정 트리

- **옵션 1** — 진짜 reactive면 deps에 추가, 재실행이 의도된 동작이게 만든다
- **옵션 2** — 사실 non-reactive였다면 컴포넌트 밖으로 옮기거나 Effect 안에서 생성
- **옵션 3** — 최신 값은 필요한데 재동기화는 싫다면 `useEffectEvent`로 추출 (다음 강의)
- 결정 기준: "이 값이 바뀌면 동기화를 새로 시작해야 하는가?" Yes→1, No→2/3
- 🚫 절대 금지: linter suppress — stale closure 버그를 그대로 통과시킨다

---

<!-- beat: b3 -->
<!-- _footer: "LO-S5.4" -->

## 케이스별 처방 — 같은 경고, 다른 답

```jsx
// 옵션 1: roomId는 진짜 reactive (재연결이 의도)
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);

// 옵션 2: serverUrl을 컴포넌트 밖 상수로
const serverUrl = 'https://localhost:1234'; // 모듈 스코프

// 옵션 3: 미리보기 (다음 강의)
// const onTheme = useEffectEvent(() => notify(theme));
```

같은 경고도 코드 맥락에 따라 처방이 다르다

---

<!-- beat: b4 -->
<!-- _footer: "LO-S5.5" -->

## Effect 분리 원칙

- **하나의 Effect = 하나의 독립적 동기화 프로세스**
- 한 Effect 안에 무관한 동기화가 묶이면 한쪽 deps 변경이 다른 쪽도 재실행시킨다
- 분리 기준: cleanup이 정말 한 쌍으로 묶여야 하는가?
- deps가 같다고 합치는 게 아니라 **책임이 같아야** 합친다

---

<!-- beat: b5 -->
<!-- _footer: "LO-S5.5" -->

## Before / After — logVisit + 채팅 분리

```jsx
// 🔴 Before — 채팅 + 분석 섞임
useEffect(() => {
  logVisit(roomId);
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);

// ✅ After — 책임별 분리
useEffect(() => { logVisit(roomId); }, [roomId]);
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [roomId]);
```

---

<!-- beat: b6 -->
<!-- _footer: "LO-S5.5" -->

## 자문자답 — 분리 vs 유지?

```jsx
useEffect(() => {
  window.addEventListener('scroll', onScroll);
  document.title = roomId;
  return () => window.removeEventListener('scroll', onScroll);
}, [roomId]);
```

- 정답: **분리한다**
- scroll 리스너의 cleanup은 `removeEventListener`, title 동기화는 cleanup도 deps도 다른 책임
- 신호: "두 코드를 다른 시점에 시작/중지하고 싶어지면 분리하라"

---

<!-- beat: b7 -->

## 정리 — 세 줄

- ✅ exhaustive-deps는 suppress가 아니라 코드를 바꿔 해결 (deps 추가 / 외부화 / useEffectEvent)
- ✅ linter 경고는 "코드 설계의 거울"로 받아들인다
- ✅ 한 Effect = 한 동기화 책임. 책임이 다르면 분리해 각자의 deps와 cleanup을 갖게
