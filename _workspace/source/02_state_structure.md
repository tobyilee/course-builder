# Source: Choosing the State Structure

## 5가지 원칙

### 1. 관련 state는 묶어라 (Group related)
항상 함께 갱신되는 두 변수는 객체로 합친다.
```js
// before
const [x, setX] = useState(0);
const [y, setY] = useState(0);
// after
const [position, setPosition] = useState({ x: 0, y: 0 });
```
⚠️ Pitfall: 객체 갱신 시 모든 필드 복사 필요 (`setPosition({ ...position, x: 100 })`).

### 2. 모순(contradictions) 회피
```js
// 둘 다 true가 가능 → 모순
const [isSending, setIsSending] = useState(false);
const [isSent, setIsSent] = useState(false);
// status enum으로 단일화
const [status, setStatus] = useState('typing'); // 'typing' | 'sending' | 'sent'
const isSending = status === 'sending';
const isSent = status === 'sent';
```

### 3. 중복(redundant) state 회피
파생 가능한 값은 state로 두지 말고 render 시 계산.
```js
// before — fullName이 redundant
const [fullName, setFullName] = useState('');
// after
const fullName = firstName + ' ' + lastName;
```

#### Don't mirror props in state
```js
// ❌ 부모가 messageColor를 바꿔도 갱신 안 됨
const [color, setColor] = useState(messageColor);
// ✅ prop 직접 사용
const color = messageColor;
// ✅ 의도적 무시는 'initial' 접두사
function Message({ initialColor }) {
  const [color, setColor] = useState(initialColor);
}
```

### 4. 중복(duplication) 회피
객체 자체 대신 id만 저장하고 derive.
```js
// before
const [selectedItem, setSelectedItem] = useState(items[0]); // items 변경 시 동기화 깨짐
// after
const [selectedId, setSelectedId] = useState(0);
const selectedItem = items.find(i => i.id === selectedId);
```

### 5. 깊은 중첩(deep nesting) 평탄화
```js
// before — childPlaces 트리
{ id:0, childPlaces:[{ id:1, childPlaces:[{ id:2, ... }] }] }
// after — DB 정규화 스타일
{
  0: { id:0, childIds:[1,42,46] },
  1: { id:1, childIds:[2,10,19] },
  2: { id:2, childIds:[] }
}
```
삭제/이동 시 부모 체인 전체 복사가 필요한 구조는 평탄화.
Immer 사용 시 mutation 스타일로 단순화 가능.

## 핵심 인용
> "Make your state as simple as it can be — but no simpler."

## Recap
- 함께 변하는 변수 → 합치기
- impossible state 발생 가능성 차단
- redundant 데이터 = 동기화 버그
- 객체 대신 id 보관
- 깊은 중첩 → 정규화된 평탄 구조
- props를 state에 mirror하지 않기
