---
marp: true
theme: default
paginate: true
footer: "LO-S4.4"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  blockquote { color: #555; border-left: 4px solid #888; }
---

<!-- beat: b1 -->

# 새로고침했더니 또 떴다

### 인터랙션 vs 표시 — 핸들러로 옮겨야 할 6가지

장바구니에 담을 때만 떠야 할 알림이 페이지 새로고침에서도 또 떴다.

> 원인: Effect가 *"product가 변하면"* 발화하기 때문.

---

<!-- beat: b2 -->
<!-- _footer: "LO-S4.4" -->

## 핵심 분기 질문 하나

- *"이 코드는 **왜** 실행돼야 하는가?"*
  - **사용자가 클릭했기 때문에** → 핸들러
  - **컴포넌트가 표시되었기 때문에** → Effect (외부 시스템 동기화일 때만)
- 안티패턴 #5~#10은 모두 **전자**인데 후자처럼 Effect에 들어가 있는 케이스
- 트리거를 잘못 고르면 새로고침·dev 더블 마운트에서 의도 밖 발화

---

<!-- beat: b3 -->
<!-- _footer: "LO-S4.4" -->

## #5 핸들러 간 로직 공유

```tsx
// Before — Effect가 product 변경마다 발화
useEffect(() => {
  if (product.isInCart) showNotification(`Added ${product.name}!`);
}, [product]);

// After — 공유 함수를 만들어 두 핸들러에서 호출
function buyProduct() {
  addToCart(product);
  showNotification(`Added ${product.name}!`);
}
function handleBuyClick()   { buyProduct(); }
function handleCheckoutClick() { buyProduct(); navigateTo('/checkout'); }
```

> 트리거가 클릭이면 **그 클릭 안에서** 모두 처리.

---

<!-- beat: b4 -->
<!-- _footer: "LO-S4.4" -->

## #6 POST — 분석 로깅 vs 폼 제출

- **분석 / 방문 로깅** = "컴포넌트가 표시됐기 때문"
  → `useEffect(() => post('/analytics', ...), [])` (mount-only)
- **폼 제출** = "사용자가 Submit 눌렀기 때문"
  → `handleSubmit` 핸들러 안에서 직접 `post(...)`
- 같은 `fetch`도 **트리거가 다르면 위치가 다르다**
- 헷갈릴 때 한 문장: *"이 POST는 표시 결과인가, 클릭 결과인가?"*

---

<!-- beat: b5 -->
<!-- _footer: "LO-S4.4" -->

## #7 계산 체인 — 캐스케이딩 재렌더

```tsx
// Before — Effect 3개로 chain, 한 인터랙션이 3번 렌더
useEffect(() => { setGold(computeGold(card)); }, [card]);
useEffect(() => { setRound(computeRound(gold)); }, [gold]);
useEffect(() => { setIsGameOver(check(round)); }, [round]);

// After — 한 핸들러에 모으기, 1회 렌더
function handlePlaceCard(nextCard) {
  const nextGold  = computeGold(nextCard);
  const nextRound = computeRound(nextGold);
  setCard(nextCard);
  setGold(nextGold);
  setRound(nextRound);
  setIsGameOver(check(nextRound));
}
```

---

<!-- beat: b6 -->
<!-- _footer: "LO-S4.4" -->

## #8 앱 초기화 — 두 번 실행 문제

- 증상: `useEffect(() => { loadFromStorage(); checkAuth(); }, [])`
  → dev Strict Mode에서 **두 번** 실행 → 토큰 더블 검사 등 부작용
- **해결 1**: `didInit` guard
  ```tsx
  let didInit = false;
  if (!didInit) { didInit = true; loadFromStorage(); checkAuth(); }
  ```
- **해결 2 (가장 깔끔)**: 모듈 레벨로 빼기
  → "컴포넌트와 무관한 일은 컴포넌트 밖으로"

---

<!-- beat: b7 -->
<!-- _footer: "LO-S4.4" -->

## #9·#10 부모 통지 / 부모로 데이터 전달

```tsx
// #9 Before — onChange를 Effect로
useEffect(() => { onChange(isOn); }, [isOn, onChange]);

// #9 After — 같은 핸들러에서 둘 다
function updateToggle(next) {
  setIsOn(next);
  onChange(next);
}

// #10 — 자식이 fetch해 onFetched로 부모에 올리는 우회 패턴
//   → 부모가 직접 useSomeAPI()로 가져와 prop으로 내려보낸다
//   → 또는 fully controlled로 부모가 state 소유
```

> state 흐름은 **상향 콜백 + 동기 호출**이 명료하다.

---

<!-- beat: b8 -->
<!-- _footer: "LO-S4.4" -->

## 잠깐 — 둘 다 어디로?

- 시나리오: *"메뉴 항목을 클릭하면 라우트를 바꾸고 분석 이벤트를 보낸다"*
- **라우트 변경** = 클릭 트리거 → 핸들러
- **분석 로깅** = 클릭 트리거 → 같은 핸들러에서 함께 호출
  - (만약 페이지 표시 기반이라면 mount-only Effect)
- 결정 규칙: *"트리거가 같으면 같은 자리"*

---

<!-- beat: b9 -->
<!-- _footer: "LO-S4.4" -->

## 정리 — Q3 가지 채우기

- 분기 질문 하나: **클릭 때문인가, 표시 때문인가**
- #5~#10은 전부 **클릭 때문** → 핸들러로 모은다
- 체인은 **합치고**, 초기화는 **모듈 레벨**로, 통지는 **같은 핸들러**에서
- 다음: 외부 통합 — `useSyncExternalStore` · fetch race (Q5)
