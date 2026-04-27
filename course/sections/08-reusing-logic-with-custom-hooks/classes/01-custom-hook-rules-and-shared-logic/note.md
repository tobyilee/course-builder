# use 접두사와 "로직만 공유" 원칙

> LOs: LO-8.1, LO-8.2

## 개요

Custom Hook은 React가 새로 만든 문법이 아니라, 우리가 이미 쓰는 `useState`·`useEffect`·`useRef`를 **함수로 묶어** 같은 로직을 여러 컴포넌트에서 다시 쓰게 해주는 관용구입니다 [slide 1]. 이 클래스에서는 "왜 이름이 `use`로 시작해야 하는가", "Custom Hook이 정말 공유하는 것은 무엇인가" 두 질문에 답합니다. 결론을 먼저 말하면 — Custom Hook은 **state를 공유하지 않습니다. 상태 저장 로직(stateful logic)만 공유**합니다 [S0.C1].

## 핵심 개념

### 1. `use` 접두사 = Hook 호출 가능 신호

함수 이름이 `use`로 시작하면 React와 린터는 그 함수를 **Hook으로 간주**합니다 [slide 2]. 이 규칙은 단순한 컨벤션이 아니라 두 가지 보장을 줍니다.

- **린터가 Rules of Hooks를 검사**: 조건문·반복문 안에서 호출되는지, 컴포넌트나 다른 Hook 안에서만 호출되는지를 검사할 수 있어요.
- **읽는 사람의 멘탈모델**: `useOnlineStatus()`라는 이름을 보면, 우리는 즉시 "내부에 `useState`/`useEffect`가 있을 수 있고, 매 렌더마다 호출되어야 한다"는 계약을 떠올립니다.

반대로 Hook을 **하나도 호출하지 않는** 함수에 `use` 접두사를 붙이면 안 됩니다. 예컨대 `useFormatDate(date)`처럼 단순 변환만 하는 함수는 그냥 `formatDate(date)`로 두세요 [slide 3]. 접두사를 잘못 붙이면 린터가 호출 위치 규칙을 강제해 컴포넌트 외부 호출이 막히고, 협업자에게도 잘못된 신호를 줍니다.

### 2. 공유되는 것은 "로직"이지 "state"가 아니다

같은 Custom Hook을 두 컴포넌트가 호출해도, 각 호출은 **독립된 state 인스턴스**를 만듭니다 [slide 4]. `const status = useOnlineStatus()`를 A·B 컴포넌트가 각각 부르면, 내부의 `useState`도 두 벌이 생깁니다. 두 컴포넌트 사이에서 값을 동기화하려면 그것은 Custom Hook의 일이 아니라 **state 끌어올리기(lifting)** 또는 Context의 일입니다.

이 차이를 흐리는 가장 흔한 실수가 "Custom Hook을 만들면 자동으로 전역 상태가 된다"는 오해예요. Custom Hook이 공유하는 것은 어디까지나 `useEffect`에 무엇을 구독할지, `useState`에 어떤 초기값을 줄지 같은 **재사용 가능한 호출 패턴**입니다.

## 예시

온라인/오프라인 상태를 알려주는 Hook을 분리해 봅시다.

```tsx
// useOnlineStatus.ts
import { useState, useEffect } from 'react';

export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener('online', on);
    window.addEventListener('offline', off);
    return () => {
      window.removeEventListener('online', on);
      window.removeEventListener('offline', off);
    };
  }, []);
  return isOnline;
}
```

이제 두 컴포넌트가 자유롭게 같은 로직을 씁니다.

```tsx
function StatusBar() {
  const isOnline = useOnlineStatus();           // 인스턴스 1
  return <h1>{isOnline ? '✅ Online' : '❌ Offline'}</h1>;
}

function SaveButton() {
  const isOnline = useOnlineStatus();           // 인스턴스 2 — 별도 state
  return <button disabled={!isOnline}>Save</button>;
}
```

`StatusBar`와 `SaveButton`은 같은 함수를 호출했지만 각자 자기 `useState`를 갖습니다. 우연히 같은 시점에 같은 값을 보이는 이유는, 둘 다 **같은 외부 시스템(window)** 을 구독했기 때문이지, Hook이 state를 공유했기 때문이 아닙니다 [slide 5].

## 흔한 실수

- **"Custom Hook을 쓰면 state가 공유된다"는 오해**: 호출 횟수만큼 인스턴스가 생깁니다. 진짜 공유가 필요하면 lifting/Context를 쓰세요.
- **Hook을 호출하지 않으면서 `use` 접두사 사용**: `useFormatDate`, `useCalculateTotal` 같은 순수 함수는 접두사를 빼야 합니다. 반대로 내부에서 `useState`/`useEffect`를 부른다면 반드시 `use`로 시작하세요 [slide 3].

## 복습

`use` 접두사는 "이 함수는 Hook이고 Rules of Hooks를 따른다"는 계약 신호이며, Custom Hook은 state가 아니라 **상태 저장 로직만** 공유합니다. 다음 클래스에서는 이 원칙 위에서 실제 Hook을 어떻게 설계하는지 — 특히 `useChatRoom`에서 콜백을 `useEffectEvent`로 감싸는 패턴 — 을 다룹니다 [S8.C2].
