---
marp: true
theme: default
paginate: true
footer: "LO-S9.1"
style: |
  section { font-size: 26px; }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  code { font-size: 20px; }
  pre { line-height: 1.35; }
  .diag { color: #b91c1c; font-weight: 600; }
  .rx { color: #047857; font-weight: 600; }
---

<!-- beat: b1 -->

# 안티패턴 진단 클리닉

코드 6개, 어디가 잘못됐나

PR 6개가 들어왔습니다 — 다 돌아갑니다, 그런데 찝찝합니다.
30초 안에 패턴 식별 + 처방 도구까지.

---

<!-- beat: b2 -->

## 진단 프로토콜 3단계

1. **어떤 패턴인가?** — S1~S8 안티패턴 카탈로그에서 매칭
2. **영향도는?** — 사용자 버그 > 성능 누수 > 코드 냄새
3. **수정 난이도는?** — 한 줄 > 컴포넌트 리팩터 > API 경계 변경

두 축으로 매트릭스를 그리면 PR 우선순위가 자동으로 나옵니다.

---

<!-- beat: b3 -->

## 케이스 1·2 — Ref 오용

```js
// Case 1: 모듈 전역 timeout
let timeoutId;
function Search({ query }) {
  clearTimeout(timeoutId);
  timeoutId = setTimeout(() => fetch(query), 300);
}
// Case 2: 렌더 본문에서 ref 읽기
function Form() {
  const inputRef = useRef(null);
  return <p>현재값: {inputRef.current?.value}</p>;
}
```

- **Case 1 진단:** S1 — 인스턴스별 격리할 데이터를 모듈 전역에. <span class="rx">처방: useRef + cleanup</span>
- **Case 2 진단:** S1/S2 — 렌더 중 ref 읽기는 항상 stale. <span class="rx">처방: state로 끌어올리기</span>

---

<!-- beat: b4 -->

## 케이스 3·4 — Effect 오용

```js
// Case 3: derived state를 Effect로
useEffect(() => {
  setFullName(first + ' ' + last);
}, [first, last]);

// Case 4: Effect chain 캐스케이드
useEffect(() => { setB(a + 1) }, [a]);
useEffect(() => { setC(b + 1) }, [b]);
```

- **Case 3 진단:** S4 — 렌더 중 계산이면 충분. <span class="rx">처방: `const fullName = first + ' ' + last`</span>
- **Case 4 진단:** S4 — 한 인터랙션이 3번 렌더. <span class="rx">처방: 단일 핸들러로 합치기</span>

---

<!-- beat: b5 -->

## 케이스 5·6 — Props & Hook 오용

```js
// Case 5: 객체 prop으로 무한 재연결
<ChatRoom options={{ serverUrl, roomId }} />

// Case 6: lifecycle wrapper hook
function useMount(fn) { useEffect(fn, []); }
```

- **Case 5 진단:** S7 — 부모 렌더마다 새 객체, 자식 Effect 매번 재실행. <span class="rx">처방: 원시값으로 분해</span>
- **Case 6 진단:** S8 — Custom Hook은 동기화 의도 표현용, lifecycle 추상화는 deps linter 무력화. <span class="rx">처방: useMount 제거 + 의도 명명</span>

---

<!-- beat: b6 -->

## 우선순위 매트릭스

| 영향도 ↑ / 난이도 → | **낮음** | **중간** |
|---|---|---|
| **높음** | Case 1 (전역 timeout) <br>**오늘 바로** | Case 4 (Effect chain) <br>다음 스프린트 |
| **중간** | — | Case 5 (객체 prop) <br>다음 스프린트 |
| **낮음** | Case 3 (derived) <br>자투리 시간 | Case 2·6 <br>백로그 |

원칙: **영향도가 먼저**, 난이도는 동률일 때만. "쉬운 것부터"의 함정 피하기.

---

<!-- beat: b7 -->

## 정리 — 6개 패턴 → 6개 섹션

- **전역 timeout** → S1 (Ref 격리)
- **렌더 중 ref 읽기** → S1/S2 (타이밍)
- **derived Effect** → S4 (안 써도 되는 Effect)
- **Effect chain** → S4 (캐스케이드)
- **객체 prop 재연결** → S7 (deps 줄이기)
- **useMount wrapper** → S8 (의도 표현)

진단 = **패턴 + 영향도×난이도 + 섹션 도구**. 아픈 것부터 고칩니다.
