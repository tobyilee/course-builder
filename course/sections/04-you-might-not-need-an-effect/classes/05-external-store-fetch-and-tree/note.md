# 외부 통합과 종합 결정 트리 — useSyncExternalStore · fetch race
> LOs: LO-S4.5, LO-S4.6

## 개요
검색창에 'a' 'ab' 'abc'를 빠르게 쳤더니 'a'의 결과가 'abc' 자리에 표시되고, 헤더와 사이드바의 온라인 상태 인디케이터가 서로 어긋나 깜빡입니다 [slide 1]. 마지막 두 안티패턴 — **#11 외부 store 구독**과 **#12 fetch race condition** — 을 정리하고, 12 패턴을 한 장의 결정 트리로 합쳐 섹션을 닫습니다.

## 핵심 개념
**안티패턴 #11 — `navigator.onLine` 같은 React 외부 store를 수동 `useEffect + addEventListener`로 구독한다.** [slide 2]

문제는 두 컴포넌트가 각자 구독했을 때 발생합니다. 같은 시점에 서로 다른 값을 보는 **tearing**이 생길 수 있고, SSR에서 초기값을 정하기도 까다롭습니다. React가 제공하는 정답은 `useSyncExternalStore`입니다.

```tsx
const value = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
```

`subscribe`는 컴포넌트 외부에 한 번 정의해 재생성되지 않게 하고, `getSnapshot`은 매 렌더 호출되어 최신값을 반영합니다. React는 모든 구독자가 같은 값을 보도록 일관성을 보장합니다.

**안티패턴 #12 — `useEffect` 안에서 fetch한다.** [slide 4]

`query`나 `page`가 빠르게 바뀌면 응답 순서가 어긋나 stale 데이터가 화면에 박힐 수 있습니다 — 전형적인 race condition입니다. 처방은 세 단계로 점진합니다.

1. **ignore flag cleanup** — `let ignore = false; return () => { ignore = true; }`로 늦은 응답을 폐기합니다.
2. **`useData` 같은 커스텀 훅으로 캡슐화** — 컴포넌트 본문은 `const data = useData(url)`만 호출. [S8.C1] 에서 다시 다룹니다.
3. **데이터 레이어 도입** — React Query, SWR, RSC가 캐시·취소·중복요청을 자동 처리합니다.

## 예시
**#11 — `useOnlineStatus` 훅** [slide 3]:

```tsx
function subscribe(cb) {
  window.addEventListener('online', cb);
  window.addEventListener('offline', cb);
  return () => {
    window.removeEventListener('online', cb);
    window.removeEventListener('offline', cb);
  };
}

function useOnlineStatus() {
  return useSyncExternalStore(
    subscribe,
    () => navigator.onLine,
    () => true // SSR 기본값
  );
}
```

**#12 — 3단계 리팩터링** [slide 5]:

```tsx
// Step 1 — ignore cleanup
useEffect(() => {
  let ignore = false;
  fetchResults(query, page).then(json => {
    if (!ignore) setResults(json);
  });
  return () => { ignore = true; };
}, [query, page]);

// Step 2 — useData로 추출
function useData(url) {
  const [data, setData] = useState(null);
  useEffect(() => {
    let ignore = false;
    fetch(url).then(r => r.json()).then(json => {
      if (!ignore) setData(json);
    });
    return () => { ignore = true; };
  }, [url]);
  return data;
}

const results = useData(`/api/?q=${query}&p=${page}`);
```

**종합 결정 트리** [slide 6] — 12 패턴을 5개 leaf로 흡수합니다.

```
Q1 render 중 계산 가능?  → 변수 한 줄          (#1)
Q2 비싼가?                → useMemo            (#2)
Q3 인터랙션 결과?         → 핸들러             (#5~#10)
Q4 prop 변경 시 리셋?     → key / state-in-render (#3, #4)
Q5 외부 store?            → useSyncExternalStore (#11)
   외부 fetch?            → Effect+ignore / useData (#12)
```

세 시나리오로 한 번 흘려보내 봅시다 [slide 7]: ① 검색 입력에 따른 결과 갱신은 외부 API니까 `useData` 또는 ignore cleanup. ② 장바구니 합계는 render 중 계산, items가 1만 개를 넘지 않으면 `useMemo`도 불필요. ③ 라우트 변경 시 분석 로그는 "표시되었기 때문"이면 mount-only Effect, "메뉴를 클릭했기 때문"이면 핸들러.

## 흔한 실수
이 클래스에서 가장 위험한 함정은 **fetch race condition을 못 본 척하는 것**입니다. "내 앱은 빠른 입력을 다루지 않으니 괜찮다"고 넘어가면, 모바일 환경의 느린 네트워크나 사용자가 뒤로 가기를 빠르게 누르는 경우에서 결국 stale 화면이 나타납니다. ignore flag는 5줄짜리 보험이니 fetch가 들어간 모든 Effect에 기본 탑재로 두세요. 또 하나 자주 보이는 실수는 **`useSyncExternalStore`의 `getServerSnapshot`을 빼먹는 것**입니다. SSR 환경에서 `navigator`처럼 서버에 없는 객체를 그냥 호출하면 hydration 에러가 납니다. 세 번째 인자를 항상 명시적으로 채우는 습관을 들여 두세요. 실제 앱에서 데이터 페칭이 늘어난다 싶으면 손수 ignore 패턴을 반복하지 말고 React Query·SWR 같은 데이터 레이어로 갈아타는 시점이 곧 옵니다 — 손으로 짠 race 처리가 다섯 곳을 넘기 전에요.

## 복습
- 외부 store는 `useSyncExternalStore` — tearing과 SSR을 동시에 해결합니다.
- fetch in Effect는 항상 ignore cleanup, 가능하면 `useData`로 캡슐화.
- 12 안티패턴은 5개 질문 결정 트리 한 장으로 통합됩니다.
- 다음 섹션 [S5.C1] 부터는 "정당한 Effect"의 라이프사이클로 들어갑니다.
