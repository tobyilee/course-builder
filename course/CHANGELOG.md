# Changelog

이 코스의 모든 의미 있는 변경 사항은 이 파일에 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)을 따르며,
버전 규약은 [Semantic Versioning](https://semver.org/lang/ko/)을 사용합니다.

- **MAJOR**: 코스 구조(섹션·클래스 구성)나 학습 목표의 호환성 깨짐 수준의 개편
- **MINOR**: 신규 클래스/섹션/퀴즈 추가, 슬라이드·노트·스크립트의 구조적 보강
- **PATCH**: 오탈자 교정, 자막 정렬, 렌더링 버그 수정 등 학습 내용 동일 범위의 수정

## [1.0.0] — 2026-04-27

### Added
- 초기 릴리스: 9개 섹션(S0 오리엔테이션 + S1~S8) · 26개 클래스 · 섹션별 5~9문항 퀴즈
- 각 클래스: HTML slide deck + Markdown note + TTS transcript + per-slide MP3 + full.mp3
- 코스 인덱스 페이지와 player/quiz 푸터에 버전 배지 표시

### Fixed
- S0(오리엔테이션) 퀴즈의 보기 블록이 렌더되지 않던 문제 — `mc`/`multi-select` 타입을 표준 `mcq_single`/`mcq_multi`로 정규화
