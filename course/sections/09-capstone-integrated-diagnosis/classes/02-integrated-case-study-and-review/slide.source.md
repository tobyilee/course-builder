---
marp: true
theme: default
paginate: true
footer: "LO-S9.2"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  pre { line-height: 1.35; }
  .add { color: #047857; }
  .del { color: #b91c1c; }
---

<!-- beat: b1 -->

# 검색 채팅방, 처음부터 끝까지

통합 케이스 스터디

검색 + 채팅 재연결 + 자동 스크롤 + 다크모드 토글 — 한 화면.
빌드하면서 결정 트리, 끝나면 PR review 톤으로 정당화.

---

<!-- beat: b2 -->
<!-- _footer: "LO-S9.2" -->

## 빌드 로드맵 — 결정 트리 순서

1. **검색 fetch** — 외부 시스템 동기화 (S3)
2. **ChatRoom 연결** — reactive deps + cleanup (S5)
3. **새 메시지 자동 스크롤** — DOM 명령형 (S2 ref + flushSync)
4. **다크모드 토글** — non-reactive 분리 (S6 useEffectEvent)
5. **useChatRoom · useData 추출** — 의도 캡슐화 (S8)

각 블록 빌드 후 즉시 review — "다른 도구는 왜 탈락했나" 한 줄.

---

<!-- beat: b3 -->
<!-- _footer: "LO-S9.2" -->

## 블록 1 — 검색 with race-safe fetch

```js
useEffect(() => {
  let ignore = false;
  fetch(`/search?q=${query}`)
    .then(r => r.json())
    .then(data => { if (!ignore) setResults(data); });
  return () => { ignore = true; };
}, [query]);
```

- **왜 Effect?** 서버 동기화, 인터랙션 결과 아님
- **왜 ignore?** 빠른 타이핑 시 늦은 응답이 새 결과 덮어씀 (S3 race)
- **탈락:** useMemo (비동기 X), onChange (URL 진입에도 fetch 필요)

---

<!-- beat: b4 -->
<!-- _footer: "LO-S9.2" -->

## 블록 2·3 — ChatRoom + 자동 스크롤

```js
useEffect(() => {
  const c = createConnection(serverUrl, roomId);
  c.connect();
  return () => c.disconnect();
}, [serverUrl, roomId]);

// 새 메시지 도착 시
flushSync(() => setMessages(next));
listRef.current.scrollTo({ top: listRef.current.scrollHeight });
```

- **왜 deps에 roomId?** reactive 값 (S5.2), 변하면 cleanup→재실행
- **왜 flushSync?** batching 상태에선 scrollHeight가 stale (S2.3)
- **탈락:** ref guard로 Strict Mode 회피 — unmount 누수, 처방 아님

---

<!-- beat: b5 -->
<!-- _footer: "LO-S9.3" -->

## 블록 4 — 다크모드 토글, 재연결 X

```diff
- useEffect(() => {
-   connect(roomId);
-   showToast(`Connected in ${theme}`);
- }, [roomId, theme]);  // theme 토글마다 재연결 😱

+ const onConnected = useEffectEvent(() => {
+   showToast(`Connected in ${theme}`);
+ });
+ useEffect(() => {
+   connect(roomId);
+   onConnected();
+ }, [roomId]);  // theme 토글에 영향 없음 ✓
```

- **왜 useEffectEvent?** 최신 theme 읽되 reactive 추적 X (S6.2)
- **탈락:** ref 동기화 (보일러플레이트), linter suppress (금지 원칙 S7.1)

---

<!-- beat: b6 -->
<!-- _footer: "LO-S9.3" -->

## 블록 5 — useChatRoom · useData 추출

```js
function useChatRoom({ serverUrl, roomId, onMessage }) {
  const onMsg = useEffectEvent(onMessage);
  useEffect(() => {
    const c = createConnection(serverUrl, roomId);
    c.on('message', m => onMsg(m));
    c.connect();
    return () => c.disconnect();
  }, [serverUrl, roomId]);
}
```

- **reactive는 인자로**, 핸들러는 useEffectEvent로 wrap (S8.3)
- **왜 추출?** 도메인 의미 표현 + 미래 useSyncExternalStore 교체 여지
- **탈락:** useMount 같은 lifecycle wrapper (의도 잃고 deps 죽음, S8.4)

---

<!-- beat: b7 -->
<!-- _footer: "LO-S9.3" -->

## Review 모드 — 동료 PR 코멘트

- **Q: onChange에서 fetch하면?** → query는 표시 중 동기화 (URL/뒤로가기에도 필요), 인터랙션 결과 아님
- **Q: flushSync 없이 scrollTo?** → batching으로 DOM 미반영, scrollHeight stale
- **Q: theme도 deps에 넣고 reconnect 받아들이면?** → 메시지 끊김, 가독성 < 정확성
- **Q: useChatRoom 단일 사용처인데 왜 뺐어?** → 의도 캡슐화 + 테스트 + 미래 교체 여지 (트레이드오프: 약간의 간접)

각 답변에 **"다른 선택지 → 왜 탈락"** — 이게 LO-S9.3 본질.

---

<!-- beat: b8 -->
<!-- _footer: "LO-S9.2" -->

## 코스 졸업 — 한 바퀴 돌았습니다

- **검색** = useData/race (S3) · **채팅** = useChatRoom/재연결 (S5)
- **자동스크롤** = ref + flushSync (S2) · **다크모드** = useEffectEvent (S6)
- 결정 트리는 **모든 줄에** 적용 — 왜 이 도구, 왜 다른 건 탈락, 어떤 트레이드오프

> Escape Hatch는 **마지막 수단**, 그러나 필요할 땐 정확히.

수고하셨습니다.
