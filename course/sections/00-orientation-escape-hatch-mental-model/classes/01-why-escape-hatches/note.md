# 왜 'Escape Hatch'인가 — React의 기본 흐름과 마지막 수단

> LOs: LO-S0.1, LO-S0.3

## 개요

직전 'Managing State' 코스에서 우리는 `useState`, lifting, `key`, `useReducer`, context까지 거의 모든 UI 상태 패턴을 다뤘습니다. 그런데 실무에서는 그 도구들로 풀리지 않는 순간이 옵니다 — input에 focus 주기, 디바운스 타이머 ID 보관, 채팅 서버 연결 같은 일들이죠 [slide 1]. 그 자리에 등장하는 `useRef`, `useEffect`, Custom Hook을 React 공식 문서는 '비상구(Escape Hatch)'라 부릅니다. 오늘은 왜 이 이름이 붙었는지, 그리고 왜 '마지막 수단'으로 다뤄야 하는지부터 짚습니다.

## 핵심 개념

**React의 기본 흐름 = 선언형 렌더 + 순수 함수형 컴포넌트 + 단방향 props** [slide 2]. 같은 state면 같은 UI가 나오기에 예측 가능하고, 테스트가 쉽고, 디버깅 동선이 짧습니다. 'Managing State' 코스의 90% 사례는 이 흐름 안에서 끝납니다 — UI 상태는 `useState`, 부모-자식 공유는 lifting, 인스턴스 분리는 `key`, 트리 전파는 context.

그런데 React 바깥의 세계가 있습니다 — 브라우저 DOM API, 타이머, 네트워크 소켓, 서드파티 라이브러리. Escape Hatch가 등장하는 시나리오는 셋입니다 [slide 3]:

1. **외부 시스템 동기화** (서버 연결, 구독) → `useEffect`
2. **명령형 DOM 조작** (focus, scroll, play) → DOM ref
3. **비-렌더 데이터 보관** (timeout ID, 디바운서 인스턴스) → value ref

세 시나리오의 공통점은 '렌더 결과로 표현되지 않는 일'이라는 점입니다. 재사용 단위로 묶으면 Custom Hook이 됩니다.

## 예시

세 가지 코드 패턴으로 감을 잡아봅시다 [slide 4].

```tsx
// ① 명령형 DOM: 마운트 시 input focus
const inputRef = useRef<HTMLInputElement>(null);
useEffect(() => { inputRef.current?.focus(); }, []);
return <input ref={inputRef} />;

// ② 비-렌더 데이터: 디바운스 타이머 ID
const timerRef = useRef<number | null>(null);
const onChange = (v: string) => {
  if (timerRef.current) clearTimeout(timerRef.current);
  timerRef.current = window.setTimeout(() => search(v), 300);
};

// ③ 외부 시스템 동기화: roomId 바뀔 때 재연결
useEffect(() => {
  const conn = createConnection(roomId);
  conn.connect();
  return () => conn.disconnect();
}, [roomId]);
```

①은 `useState`로는 표현 불가합니다 — DOM 노드의 `.focus()`는 명령형 호출이니까요. ②에서 타이머 ID를 state에 두면 매 입력마다 재렌더가 폭증합니다. ③은 cleanup이 이전 연결을 안전하게 끊어줍니다. 셋 모두 '렌더 함수만으로는 표현 안 되는 부분'이 본질입니다.

## 흔한 실수

**오해 1: "Escape Hatch는 강력하니 자주 쓰면 좋다."** 정반대입니다. 세 가지 비용이 따라옵니다 [slide 5] — (a) 예측 가능성 비용: ref/effect는 렌더 결과 바깥에서 동작해 코드만 보고 결과를 추론하기 어렵습니다. (b) 테스트 용이성 비용: 외부 시스템이 끼면 단위 테스트가 통합 테스트로 격상됩니다. (c) 동기화 비용: Effect는 의존성 배열을 계속 관리해야 하고, 까먹으면 stale 또는 무한 재실행입니다.

**오해 2: "이벤트로 발생한 일도 Effect에 넣으면 안전하다."** 클릭으로 발생한 결과를 `useEffect`로 우회하면 한 박자 늦게 실행되고 추적이 어려워집니다. 이 분기 판단은 다음 클래스의 결정 트리 [S0.C2]에서 다룹니다.

## 복습

- 기본 흐름 = 선언형 렌더 + 순수 함수 + 단방향 props — 90% 사례는 여기서 해결
- Escape Hatch 시나리오 3종 = 외부 동기화 / 명령형 DOM / 비-렌더 데이터
- 쓸 땐 비용 3가지(예측·테스트·동기화)를 의식 — 기본은 안 쓰는 것
- 다음 클래스 [S0.C2]에서 이 자세를 결정 트리로 행동화합니다
