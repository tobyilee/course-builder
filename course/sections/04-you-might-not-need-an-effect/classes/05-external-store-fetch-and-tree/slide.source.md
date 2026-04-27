---
marp: true
theme: default
paginate: true
footer: "LO-S4.5"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  blockquote { color: #555; border-left: 4px solid #888; }
---

<!-- beat: b1 -->

# 'a'의 결과가 'abc' 자리에

### 외부 통합 · 종합 결정 트리

검색창에 빠르게 타이핑했더니 응답 순서가 어긋나 stale 결과가 표시.
온라인 인디케이터는 두 컴포넌트 사이에서 깜빡임.

> 마지막 안티패턴 **#11 외부 store**, **#12 fetch race**, 그리고 종합 결정 트리.

---

<!-- beat: b2 -->
<!-- _footer: "LO-S4.5" -->

## 안티패턴 #11 — 외부 store 수동 구독

- 증상: `useEffect` + `addEventListener` + `useState`로 `navigator.onLine` 미러링
- 문제
  - 두 컴포넌트가 각자 구독하면 **tearing** (값 불일치) 가능
  - SSR 초기값 처리가 까다롭다
- 정답: **`useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)`**
  - `subscribe`는 컴포넌트 외부 정의 → 한 번만 생성
  - `getSnapshot`은 매번 호출되어 최신값 반영, React가 일관성 보장

---

<!-- beat: b3 -->
<!-- _footer: "LO-S4.5" -->

## Before / After — useOnlineStatus

```tsx
// Before — Effect + state, tearing 위험
const [isOnline, setIsOnline] = useState(navigator.onLine);
useEffect(() => {
  const update = () => setIsOnline(navigator.onLine);
  window.addEventListener('online', update);
  window.addEventListener('offline', update);
  return () => { /* removeEventListener ... */ };
}, []);

// After — useSyncExternalStore로 캡슐화
function subscribe(cb) { /* add/remove listener */ return () => {}; }
function useOnlineStatus() {
  return useSyncExternalStore(subscribe, () => navigator.onLine, () => true);
}
```

---

<!-- beat: b4 -->
<!-- _footer: "LO-S4.5" -->

## 안티패턴 #12 — fetch in Effect의 race

- 증상: `query`/`page`가 빠르게 바뀌면 응답 순서가 어긋나 **stale 결과 표시**
- **1차 처방**: cleanup `ignore` flag — 이전 응답을 버린다
- **2차 처방**: `useData` 같은 커스텀 훅으로 패턴을 캡슐화
  → 컴포넌트는 `const data = useData(url)` 한 줄
- **3차 처방 (프로덕션)**: React Query · SWR · RSC
  → 캐시 · 취소 · 중복요청 자동 처리

---

<!-- beat: b5 -->
<!-- _footer: "LO-S4.5" -->

## Before / After — fetch with ignore → useData

```tsx
// Before — race condition
useEffect(() => {
  fetchResults(query, page).then(setResults);
}, [query, page]);

// After (1차) — ignore flag
useEffect(() => {
  let ignore = false;
  fetchResults(query, page).then(json => { if (!ignore) setResults(json); });
  return () => { ignore = true; };
}, [query, page]);

// After (2차) — useData 커스텀 훅
const results = useData(`/api/?q=${query}&p=${page}`);
```

---

<!-- beat: b6 -->
<!-- _footer: "LO-S4.6" -->

## 종합 결정 트리 — 12 패턴, 한 장

```text
Q1. render 중 계산 가능?  → 변수 한 줄         (#1)
Q2. 비싼가?                → useMemo            (#2)
Q3. 인터랙션 결과?        → 핸들러             (#5~#10)
Q4. prop 변경 시 리셋?    → key prop           (#3)
                          → derived /
                            state-during-render (#4)
Q5. 외부 store?            → useSyncExternalStore (#11)
    fetch?                 → Effect+ignore /
                            useData             (#12)
```

> 12 패턴 → **5 질문 · 5 leaf**로 흡수.

---

<!-- beat: b7 -->
<!-- _footer: "LO-S4.6" -->

## 잠깐 — 새 시나리오 3개를 정당화

- **(1) 검색 입력에 따라 결과 갱신**
  → Q5 외부(API) → fetch + ignore 또는 `useData`
- **(2) 장바구니 합계**
  → Q1 render 중 계산, 비싸지 않으면 `useMemo`도 불필요
- **(3) 라우트 변경 시 분석 로그**
  → 표시 기반이면 Effect(mount-only) · 클릭 트리거면 핸들러
- 각 선택의 *"왜 이 도구인가"* 한 문장 답변 연습

---

<!-- beat: b8 -->
<!-- _footer: "LO-S4.6" -->

## 정리 — 섹션 마무리

- **외부 store** → `useSyncExternalStore` (tearing 방지)
- **fetch in Effect** → 항상 `ignore` cleanup 또는 `useData` 캡슐화
- **12 패턴** → 5 질문 결정 트리 한 장으로 통합
- 다음 섹션부터는 *정당한 Effect*의 라이프사이클 이야기
