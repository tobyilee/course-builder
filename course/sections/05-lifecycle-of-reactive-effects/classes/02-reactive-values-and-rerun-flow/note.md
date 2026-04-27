# Reactive vs Non-reactive 값 — Object.is로 판정되는 재실행 흐름
> LOs: LO-S5.2, LO-S5.3

## 개요

[S5.C1]에서 "각 렌더가 자기 closure를 가진다"는 모델을 세웠다면, 이번엔 그 closure 안에서 쓰이는 값들을 **두 부류** 로 가르는 기준을 잡습니다. Effect의 deps 배열에 무엇이 들어가야 하느냐는 결국 "어떤 식별자가 reactive인가"라는 단 하나의 질문으로 환원됩니다 [slide 1]. 그리고 React가 그 deps 배열을 어떻게 비교해 cleanup→재실행을 결정하는지 [slide 6] 한 컷씩 따라가면, 빈 `[]` 의 진짜 의미도 같이 잡힙니다.

## 핵심 개념

**Reactive** = props, state, 그리고 컴포넌트 본문에서 그것들로부터 파생된 변수 — 매 렌더에서 다시 계산되고, 렌더마다 달라질 수 있는 값들 [slide 2]. **Non-reactive** = 컴포넌트 밖에서 선언된 모듈 상수, `ref.current`, `location.pathname` 같은 외부 mutable 글로벌, 컴포넌트 밖에서 정의된 함수 — 이들은 React의 데이터 흐름 바깥에 있어 React가 변화를 추적할 수 없습니다.

deps 배열의 진짜 규칙은 "linter가 시키니까"가 아니라 **"reactive 값을 적으면 React가 Object.is로 비교해 cleanup→재실행을 일으킨다"** 입니다 [slide 4]. `Object.is(prev, next)`가 `false`이면 동기화를 다시 합니다. 빈 `[]` 는 "이 Effect는 어떤 reactive 값도 안 읽으니 재동기화가 필요 없다"는 **주장** 이지, "한 번만 실행"이라는 의도가 아닙니다 [slide 8].

## 예시

```js
const serverUrl = 'https://localhost:1234';   // 모듈 상수 — non-reactive
function ChatRoom({ roomId }) {                // prop — reactive
  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.connect();
    return () => c.disconnect();
  }, [roomId]); // serverUrl 생략 OK
}
```
roomId가 바뀌면 React는 `Object.is('general','travel')`을 계산하고 → false → cleanup → 본문 재실행 → 새 closure가 새 roomId 캡처 [slide 6]. serverUrl을 `useState`로 바꾸는 순간 reactive가 되어 deps에 합류해야 합니다.

## 흔한 실수

- **`ref.current`를 deps에 넣는다**: ref는 mutation이 React에 보고되지 않으므로 deps로서 의미가 없습니다 — Object.is가 변화를 못 읽습니다.
- **외부 mutable global을 deps에 넣는다**: `location.pathname`, 임의의 가변 객체는 React가 추적하지 않으므로 deps에 넣어도 재실행 신호가 안 옵니다 — 필요하면 `useSyncExternalStore` ([S4.C5]).
- **빈 `[]` 를 "한 번만"으로 오해한다**: 사실은 "이 Effect는 reactive 값을 안 읽는다"는 선언이라 reactive 값을 몰래 읽고 있으면 거짓말이 됩니다.

## 복습

Reactive(props/state/derived) → deps에 / Non-reactive(상수/ref/외부 mutable) → 생략 OK. React는 Object.is로 비교해 재실행을 정한다. `[]` 는 "재동기화 불필요" 주장이다. 다음 클래스 [S5.C3]에서는 이 분류로도 풀리지 않는 회색 지대 — exhaustive-deps 경고를 어떻게 코드 변경으로 풀지 — 를 다룹니다.
