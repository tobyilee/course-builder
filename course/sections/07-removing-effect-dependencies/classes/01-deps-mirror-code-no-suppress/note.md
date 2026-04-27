# Suppress 금지 — 정적 값은 Effect 밖으로

> LOs: LO-7.1 (린터를 끄지 않고 의존성을 줄이는 사고 절차를 적용한다), LO-7.2 (렌더 동안 변하지 않는 값을 컴포넌트 밖으로 옮겨 의존성에서 제거한다)

## 개요

`react-hooks/exhaustive-deps` 경고가 뜰 때 가장 빠른 해결은 `// eslint-disable-next-line` 한 줄입니다. 그리고 가장 비싼 해결이기도 합니다 [slide 1]. Effect의 의존성 배열은 "이 값이 바뀌면 동기화를 다시 해라"라는 계약인데, suppress는 그 계약을 거짓말로 만들어 버립니다. 이 클래스에서는 의존성을 **속이지 않고 줄이는 첫 번째 전략** — 애초에 reactive가 아닌 값을 컴포넌트 밖으로 빼내기 — 를 다룹니다. S5에서 배운 "매 렌더가 자체 closure를 갖는다" 모델([S5.C1])과 S6의 useEffectEvent([S6.C1])가 이번 사고의 토대입니다.

## 핵심 개념

**왜 suppress는 거짓말인가.** linter는 Effect 본문이 사용하는 모든 reactive 값을 의존성에 넣으라고 강제합니다. 의존성을 빠뜨리면 stale closure가 만들어져, 화면에 보이는 state와 Effect 안에서 보이는 state가 어긋납니다 [slide 2]. suppress는 이 어긋남을 "잠시" 숨기지만, 다른 누가 코드를 만질 때 폭탄으로 돌아옵니다.

**의존성을 진짜로 줄이는 사고 절차.** 의존성을 줄이고 싶다면 의존성 배열이 아니라 **코드 자체**를 바꿉니다. 절차는 단순합니다 [slide 3].

1. 이 값이 진짜로 reactive인가? (props, state, 컴포넌트 안에서 만든 값만 reactive)
2. reactive가 아니라면 컴포넌트 밖으로 옮긴다.
3. reactive지만 동기화 트리거가 되면 안 된다면 다른 전략(updater, useEffectEvent, Effect 분리, 객체 분해)을 본다.

이번 클래스는 1·2번에 집중합니다.

**정적 값 외부화.** `const ROOM_OPTIONS = { serverUrl: 'https://...' }`처럼 렌더와 무관한 상수, 순수 함수, 외부 라이브러리 인스턴스는 컴포넌트 함수 **바깥**에 선언합니다. 그러면 linter는 더 이상 그 값을 reactive로 보지 않고, 의존성 배열에서 빠집니다 [slide 4]. 핵심은 "값이 바뀌어도 Effect가 다시 실행되면 안 되는 값인가?"라는 질문입니다. 답이 '예'라면 외부화 후보입니다.

## 예시

채팅방 연결 Effect를 보겠습니다.

```tsx
// Before — serverUrl이 의존성에 들어가야 한다고 linter가 경고
function ChatRoom({ roomId }: { roomId: string }) {
  const serverUrl = 'https://chat.example.com';
  useEffect(() => {
    const conn = createConnection(serverUrl, roomId);
    conn.connect();
    return () => conn.disconnect();
  }, [roomId, serverUrl]); // serverUrl은 영원히 안 바뀌는데도 의존성
}
```

`serverUrl`은 렌더마다 같은 문자열이지만 컴포넌트 *안에서* 선언됐기 때문에 React 입장에선 reactive입니다. 외부로 옮기면 깔끔하게 사라집니다.

```tsx
// After — 외부화로 의존성에서 제거
const SERVER_URL = 'https://chat.example.com';

function ChatRoom({ roomId }: { roomId: string }) {
  useEffect(() => {
    const conn = createConnection(SERVER_URL, roomId);
    conn.connect();
    return () => conn.disconnect();
  }, [roomId]); // suppress 없이도 정직한 의존성
}
```

같은 원리가 `function formatLog(...)`, `const validator = new Validator()` 같은 헬퍼에도 적용됩니다.

## 흔한 실수

**린터를 suppress해서 "해결"하기.** `// eslint-disable-next-line react-hooks/exhaustive-deps`는 거의 항상 버그를 미래로 미루는 행위입니다. 의존성에서 뭔가를 빼고 싶다면 코드를 바꿔야지, 경고를 끄면 안 됩니다 [slide 5]. 정당한 경우는 극히 드뭅니다 — Effect 내부 ref만 쓰는 등 진짜로 reactive 의존성이 0인 케이스 정도.

**컴포넌트 안에서 매번 새로 만든 "상수".** `const options = { ... }`를 함수 본문에 두면 매 렌더 새 객체가 됩니다. 외부화하지 않으면 정적인 듯해도 reactive입니다. 다음 클래스([S7.C2])에서 이 객체 문제를 본격적으로 다룹니다.

## 복습

- 의존성 경고는 끄지 말고 **코드를 바꿔** 해결합니다.
- 렌더에 의존하지 않는 값은 컴포넌트 밖에 선언해 reactive에서 빼냅니다.
- 다음 단계는 매 렌더 새로 만들어지는 객체·함수 의존성을 다루는 것 — [S7.C2]에서 이어집니다.
