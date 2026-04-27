# Event와 Effect 가르기 — "왜 이 코드가 실행돼야 하나?"

> LOs: LO-6.1 (Event handler와 Effect를 "왜 실행되는가?" 기준으로 구분한다), LO-6.2 (reactive value의 정의를 사용해 코드 위치를 결정한다)

## 개요

채팅방 컴포넌트가 있다고 가정해 봅시다. 사용자가 **메시지 전송 버튼을 누르는 순간** `sendMessage()`가 실행돼야 하고, **roomId가 바뀔 때마다** 채팅 서버에 다시 connect 해야 합니다. 둘 다 "어떤 일에 반응한다"는 점은 같은데, 하나는 `onClick`에 두고 하나는 `useEffect`에 둡니다. 왜 그럴까요? 이 클래스는 그 결정 근거를 한 문장으로 정리합니다 [slide 2]. 답을 미리 말하면 — **"왜 이 코드가 실행돼야 하는가?"** 라는 질문에 답하는 주체가 다르기 때문입니다. 사용자면 event, 컴포넌트의 화면-상태 동기화면 effect입니다 [S5.C1 참고].

## 핵심 개념

**Event handler는 "특정 상호작용에 반응"해서 실행됩니다.** 사용자가 버튼을 클릭하든, 폼을 submit 하든, **그 행위가 일어났을 때만** 코드가 돕니다. 같은 props/state라도 사용자가 다시 누르지 않으면 다시 실행되지 않죠. 즉 event handler 안의 로직은 **non-reactive** — props·state가 변해도 자동으로 재실행되지 않습니다 [slide 4].

**Effect는 "동기화가 필요할 때마다" 실행됩니다.** roomId가 'general'에서 'travel'로 바뀌면 우리는 사용자에게 묻지 않고도 새 방에 connect 해야 합니다. 컴포넌트가 화면에 그리고 있는 reactive value(props, state, 그로부터 파생된 값)와 외부 시스템 상태가 어긋나면, React가 알아서 effect body를 재실행해 맞춥니다 [slide 5].

이 둘을 가르는 결정 질문은 단 하나입니다: **"이 코드는 사용자가 무엇을 했기 때문에 실행되는가, 아니면 화면이 어떤 값과 동기화되어야 하기 때문에 실행되는가?"** 전자는 핸들러로, 후자는 effect로 갑니다 [slide 6]. 이 질문이 중요한 이유는 reactive value의 변경에 반응할지 말지를 가르기 때문입니다. 핸들러에 잘못 넣으면 동기화가 끊기고, effect에 잘못 넣으면 사용자가 누르지도 않은 액션이 자동으로 발사됩니다.

## 예시

쇼핑 페이지에서 **상품을 장바구니에 담는 버튼**과 **장바구니 개수를 분석 서버에 동기화**하는 두 가지 일을 비교해 봅시다.

```tsx
function Product({ product }) {
  const [count, setCount] = useState(0);

  // Event: 사용자가 클릭했기 때문에만 실행된다 (non-reactive)
  function handleBuyClick() {
    addToCart(product);                 // count, product 둘 다 그 시점 값으로 OK
    showNotification(`${product.name} 담음`);
  }

  // Effect: count가 바뀌면 외부 시스템(analytics)과 다시 동기화한다 (reactive)
  useEffect(() => {
    logCartCount(count);
  }, [count]);

  return <button onClick={handleBuyClick}>구매</button>;
}
```

`handleBuyClick`은 `count`나 `product`를 **그 순간의 값**으로 읽으면 충분합니다. 사용자가 다시 누르지 않으면 자동 재실행될 이유가 없죠. 반면 `logCartCount`는 `count`가 변할 때마다 자동으로 다시 보내야 하므로 effect입니다. **같은 함수 호출도 위치에 따라 의미가 달라진다** — 이게 핵심입니다 [slide 6].

## 흔한 실수

**"버튼 클릭 시 fetch도 하니까 effect로 옮겨야지"** 는 함정입니다. fetch가 *클릭의 결과*면 그건 핸들러 안에 있어야 합니다. effect로 옮기는 순간 컴포넌트가 mount 될 때, 또는 의존성이 바뀔 때마다 의도하지 않게 fetch가 발사될 수 있습니다. 결정 질문으로 돌아가세요 — "사용자가 클릭했기 때문에"이지 "어떤 값과 동기화되어야 해서"가 아닙니다 [slide 7].

**"Effect 안의 알림 로직이 reactive 하게 다시 떠서 귀찮다"** 는 다음 클래스의 출발점입니다. 그건 effect 자체가 잘못된 게 아니라, effect 안에 **non-reactive 로직이 섞여 있다**는 신호이며, 그것을 떼어내는 도구가 다음에 나올 `useEffectEvent`입니다 [S6.C2 예고].

## 복습

Event는 "사용자가 했기 때문에", Effect는 "동기화가 필요해서" 실행됩니다. 이 한 문장이 위치 결정의 모든 것입니다. 다음 클래스에서는 effect 안에 잘못 끼어든 non-reactive 조각을 어떻게 분리하는지 봅니다.
