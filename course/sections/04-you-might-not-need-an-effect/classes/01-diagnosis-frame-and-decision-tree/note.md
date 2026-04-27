# Effect 안 써도 되는 경우 — 진단 프레임과 결정 트리
> LOs: LO-S4.1

## 개요
실제 코드베이스를 열어 보면 `useEffect`로 시작하는 블록의 상당수는 사실 Effect가 아니어도 되는 코드입니다. `firstName`과 `lastName`을 합쳐 `fullName`을 만드는 단순한 일을 굳이 `useState`와 `useEffect`로 동기화한 코드 [slide 1] 를 한 번쯤 본 적이 있을 거예요. 이번 섹션의 출발점은 단 한 문장입니다 — **외부 시스템이 없으면 Effect도 필요 없다.** 이 원칙을 손에 쥐고 12가지 안티패턴을 진단하는 지도를 그려 보겠습니다.

## 핵심 개념
**Effect의 정의를 먼저 다시 못박아 둡시다.** [S3.C1] 에서 살펴봤듯 Effect는 "외부 시스템과의 동기화 escape hatch"입니다. 서버, DOM, 타이머, 브라우저 API처럼 React 트리 바깥의 무언가와 컴포넌트 상태를 맞출 때만 정당화됩니다.

외부 시스템이 없는데 Effect를 쓰면 세 가지 비용이 따라옵니다 [slide 2].

1. **불필요한 추가 렌더** — 렌더 → Effect → setState → 재렌더의 두 번째 사이클이 거의 항상 따라옵니다.
2. **개발 모드 더블 마운트** — Strict Mode에서 Effect는 두 번 실행되도록 설계되어 있어, 멱등하지 않은 코드는 즉시 버그를 드러냅니다.
3. **의존성 트래킹 부담** — 의존성 배열을 채우고 ESLint와 씨름하는 시간이 늘어납니다.

이 비용들을 피하기 위해 12가지 안티패턴을 5개 그룹으로 묶어 진단합니다 [slide 3].

- **그룹 A — Derived state**: #1 props/state 갱신, #2 비싼 계산 캐싱
- **그룹 B — State 리셋/조정**: #3 전체 리셋, #4 부분 조정
- **그룹 C — 인터랙션 vs 표시**: #5 핸들러 공유, #6 POST, #7 체인, #8 초기화, #9 부모 통지, #10 부모로 데이터 전달
- **그룹 D — 외부 통합**: #11 store 구독, #12 fetch race

## 예시
한 장짜리 결정 트리를 5개 질문으로 정리하면 [slide 4] 다음과 같습니다.

```
Q1. render 중 계산 가능?    → 변수 한 줄  (state X, Effect X)
Q2. 비싼 계산?               → useMemo
Q3. 사용자 인터랙션 결과?    → 핸들러
Q4. prop 변경 시 리셋?       → key prop / state-during-render
Q5. 외부 store?              → useSyncExternalStore (마지막에야 비로소 Effect)
```

세 가지 미니 케이스를 이 트리로 흘려보내 봅시다 [slide 5].

```tsx
// Case 1 — Q1에서 종료
const fullName = firstName + ' ' + lastName;

// Case 2 — Q3 핸들러로
function handleSubmit() {
  postOrder(form);
}

// Case 3 — Q5 외부 store
const isOnline = useSyncExternalStore(subscribe, () => navigator.onLine);
```

세 케이스 모두 Effect를 한 줄도 쓰지 않고 끝났습니다. 이게 이번 섹션이 약속하는 풍경이에요.

## 흔한 실수
가장 자주 보이는 함정은 **Effect로 derived value를 보관하는 것**입니다. "fullName을 어딘가에 저장해야 한다"는 무의식적인 가정 때문에 `useState(fullName)`을 만들고, 그걸 `firstName/lastName`과 동기화하려 Effect를 추가하죠. 사실 fullName은 매 렌더마다 즉석에서 계산해도 일관성이 자동으로 유지됩니다 — 저장할 이유가 없습니다. "render는 순수 함수"라는 React 멘탈모델 [S0.C1] 을 떠올리면, 입력이 같으면 출력이 같다는 보장이 이미 우리 편이라는 사실이 보입니다.

## 복습
Effect는 외부 시스템 동기화 전용 도구입니다. 12가지 안티패턴은 5개 그룹과 5개 질문 결정 트리로 정리되며, 다음 4개 클래스 [S4.C2]–[S4.C5] 가 각 가지를 Before/After로 채워 갑니다.
