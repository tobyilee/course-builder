# AI Course Builder

## 하네스: AI Online Course Builder

**목표:** 주제 입력만으로 ADDIE + Bloom's Taxonomy 기반의 온라인 강의(Section → Class, 각 Class에 HTML slide + MD note + TTS transcript, Section 단위 quiz 5~9문항)를 자동 생성한다.

**트리거:** 강의·코스·커리큘럼 생성/설계/제작 요청 시 `course-builder` 스킬을 사용하라. "강의 만들어줘", "온라인 코스 설계", "커리큘럼 짜줘", "슬라이드+노트+스크립트", "TTS 강의", "섹션별 퀴즈 포함 강의", "이 주제로 강의 만들어", "코스 재실행", "섹션만 다시" 등이 트리거. 영어 요청도 동일 스킬 트리거: "make a course on X", "build a curriculum for X", "design a lecture for X". 단순 질문(이론 설명·정의 조사)은 직접 응답.

**언어 지정:** Course 생성 요청의 language는 기본 `ko`. 사용자가 "영어로", "in English", "English course", "영문으로 만들어줘" 등을 명시하면 `language="en"`으로 orchestrator에 전달 — slide·note·transcript·quiz·audio·player UI 전부 영어로 생성. 요청 언어로부터 자동 추정하지 말 것(예: 사용자가 영어로 물어봤다고 해서 영어 강의로 가정 금지; 명시 필요).

**작업 디렉토리:** `course/` (산출물), `_workspace/` (중간 산출물, 재실행 시 `_workspace_prev/`로 이동).

