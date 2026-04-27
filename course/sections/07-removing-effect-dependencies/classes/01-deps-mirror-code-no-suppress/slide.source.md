---
marp: true
theme: default
paginate: true
footer: "LO-S7.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  table { font-size: 22px; }
---

<!-- beat: b1 -->

# deps는 코드의 거울

## linter suppress 절대 금지 원칙

LO-S7.1 · Effect 의존성 줄이기 6 전략

---

<!-- beat: b1 -->

## 한 줄짜리 suppress가 만드는 버그

```jsx
useEffect(() => {
  const id = setInterval(() => {
    setCount(count + 1);
  }, 1000);
  return () => clearInterval(id);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []);
```

- 화면에는 `1, 1, 1, 1...` 만 찍힌다
- 콘솔 에러는 없지만 카운터가 멈춘다

---

<!-- beat: b2 -->
<!-- _footer: "LO-S7.1" -->

## 원칙 — deps는 '고르는 것'이 아니다

- Effect 본문이 사용한 reactive 값(prop/state/렌더 변수)이 곧 deps
- 코드와 deps가 어긋나면 React가 잘못된 시점에 재실행하거나 아예 안 함
- linter `exhaustive-deps`는 거울이 잘 맞는지 검사하는 도구
- 거울 비유: 코드를 안 바꾸고 deps만 손대면 거울 속 얼굴을 지우는 것

---

<!-- beat: b3 -->
<!-- _footer: "LO-S7.1" -->

## frozen closure가 카운터를 1에 묶는 이유

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    // 첫 렌더의 count(=0)가 영구 캡처됨
    setInterval(() => setCount(count + 1), 1000);
  }, []); // ← suppress
}
```

- 매 tick마다 `setCount(0 + 1)`만 실행 → 화면은 항상 1
- suppress는 문제를 숨길 뿐, 해결하지 않는다

---

<!-- beat: b4 -->
<!-- _footer: "LO-S7.2" -->

## 올바른 워크플로 + 6 전략 매핑

| 문제 신호 | 후보 전략 |
|---|---|
| 절대 안 바뀌는 값이 deps에 | ① 정적값 외부화 |
| 객체/함수 deps로 무한 재실행 | ② Effect 안에서 생성 |
| state를 쓰기 위해 읽는 패턴 | ③ updater 함수 |
| 읽고 싶지만 반응시키긴 싫음 | ④ useEffectEvent |
| 한 Effect가 여러 동기화 묶음 | ⑤ Effect 분리 |
| 부모가 매 렌더 새 객체 prop | ⑥ 원시값 분해 |

워크플로: 작성 → linter → 코드 변경 → 반복

---

<!-- beat: b5 -->
<!-- _footer: "LO-S7.2" -->

## 미니 자문자답 — 어느 전략 후보?

- (1) options 객체 deps로 무한 재연결 → ?
- (2) `setCount(count + 1)` 때문에 매 tick 재생성 → ?
- (3) isMuted 토글마다 채팅 끊김 → ?
- (4) country fetch + city fetch 한 Effect → ?

정답은 다음 두 class에서 코드로 확인합니다

---

<!-- beat: b6 -->

## 정리 — 세 줄

- 거울 — deps는 Effect 코드가 결정한다
- suppress 금지 — frozen closure 버그의 지름길
- 워크플로 — 작성 → linter → 코드 변경 → 반복, 도구는 6 전략
