---
marp: true
theme: default
paginate: true
footer: "LO-S8.4"
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
---

<!-- beat: b1 -->

# 추출할 것인가, 말 것인가

## composition과 미래 대비

다 빼고 싶은 충동을 멈출 시간 — 두 갈래 표지판

---

<!-- beat: b2 -->
<!-- _footer: "LO-S8.4" -->

## 추출 / 회피 — 한눈 기준

| ✅ 추출하라 | ❌ 추출하지 마라 |
|---|---|
| 여러 컴포넌트에 같은 stateful 로직 | 한 컴포넌트에서만 쓰는 로직 |
| 외부 시스템 동기화 Effect | Hook 호출 없는 함수 (일반 함수로) |
| 도메인 의미가 이름에 드러남 | `useMount`, `useEffectOnce` (lifecycle wrapper) |
| 구현 세부를 호출처로부터 숨김 | — |

기준 한 줄: **"도메인 이름이 붙는가?"**

---

<!-- beat: b3 -->
<!-- _footer: "LO-S8.4" -->

## useMount는 왜 안티패턴?

```jsx
// ❌ 안티패턴
function useMount(fn) {
  useEffect(fn, []); // deps 항상 []
}

// 사용처
useMount(() => {
  connect(roomId); // roomId가 reactive해도 deps에 안 들어감
});
```

- **deps 거짓말**: `roomId` 바뀌어도 재연결 안 됨, stale closure
- **linter 무력화**: exhaustive-deps가 fn 내부를 분석 못 함
- 도메인 없음 + 검사 회피 → 회피 후보

---

<!-- beat: b4 -->
<!-- _footer: "LO-S8.5" -->

## Composition — Hook이 Hook을 부른다

```jsx
function useInterval(callback, delay) {
  const onTick = useEffectEvent(callback);
  useEffect(() => {
    const id = setInterval(onTick, delay);
    return () => clearInterval(id);
  }, [delay]);
}

function useCounter(delay) {
  const [count, setCount] = useState(0);
  useInterval(() => setCount(c => c + 1), delay);
  return count;
}
// 사용처: const count = useCounter(1000);
```

도메인 사다리: `useEffect` → `useInterval` → `useCounter`

---

<!-- beat: b5 -->
<!-- _footer: "LO-S8.5" -->

## 캡슐화의 보상 — 미래 API로 갈아끼우기

```jsx
// Before: useState + useEffect (12줄)
function useOnlineStatus() { /* ... */ }

// After: useSyncExternalStore (3줄)
function useOnlineStatus() {
  return useSyncExternalStore(
    subscribe,
    () => navigator.onLine,
    () => true,
  );
}
```

호출처(`StatusBar`, `SaveButton`) 변경: **0** — 한 글자도 안 바뀜

---

<!-- beat: b6 -->

## 직접 답해보세요

- Q1. 한 컴포넌트에서만 쓰는 fetch 50줄, 추출? → **NO**. 두 번째 사용처 생길 때
- Q2. 팀이 `useUpdateEffect` 도입하자고 하면? → **위험**. 도메인 없음 + 가짜 lifecycle
- Q3. `useCounter` 안에서 `useInterval` 부르는 건 위반? → **합법**, 권장
- Q4. `useSyncExternalStore`로 교체 시 호출처 테스트 다시? → **불필요**. 반환 동일

---

<!-- beat: b7 -->
<!-- _footer: "LO-S8.5" -->

## 오늘의 3줄

- **추출 기준**: 반복 + 도메인 의미. 단일 사용처/Hook 미호출/lifecycle wrapper는 회피
- **Composition**: Hook이 Hook을 부르며 도메인 사다리를 쌓는다
- **캡슐화의 보상**: 호출처 변경 0으로 미래 API(`useSyncExternalStore`)로 갈아끼울 수 있다
