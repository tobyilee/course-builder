# Source: You Might Not Need an Effect

## 핵심 원칙
Effect는 **외부 시스템 동기화 escape hatch**. 외부 시스템이 없다면 Effect도 필요 없음.

## 12가지 안티패턴 (Before / After)

### 1. props/state 기반 state 갱신
```js
// 🔴 Effect로 derived state 보관
const [fullName, setFullName] = useState('');
useEffect(() => setFullName(firstName + ' ' + lastName), [firstName, lastName]);

// ✅ render 중 계산
const fullName = firstName + ' ' + lastName;
```

### 2. 비싼 계산 캐싱
```js
// 🔴
useEffect(() => setVisibleTodos(getFilteredTodos(todos, filter)), [todos, filter]);
// ✅ useMemo
const visibleTodos = useMemo(() => getFilteredTodos(todos, filter), [todos, filter]);
```
React Compiler가 자동 메모이즈하는 경우도 많음.

### 3. prop 변경 시 전체 state 리셋
```js
// 🔴
useEffect(() => setComment(''), [userId]);
// ✅ key prop
<Profile userId={userId} key={userId} />
```

### 4. prop 변경 시 일부 state 조정
```js
// 🔴
useEffect(() => setSelection(null), [items]);

// ✅ render 중 직접 조정 (state-during-render)
const [prevItems, setPrevItems] = useState(items);
if (items !== prevItems) {
  setPrevItems(items);
  setSelection(null);
}

// ✅ 더 좋음: derived
const selection = items.find(i => i.id === selectedId) ?? null;
```

### 5. 이벤트 핸들러 간 로직 공유
```js
// 🔴 Effect — 페이지 리로드 시 잘못 발화
useEffect(() => {
  if (product.isInCart) showNotification(`Added ${product.name}!`);
}, [product]);

// ✅ 함수로 추출 → 핸들러에서 호출
function buyProduct() { addToCart(product); showNotification(...); }
```

### 6. POST 요청
- **분석/방문 로그** = "표시되었기 때문에" → Effect (mount-only)
- **폼 제출** = "사용자가 클릭했기 때문에" → 핸들러

### 7. 계산 체인
```js
// 🔴 multiple Effects 갱신 — 캐스케이딩 재렌더
useEffect(() => { if (card?.gold) setGoldCount(c => c + 1); }, [card]);
useEffect(() => { if (goldCount > 3) { setRound(r => r + 1); setGoldCount(0); } }, [goldCount]);

// ✅ 한 핸들러에 다 모음
function handlePlaceCard(nextCard) {
  setCard(nextCard);
  if (nextCard.gold) {
    if (goldCount < 3) setGoldCount(goldCount + 1);
    else { setGoldCount(0); setRound(round + 1); if (round === 5) alert(...); }
  }
}
```

### 8. 앱 초기화
```js
// 🔴 dev 더블 마운트로 두 번 실행
useEffect(() => { loadDataFromLocalStorage(); checkAuthToken(); }, []);

// ✅ guard
let didInit = false;
function App() {
  useEffect(() => {
    if (!didInit) { didInit = true; loadDataFromLocalStorage(); checkAuthToken(); }
  }, []);
}

// ✅ 모듈 레벨 (가장 깔끔)
if (typeof window !== 'undefined') { checkAuthToken(); loadDataFromLocalStorage(); }
```

### 9. 부모에 state 변경 통지
```js
// 🔴
useEffect(() => onChange(isOn), [isOn, onChange]);

// ✅ 같은 핸들러에서 둘 다 갱신
function updateToggle(next) { setIsOn(next); onChange(next); }
```
또는 fully controlled로 부모가 state 소유.

### 10. 부모로 데이터 전달
```js
// 🔴 자식 Effect → 부모 setter
function Child({ onFetched }) {
  const data = useSomeAPI();
  useEffect(() => data && onFetched(data), [data, onFetched]);
}
// ✅ 부모가 fetch, 자식엔 props
function Parent() { const data = useSomeAPI(); return <Child data={data} />; }
```

### 11. 외부 store 구독 → useSyncExternalStore
```js
// 🔴 수동 subscribe in Effect
useEffect(() => {
  function update() { setIsOnline(navigator.onLine); }
  window.addEventListener('online', update); window.addEventListener('offline', update);
  return () => { /* unbind */ };
}, []);

// ✅ useSyncExternalStore
function subscribe(cb) { window.addEventListener('online', cb); window.addEventListener('offline', cb); return () => {/* */}; }
function useOnlineStatus() {
  return useSyncExternalStore(subscribe, () => navigator.onLine, () => true);
}
```

### 12. 데이터 fetch (race condition)
```js
// 🔴 응답 순서 어긋나면 stale 데이터 표시
useEffect(() => { fetchResults(query, page).then(setResults); }, [query, page]);

// ✅ ignore flag
useEffect(() => {
  let ignore = false;
  fetchResults(query, page).then(json => { if (!ignore) setResults(json); });
  return () => { ignore = true; };
}, [query, page]);

// ✅ Custom Hook으로 추출
function useData(url) { /* 동일 패턴 캡슐화 */ }
```

## 결정 트리
- **render 중 계산 가능?** → state X, Effect X
- **비싼 계산?** → useMemo
- **사용자 인터랙션 결과?** → 핸들러
- **컴포넌트 표시 결과?** → Effect (외부 시스템 동기화일 때만)
- **prop 변경 시 리셋?** → key prop
- **외부 store?** → useSyncExternalStore

## Recap
- 렌더 중 계산되는 값을 Effect로 옮기지 마라
- 비싼 계산은 useMemo
- 컴포넌트 전체 리셋은 key
- 이벤트 트리거 로직은 핸들러
- 다중 Effect 체인은 한 핸들러로 합쳐라
- 외부 store는 useSyncExternalStore
- fetch는 cleanup ignore 패턴 / Custom Hook 추출
