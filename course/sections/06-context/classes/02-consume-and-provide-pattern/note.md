# 같은 컴포넌트가 consume + provide — 자동 level 증가 패턴

> LOs: LO-S6.3

## 개요
[S6.C1]의 `Section`은 `<Section level={1}>`처럼 매번 사람이 손으로 level을 적었습니다 [slide 2]. 중첩이 깊어지면 `<Section level={1}><Section level={2}><Section level={3}>...`로 인간이 카운트하는 실수가 생기죠. 이 class의 목표는 **`level` prop을 완전히 제거**하고, `Section` 중첩 깊이만으로 `h1 → h2 → h3`가 자동으로 잡히게 만드는 패턴입니다.

## 핵심 개념
아이디어는 단순합니다: `Section`이 `LevelContext`를 **읽고**(consume), 거기에 +1을 더한 값을 다시 자식들에게 **공급**(provide)합니다 [slide 3]. 한 컴포넌트 안에서 두 역할이 동시에 일어나는 게 핵심입니다.

여기서 작동하는 두 규칙을 분명히 합시다.

- **가장 가까운 Provider 규칙**: 자손이 `useContext(Ctx)`를 부르면 React는 트리를 위로 거슬러 올라가 처음 만난 `<Ctx value=…>`의 값을 읽고 멈춥니다. 즉 `Section` 자신이 만든 Provider는 자기 **자식**이 봅니다 — 자기 자신은 한 단계 위 Provider의 값을 읽죠 [slide 4].
- **여러 context는 서로 독립**: `ThemeContext`와 `LevelContext`가 같은 트리에 공존해도 간섭 없이 각자의 Provider 체인을 가집니다.

이 두 규칙 덕분에 `Section`이 한 번 정의되면 `level` prop은 사라지고, **트리에서의 깊이가 곧 level**이 됩니다. `Heading`은 한 줄도 바꾸지 않습니다 — context의 캡슐화 효과입니다.

## 예시
```js
// Section.js
import { useContext } from 'react';
import { LevelContext } from './LevelContext.js';

export function Section({ children }) {
  const level = useContext(LevelContext); // consume
  return (
    <section>
      <LevelContext value={level + 1}>   {/* provide */}
        {children}
      </LevelContext>
    </section>
  );
}

// Page.js
<Section>
  <Heading>Title</Heading>      {/* h1 */}
  <Section>
    <Heading>Sub</Heading>       {/* h2 */}
    <Section>
      <Heading>SubSub</Heading>  {/* h3 */}
    </Section>
  </Section>
</Section>
```

라이브로 추적해 봅시다 [slide 5]. 최상위 `Section`은 위에 Provider가 없으니 `createContext(0)`의 기본값 `0`을 읽고, `value={0 + 1} = 1`을 자식에게 줍니다 — 그 안의 `Heading`은 `h1`. 두 번째 `Section`은 `1`을 읽고 `2`를 줍니다 — `h2`. 세 번째는 `3` — `h3`. 사람이 카운트하지 않아도 트리 모양이 결과를 결정합니다.

## 흔한 실수
- **`useContext`를 조건/루프 안에서 호출**하기. 자동 증가 패턴이라고 예외가 아닙니다 — `if (someFlag) { const level = useContext(...) }`는 안 됩니다.
- **value로 매 렌더 새 객체 리터럴 넘기기**. 예를 들어 `<Ctx value={{ level, setLevel }}>`처럼 매 렌더 새 객체를 만들면, 부모가 리렌더할 때마다 참조가 바뀌어 모든 consumer가 무조건 재렌더됩니다. 필요하면 `useMemo`로 객체를 안정화하거나 값을 잘게 쪼개 별도 context로 분리하세요. (실제 영향은 프로파일러로 검증 필요)
- **중간에 `<div>`나 다른 wrapper가 끼면 카운트가 끊긴다고 오해**하기. context는 DOM 노드가 아니라 **컴포넌트 트리의 Provider**를 추적하므로 `<div>`는 무관합니다. `Section`이 새 Provider를 만들 때만 level이 증가합니다.

## 복습
`Section`이 `useContext`로 읽고 `+1` 한 값을 다시 Provider로 흘려보내면, 가장 가까운 Provider 규칙 덕분에 깊이가 곧 level이 됩니다. 다음 [S6.C3]에서는 이 강력한 도구를 **언제 쓰지 말아야 하는지** — props/composition 대안과 비교 — 를 다룹니다.
