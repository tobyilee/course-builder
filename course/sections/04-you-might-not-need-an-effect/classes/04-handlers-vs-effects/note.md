# 인터랙션 vs 표시 — 핸들러로 옮겨야 할 6가지
> LOs: LO-S4.4

## 개요
장바구니에 상품을 담았더니 "추가됨!" 알림이 떴습니다. 그런데 페이지를 새로고침했더니 같은 알림이 또 떴어요 [slide 1]. Effect가 "product가 변하면" 발화하도록 작성되어 있어서, 첫 마운트도 "product가 변한 것"으로 본 겁니다. 이번 클래스의 한 줄 질문은 단순합니다 — **"왜 이 코드가 실행돼야 하는가?"**

## 핵심 개념
모든 분기가 한 질문에서 갈립니다 [slide 2].

- "사용자가 **클릭했기 때문에**" 실행되어야 한다 → **핸들러**
- "컴포넌트가 **표시되었기 때문에**" 실행되어야 한다 → **Effect** (그것도 외부 시스템 동기화일 때만)

안티패턴 #5~#10은 모두 전자(클릭)인데 후자(표시)처럼 Effect에 들어가 있는 경우입니다. 여섯 가지를 한 호흡으로 정리해 둡니다.

- **#5 핸들러 간 로직 공유** — 같은 동작을 두 버튼에서 쓰고 싶을 때 Effect로 우회하지 말고 함수로 추출.
- **#6 POST 요청** — 분석/방문 로깅은 Effect(mount-only), 폼 제출은 핸들러. 같은 fetch라도 트리거가 다르면 위치가 다릅니다.
- **#7 계산 체인** — 여러 state를 차례로 갱신하는 Effect 체인을 한 핸들러로 합쳐서 단일 렌더로.
- **#8 앱 초기화** — `useEffect(() => init(), [])` 대신 모듈 레벨 또는 `didInit` guard.
- **#9 부모에 통지** — `useEffect(() => onChange(x), [x])` 대신 같은 핸들러에서 `setX`와 `onChange`를 함께 호출.
- **#10 부모로 데이터 전달** — 자식이 fetch해서 부모에 올려보내는 대신 부모가 직접 가져오거나 fully controlled로.

## 예시
**#5 핸들러 공유** [slide 3]:

```tsx
// After
function buyProduct() {
  addToCart(product);
  showNotification(`Added ${product.name}!`);
}
// <button onClick={buyProduct}>Buy</button>
// <button onClick={buyProduct}>Add to cart</button>
```

**#7 계산 체인** [slide 5]:

```tsx
// After — 한 핸들러에서 직접 계산
function handlePlaceCard(nextCard) {
  setCard(nextCard);
  if (nextCard.gold) {
    if (goldCount < 3) setGoldCount(goldCount + 1);
    else { setGoldCount(0); setRound(round + 1); }
  }
}
```

3번의 캐스케이드 렌더가 1번으로 압축되고, 디버깅도 쉬워집니다.

**#8 앱 초기화** [slide 6]:

```tsx
// 가장 깔끔 — 모듈 레벨
if (typeof window !== 'undefined') {
  checkAuthToken();
  loadDataFromLocalStorage();
}
```

컴포넌트 라이프사이클과 무관한 일은 컴포넌트 밖으로.

**#9 부모 통지** [slide 7]:

```tsx
function updateToggle(next) {
  setIsOn(next);
  onChange(next);
}
```

state가 바뀌었기 "때문에" 통지하는 게 아니라, 사용자가 토글을 눌렀기 "때문에" 통지하는 겁니다. 트리거를 따라가면 자리가 명확해집니다.

## 흔한 실수
이 클래스의 안티패턴들이 공유하는 함정은 **인터랙션 결과를 Effect에서 처리하는 것**입니다. "버튼을 누르면 product 상태가 바뀌고, product가 바뀐 걸 Effect가 감지해서 알림을 띄운다" — 한 단계 우회하는 듯하지만 실은 두 가지를 망칩니다. 첫째, 마운트나 새로고침 같은 "표시" 트리거에도 같은 코드가 발화해 유령 알림을 만듭니다. 둘째, 인과 관계가 흐릿해져 디버깅 시 "이 알림은 누가 띄웠지?"를 추적하기 어렵습니다. **클릭 안에서 일어난 일은 클릭 안에서 끝내세요.** Effect는 외부 시스템 동기화의 자리지, 인터랙션 결과의 자리가 아닙니다.

또 하나 자주 보는 실수는 **앱 초기화를 빈 deps Effect로 두고 dev에서 두 번 실행되는 것을 못 본 척하는 것**입니다. 토큰 검사가 두 번 도는데 운 좋게 멱등하다고 넘기면 언젠가 분석 이벤트 중복이나 인증 충돌이 터집니다. 모듈 레벨 또는 guard로 명시적으로 한 번임을 보장하세요.

## 복습
- 한 가지 질문 — 클릭 때문인가, 표시 때문인가
- #5~#10은 전부 클릭 때문 → **핸들러로 모은다**
- 체인은 합치고, 초기화는 모듈 레벨로, 통지는 같은 핸들러에서
- 다음 클래스 [S4.C5] 에서는 Q5 외부 통합과 종합 결정 트리로 섹션을 닫습니다.
