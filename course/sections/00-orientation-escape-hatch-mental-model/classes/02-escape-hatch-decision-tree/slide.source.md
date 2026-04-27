---
marp: true
theme: default
paginate: true
footer: "LO-S0.2"
style: |
  section { font-size: 28px; }
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  code { font-size: 22px; }
  blockquote { color: #555; border-left: 4px solid #888; }
---

<!-- beat: b1 -->

# 결정 트리

### 지금 이 코드, Escape Hatch가 정말 필요한가?

PR 리뷰에서 `useEffect`를 보고 망설이는 순간 — **3개 질문**으로 끝낸다.

> 이 트리가 앞으로 S1~S9를 항해하는 나침반이다.

---

<!-- beat: b2 -->
<!-- _footer: "LO-S0.2" -->

## Q1 — 외부 시스템이 끼어 있는가?

- **외부 시스템** = 서버, 타이머, DOM 노드, 서드파티 라이브러리
- **Yes** → Effect(연결/해제) 또는 ref(인스턴스 보관)로 진입 → **여기서 멈춤**
- **No** → Q2로
- 핵심 정의: *"리렌더가 끝나도 React가 정리해주지 않는 모든 것"*

---

<!-- beat: b3 -->
<!-- _footer: "LO-S0.2" -->

## Q2 — 렌더 중 계산만으로 충분한가?

- props/state로부터 값을 **derive**할 수 있나?
- **Yes** → render 중 계산 또는 `useMemo`. **Effect 절대 금지** (S4 핵심 안티패턴)
- **No** → Q3로

```tsx
// 렌더 중에 그냥 계산하세요
const fullName = `${firstName} ${lastName}`;
const filtered = items.filter(i => i.name.includes(query));
```

---

<!-- beat: b4 -->
<!-- _footer: "LO-S0.2" -->

## Q3 — 사용자 인터랙션의 결과인가?

- 클릭·입력·제출 같은 이벤트가 직접 trigger했나?
- **Yes** → **event handler**. `useEffect`로 우회하지 말 것 (S4)
- **No**이면서 Q1·Q2도 모두 No → 그제야 진짜 Effect 후보 (다시 의심)
- 순서가 중요: **외부 시스템 → 렌더 계산 → 인터랙션**

---

<!-- beat: b5 -->
<!-- _footer: "LO-S0.2" -->

## 4개 시나리오에 적용하기

| 시나리오 | Q1 | Q2 | 결론 |
|---|---|---|---|
| 검색어로 items 필터링 | No | Yes | **render 중 계산** |
| 첫 input에 focus | Yes | — | **ref + Effect** |
| roomId 바뀌면 채팅 재연결 | Yes | — | **useEffect + cleanup** |
| setTimeout ID 보관 | Yes | — | **useRef** |

---

<!-- beat: b6 -->
<!-- _footer: "LO-S0.2" -->

## 같이 풀어보기 — 토스트 3초 자동 닫기

> "폼 제출 후 성공 토스트 띄우기 + 3초 후 자동 닫기"

- **Q1**: 외부 시스템? — 타이머가 외부 → **Yes**
- **띄우기**: 폼 핸들러에서 직접 (인터랙션 결과)
- **3초 닫기**: 타이머 ID는 ref에 보관, 필요 시 Effect cleanup
- 포인트: *한 기능 안에서도 부분별로 트리를 따로 적용*

---

<!-- beat: b7 -->
<!-- _footer: "LO-S0.2" -->

## 코스 로드맵 — 트리 위에 매핑

- **S1~S2**: *Refs 잎* 깊이 파기 — 값 보관(S1), DOM ref(S2)
- **S3~S7**: *Effect 잎* 깊이 파기
  - 동기화 모델(S3) → 안티패턴 12종(S4) → 라이프사이클(S5)
  - useEffectEvent(S6) → deps 줄이기(S7)
- **S8~S9**: 재사용/통합 — Custom Hook(S8), 통합 케이스(S9)

---

<!-- beat: b8 -->
<!-- _footer: "LO-S0.2" -->

## 정리 — 3개 질문, 4개 잎

- **Q1** 외부 시스템? → Effect / Ref
- **Q2** 렌더 중 계산? → render 계산 / `useMemo`
- **Q3** 인터랙션? → event handler
- 셋 다 No → 그제야 *진짜 Effect* 후보
- 다음 시간 (S1) → **Refs 잎**부터 깊이 들어간다
