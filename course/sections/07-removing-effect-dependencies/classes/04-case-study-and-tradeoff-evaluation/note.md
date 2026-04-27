# 실전 케이스 스터디 — 6 전략 조합 선택과 트레이드오프 평가
> LOs: LO-S7.5

## 개요

[S7.C1~C3]에서 6가지 전략(정적값 외부화 / 객체 inline / updater / useEffectEvent / Effect 분리 / 원시값 분해)을 하나씩 봤다면, 이번엔 한 케이스 위에 **두세 개를 동시에 적용** 하는 평가형 사고를 훈련합니다 [slide 1]. "재연결이 너무 많다"는 ChatRoom 환자를 받아, 어느 조합이 가독성·캡슐화·마이그레이션 비용 사이의 균형을 가장 잘 잡는지 PR 리뷰하듯 토론합니다.

## 핵심 개념

전략 선택은 알고리즘이 아니라 **트레이드오프** 입니다 [slide 5]. 같은 문제도 팀 컨벤션, 함수형 라이브러리 사용 여부, 마이그레이션 비용에 따라 답이 달라집니다. 평가의 3축:

- **가독성**: 콜사이트가 무엇을 하는지 5초 안에 보이는가? (`updater` 함수는 짧지만, `useEffectEvent` 추출은 의도가 분명한 대신 호출 스택이 한 단계 깊어집니다.)
- **캡슐화**: 같은 결정을 다른 컴포넌트가 반복할 일이 있나? 그렇다면 [S8]에서 만날 Custom Hook으로 가는 다리.
- **마이그레이션 비용**: 기존 호출자에게 미치는 변경 폭. 객체 prop을 원시값으로 분해하면 호출자 시그니처가 바뀝니다.

## 예시

ChatRoom Before:
```js
function ChatRoom({ options, theme }) {
  useEffect(() => {
    const c = createConnection(options);
    c.on('message', () => playSound(theme));
    c.connect();
    return () => c.disconnect();
  }, [options, theme]); // options = 매 렌더 새 객체, theme = 토글마다 재연결
}
```
After (전략 3 + 4 + 6 조합) [slide 4]:
```js
function ChatRoom({ roomId, serverUrl, theme }) {
  const onMessage = useEffectEvent(() => playSound(theme));
  useEffect(() => {
    const c = createConnection({ roomId, serverUrl });
    c.on('message', () => onMessage());
    c.connect();
    return () => c.disconnect();
  }, [roomId, serverUrl]);
}
```
객체 prop 분해(전략 6) + useEffectEvent(전략 4) + 부모도 원시값으로 props 전달 — 세 가지가 한 환자에 동시 들어갔습니다.

## 흔한 실수

- **모든 함정을 useEffectEvent로 덮는다**: 가장 강력해 보이지만 _실험적 API_ 라는 점, 그리고 다른 컴포넌트로 전달이 안 된다는 한계가 곧 다가옵니다 ([S6.C3]).
- **객체 prop을 그대로 둔 채 inline만 한다**: Effect 안에서 객체를 만들어도 부모가 매 렌더 같은 reference를 새로 넘기면 결국 deps에 그 객체가 들어가는 한 같은 문제가 반복됩니다.
- **분리하면 가독성이 떨어질 거라 가정**: 두 개의 짧은 Effect가 한 개의 긴 Effect보다 거의 항상 읽기 좋습니다 ([S5.C3]).

## 복습

문제 → 6 전략 매핑표 [slide 7]: deps 너무 많음 → 1+2 / 무한 루프 → 3 / 읽기만 → 4 / 매 렌더 재생성 → 2+6 / 여러 동기화 → 5 / suppress 유혹 → 늘 1·2·4 중 하나. 다음 섹션 [S8]에서는 이런 결정을 한 번 잘 만들어 두면 여러 컴포넌트가 재사용할 수 있다는 — Custom Hook 추출의 진짜 가치를 다룹니다.
