---
marp: true
theme: default
paginate: true
footer: "LO-S0.1"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  blockquote { color: #555; border-left: 4px solid #888; }
---

<!-- beat: b1 -->

# 왜 'Escape Hatch'인가

### React 기본 흐름과 마지막 수단

`useRef` · `useEffect` · Custom Hook을 왜 "비상구"라고 부를까?

> 직전 *Managing State* 코스 → 이번엔 그 흐름 **바깥** 이야기.

---

<!-- beat: b2 -->
<!-- _footer: "LO-S0.1" -->

## 복습 — React 기본 흐름 3요소

- **선언형 렌더**: state → UI를 한 줄로 설명
- **순수 함수형 컴포넌트**: 같은 입력이면 같은 출력
- **단방향 props**: 데이터는 위에서 아래로만 흐름
- 미덕: 예측 가능, 테스트 쉬움, 디버깅 동선이 짧음
- *Managing State* 코스의 90% 케이스는 이 흐름 안에서 해결

---

<!-- beat: b3 -->
<!-- _footer: "LO-S0.1" -->

## 그런데 React 바깥의 세계가 있다

- **외부 시스템 동기화** — 서버 연결, 구독, 타이머
- **명령형 DOM 조작** — focus, scroll, video.play()
- **비-렌더 데이터 보관** — timeout ID, 디바운서 인스턴스
- 공통점: *렌더 결과*만으로 표현할 수 없는 일
- 도구 매핑 → **Effects / DOM Refs / Value Refs**, 묶으면 **Custom Hook**

---

<!-- beat: b4 -->
<!-- _footer: "LO-S0.1" -->

## 세 가지 시나리오, 한눈에 보기

```tsx
// ① focus — DOM ref
const inputRef = useRef<HTMLInputElement>(null);
useEffect(() => { inputRef.current?.focus(); }, []);

// ② debounce timer ID — value ref
const timerRef = useRef<number | null>(null);

// ③ chat 서버 재연결 — Effect + cleanup
useEffect(() => {
  const conn = createConnection(roomId);
  conn.connect();
  return () => conn.disconnect();
}, [roomId]);
```

---

<!-- beat: b5 -->
<!-- _footer: "LO-S0.3" -->

## 왜 '마지막 수단'인가 — 세 가지 비용

- **예측 가능성 비용**: 렌더 바깥 동작 → 코드만 보고 결과 추론이 어렵다
- **테스트 용이성 비용**: 외부 시스템이 끼면 단위 테스트가 통합 테스트가 된다
- **동기화 비용**: 의존성 배열 관리 실수 → stale 또는 무한 재실행
- 그래서 기본자세 = **되도록 안 쓰는 것**, 쓸 땐 정당한 이유가 있어야

---

<!-- beat: b6 -->
<!-- _footer: "LO-S0.1" -->

## 잠깐 퀴즈 — 어떤 게 Escape Hatch?

- (a) 입력창의 글자 수를 화면에 표시
- (b) 입력 후 500ms 기다렸다 검색 호출
- (c) 두 컴포넌트가 같은 카운터 값을 공유

> 정답: **(b)** — 타이머 ID 보관 + 외부 타이머 필요
> (a)는 derived 값, (c)는 lifting — 둘 다 기본 흐름

핵심 질문: *"렌더 결과만으로 설명되나? 외부 시스템이 끼어 있나?"*

---

<!-- beat: b7 -->
<!-- _footer: "LO-S0.3" -->

## 정리 — 오늘의 멘탈모델

- **기본 흐름** = 선언형 + 순수 + 단방향 → 90% 사례 해결
- **Escape Hatch 시나리오 3종** = 외부 동기화 / 명령형 DOM / 비-렌더 데이터
- 쓸 땐 **비용 3가지**(예측·테스트·동기화)를 의식
- 다음 시간 → 이 자세를 **결정 트리**로 행동화한다
