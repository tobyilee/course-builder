# 통합 케이스 스터디 — 검색 채팅방을 처음부터 끝까지
> LOs: LO-S9.2, LO-S9.3

## 개요

코스의 마지막 클래스입니다. 망가진 코드를 진단했던 [S9.C1]의 반대 방향 — **0에서 출발해 검색 가능한 채팅방을 단계 빌드** 하며, 매 단계마다 결정 트리(Q1 외부 시스템? Q2 렌더 중 계산? Q3 인터랙션? from [S0.C2])를 따라 어느 escape hatch가 정당한지 정합니다 [slide 1]. 빌드가 끝나면 곧장 review 모드로 전환해, 동료 PR 코멘트 톤으로 모든 결정을 정당화합니다.

## 핵심 개념

5개 빌드 블록 [slide 2]:
1. **메시지 fetch** ([S4.C5] race-safe `useData`) — `let ignore = false; return () => { ignore = true; }` 패턴을 Custom Hook으로 추출
2. **채팅방 재연결** ([S5.C2] roomId reactive + [S6] useEffectEvent로 알림은 비-반응형) — `useChatRoom` Hook으로 묶기
3. **새 메시지 자동 스크롤** ([S2.C2] flushSync + ref) — state 갱신 직후 DOM을 즉시 읽어야 하는 정당한 케이스
4. **다크모드 토글** ([S6] useEffectEvent로 재연결 방지) — theme 변경이 채팅 끊지 않게
5. **온라인 상태 배지** ([S4.C5] useSyncExternalStore 또는 `useOnlineStatus` Hook)

각 블록에서 "왜 이 도구이고 왜 다른 선택지(useMemo, key, useState)는 탈락했나"를 명시적으로 적습니다 [slide 5]. 이게 LO-S9.3의 평가 부분입니다.

## 예시

```jsx
function App() {
  const isOnline = useOnlineStatus();        // [S8] custom hook
  const [theme, setTheme] = useState('dark');
  const [roomId, setRoomId] = useState('general');
  const messages = useData(`/api/${roomId}`); // race-safe fetch

  useChatRoom({                                // 재연결 동기화
    roomId,
    serverUrl,
    onReceiveMessage(m) { playSound(theme); }  // useEffectEvent로 wrap
  });

  return <ChatPanel messages={messages} theme={theme} online={isOnline} />;
}
```
[slide 4] dark mode toggle은 `theme`을 deps에 넣지 않고도 알림에서는 최신 theme을 봅니다 — 재연결 0회.

## 흔한 실수

- **렌더 트리거 없는 값을 state로** ([S1.C1]) — 자동 스크롤용 lastChild 위치 같은 건 ref. 표시되는 것만 state.
- **`useMount`처럼 lifecycle wrapper를 만든다** ([S8.C3]) — 그냥 useEffect를 쓰는 게 더 명확합니다.
- **`onReceiveMessage`를 useEffectEvent로 wrap 안 한다** ([S8.C2]) — 매 렌더 새 함수 → deps 오염 → 매 렌더 재연결 폭발.
- **`useData`의 `ignore` flag 빼먹기** ([S4.C5]) — race condition으로 옛 응답이 새 결과를 덮어씁니다.

## 복습

검색 채팅방 빌드를 통해 8개 sub-chapter([S1~S8])가 어떻게 한 앱에서 만나는지 봤습니다. 각 escape hatch 사용처에는 (a) 어느 섹션 원칙으로 정당화되는가, (b) 어떤 대안이 탈락했는가, (c) 어떤 트레이드오프(가독성·캡슐화·마이그레이션 비용)를 받아들였는가 — 이 세 줄이 PR 코멘트로 따라붙으면 코드 리뷰가 한층 단단해집니다. **코스 끝.** 코드 리뷰와 신규 설계 양쪽에서 같은 언어로 사고합시다.
