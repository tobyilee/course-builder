# 결정 트리 — 지금 이 코드, Escape Hatch가 정말 필요한가?

> LOs: LO-S0.2

## 개요

이전 클래스 [S0.C1]에서 'Escape Hatch는 마지막 수단'이라는 자세를 잡았습니다. 그런데 PR 리뷰에서 `useEffect` 코드 한 덩어리를 마주하면 여전히 망설이게 됩니다 — "이건 정말 필요한 건가, 빼도 되는 건가?" 오늘은 그 망설임을 단 **3개 질문**으로 끝내는 결정 트리를 만듭니다 [slide 1]. 이 트리는 앞으로 S1~S9 전체를 항해하는 나침반이 됩니다.

## 핵심 개념

세 질문은 **순서가 중요**합니다 — 외부 시스템 → 렌더 계산 → 인터랙션 순서를 지켜야 정답률이 높습니다.

**Q1. 외부 시스템이 끼어 있는가?** [slide 2] 서버, 타이머, DOM 노드, 서드파티 라이브러리처럼 '리렌더가 끝나도 React가 정리해주지 않는 모든 것'이 외부 시스템입니다. Yes면 Effect 영역(연결/해제) 또는 ref(인스턴스 보관)로 진입하고 거기서 멈춥니다. No면 다음 질문으로.

**Q2. 렌더 중 계산만으로 충분한가?** [slide 3] props/state로부터 값을 derive할 수 있나요? `fullName = firstName + ' ' + lastName`이나 `filteredList = items.filter(...)`처럼요. Yes면 render 중 계산 또는 `useMemo`로 처리하고, **Effect는 절대 금지**입니다 (S4의 핵심 안티패턴). No면 다음 질문.

**Q3. 사용자 인터랙션의 결과인가?** [slide 4] 클릭, 입력, 제출 같은 이벤트가 직접 trigger했다면 event handler가 정답입니다. `useEffect`로 우회하지 마세요. 1·2·3번이 모두 No일 때 비로소 진짜 Effect 후보가 되며, 그때도 한 번 더 의심해보세요.

잎 노드는 4개 — Effect/Ref, 렌더 계산·`useMemo`, handler, (진짜) Effect.

## 예시

네 시나리오에 트리를 적용합니다 [slide 5].

| 시나리오 | Q1 | Q2 | 결론 |
|---|---|---|---|
| ① items 검색어 필터링 결과 | No | Yes | render 중 `filter` |
| ② 페이지 로드 시 첫 input focus | Yes (DOM) | — | ref + Effect |
| ③ roomId 변경 시 채팅 재연결 | Yes (서버) | — | `useEffect` + cleanup |
| ④ setTimeout ID 저장 후 clear | Yes (타이머) | — | `useRef` |

직접 풀어볼 케이스 [slide 6]: **'폼 제출 후 성공 토스트 띄우기 + 3초 후 자동 닫기'**. 한 기능 안에서도 결정 트리를 부분별로 적용합니다.

- 토스트 띄우기: 제출 이벤트의 결과 → Q3에서 handler
- 3초 타이머: 외부 시스템(타이머) → Q1에서 ref에 ID 저장 + cleanup

```tsx
const timerRef = useRef<number | null>(null);
const onSubmit = async () => {
  await save();
  setToastVisible(true);                              // handler
  timerRef.current = window.setTimeout(() => {        // ref 보관
    setToastVisible(false);
  }, 3000);
};
useEffect(() => () => {                                // cleanup
  if (timerRef.current) clearTimeout(timerRef.current);
}, []);
```

## 흔한 실수

**오해 1: "데이터를 derive하려면 `useEffect`로 state를 또 만들어야 한다."** 렌더 중 계산이 가능하다면 그쪽이 항상 정답입니다. Effect로 derive하면 한 박자 늦은 렌더, stale 값, 무한 루프의 씨앗이 됩니다 (S4에서 자세히).

**오해 2: "결정 트리는 한 번만 통과시키면 된다."** 한 함수 안에도 여러 갈래가 동시에 존재합니다. 토스트 예시처럼 '띄우기 → handler', '닫기 → ref + Effect'를 분리해 적용해야 합니다.

## 복습

- 3개 질문 순서: 외부 시스템? → 렌더 중 계산? → 인터랙션 결과?
- 잎 4개: Effect/Ref / render 계산·`useMemo` / handler / (진짜) Effect
- 이 트리가 S1~S9 모든 결정의 출발점 [slide 7] — Refs 잎(S1~S2), Effect 잎(S3~S7), 재사용·통합(S8~S9)
- 다음 시간 [S1]부터 'Refs 잎'을 깊이 들어갑니다
