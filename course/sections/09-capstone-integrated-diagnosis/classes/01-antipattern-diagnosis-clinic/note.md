# 안티패턴 진단 클리닉 — 코드 6개, 어디가 잘못됐나
> LOs: LO-S9.1

## 개요

코스의 마지막에 다다랐습니다. 이번 클래스는 [S1~S8]에서 본 도구를 **거꾸로** 써 봅니다 — 망가진 6개 코드 스니펫을 차례로 받아 "어떤 패턴인가 → 영향도 × 수정 난이도 → 어느 섹션 도구로 고치나"를 30초 안에 답하는 진단 훈련 [slide 1]. 마지막 5분에는 6개 케이스를 영향도/난이도 매트릭스에 배치해 리팩터링 우선순위를 정합니다.

## 핵심 개념

진단 프로토콜 4단계 [slide 2]:
1. **증상 한 줄로 말하기** — "방을 바꿀 때마다 새 메시지가 다른 방에서 들린다" 같은 사용자 관점.
2. **어느 도구가 잘못 쓰였나** — Ref/Effect/Custom Hook 중 어디인지.
3. **어느 섹션 원칙을 어겼나** — S2.4의 "React 관리 DOM 직접 조작" 처럼 명시.
4. **처방 한 줄** — 어느 패턴으로 갈아끼우는지.

6대 안티패턴 [slide 3-5]:
- **전역 timeout 변수** ([S1.C2]) → 인스턴스별 ref
- **렌더 중 ref.current 읽기** ([S1.C1]) → state로 전환
- **derived state Effect** ([S4.C2]) → 렌더 중 계산
- **Effect chain** ([S4.C4]) → 한 핸들러로 통합
- **options 객체 prop으로 인한 무한 재연결** ([S7.C3]) → 원시값 분해 + useEffectEvent
- **useMount lifecycle wrapper** ([S8.C3]) → useEffect 직접

## 예시

```js
// 환자 1: 전역 timeout
let timeoutID;
function DebouncedButton({ onClick }) {
  return <button onClick={() => {
    clearTimeout(timeoutID);
    timeoutID = setTimeout(onClick, 1000);
  }}>Click</button>;
}
```
증상: 두 번째 버튼을 누르면 첫 번째 버튼의 타이머가 취소됨. 도구: Ref 누락. 섹션: [S1.C2]. 처방: `const timeoutRef = useRef(null);` 로 인스턴스별 보관.

매트릭스 활용 [slide 6]: 영향도 높음 + 수정 난이도 낮음 = **즉시 리팩터링** (예: 전역 timeout, useMount). 영향도 낮음 + 난이도 높음 = **다음 sprint** (예: options 객체 prop). 이 우선순위는 PR 리뷰 어디까지 막을지의 기준이 됩니다.

## 흔한 실수

- **모든 패턴을 영향도 동급으로 본다** → 무한 재연결 vs 코드 스타일 격차를 똑같이 막으면 PR 흐름이 멈춥니다.
- **'영향도 낮음'을 무시한다** → useMount 같은 wrapper는 한 번 퍼지면 팀 컨벤션이 됩니다 — 영향도가 시간에 따라 커지는 케이스.
- **수정 난이도를 코드 라인 수로만 잰다** → 진짜 비용은 호출자 마이그레이션 폭과 테스트 회귀 가능성입니다.

## 복습

진단 4단계 → 6대 패턴 → 영향도/난이도 매트릭스로 우선순위. 다음 클래스 [S9.C2]에서는 반대 방향 — 0에서 시작해 검색 채팅방 앱을 코스 결정 트리대로 빌드하며 escape hatch들을 정당하게 조합합니다.
