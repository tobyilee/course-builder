---
name: asset-build
description: Final build step — render all Marp slides, validate SSML, synthesize the course manifest, and package bundle.zip. Use when coherence review has passed and the course is ready for deployment. Triggered by the asset-builder agent.
---

# Asset Build — Deployable Bundle

coherence-reviewer가 `overall: "pass"` 판정한 뒤 수행. Idempotent — 여러 번 돌려도 결과 동일.

## 실행 조건
- `_workspace/99_coherence_report.json`의 `overall == "pass"`
- 아니면 **거부**: `BUILD_REFUSED: coherence not passed`

## 빌드 순서

### 1. 환경 검증
- `marp` CLI 설치 확인
- `xmllint` 또는 fallback 경로 확인
- `zip` 설치 확인

### 2. Marp 전체 재렌더
모든 `slide.source.md`를 재렌더하여 `slide.html`을 갱신.
이유: 중간에 슬라이드만 수정되었을 수 있으므로 항상 최신 상태 보장 (idempotency).

```bash
find course/sections -name slide.source.md -print0 | while IFS= read -r -d '' f; do
  dir=$(dirname "$f")
  marp --html --allow-local-files "$f" -o "$dir/slide.html"
done
```

### 3. SSML 검증
존재하는 `transcript.ssml` 각각에 대해 `validate-ssml.sh` 실행.
실패는 `WARNING`으로 격하 (txt는 항상 유효).

### 4. Quiz schema 검증
각 `quiz.json` 비즈니스 룰 검증:
- items 길이 5~9
- mcq_single의 correct 길이 == 1
- mcq_multi의 correct 길이 2~3
- 모든 item.explanation 비어있지 않음
- bloom_distribution 키 집합 유효

### 5. Manifest 합성

`course/manifest.json`:
```json
{
  "course": {
    "topic": "...", "audience": "...",
    "depth": "...", "language": "ko", "tone": "...",
    "total_duration_min": 120,
    "build_ts": "2026-04-22T14:30:00Z",
    "harness_version": "1.0.0"
  },
  "learning_objectives": [ /* from _workspace/01_architect_learning_objectives.json */ ],
  "sections": [
    {
      "id": "S1", "slug": "01-intro", "title": "...",
      "lo_ids": ["LO-1.1","LO-1.2"],
      "quiz_path": "sections/01-intro/quiz.json",
      "classes": [
        {
          "id": "S1.C1", "slug": "01-what-is-rsc", "title": "...",
          "lo_ids": ["LO-1.1"],
          "assets": {
            "slide_source": "sections/01-intro/classes/01-what-is-rsc/slide.source.md",
            "slide_html":   "sections/01-intro/classes/01-what-is-rsc/slide.html",
            "note_md":      "sections/01-intro/classes/01-what-is-rsc/note.md",
            "transcript_txt": "sections/01-intro/classes/01-what-is-rsc/transcript.txt",
            "transcript_ssml": "sections/01-intro/classes/01-what-is-rsc/transcript.ssml"
          }
        }
      ]
    }
  ],
  "stats": {
    "sections": 4, "classes": 10, "total_slides": 45,
    "lo_count": 14,
    "bloom_distribution": {"Remember":2,"Understand":4,"Apply":5,"Analyze":3},
    "estimated_audio_duration_sec": 7200
  },
  "asset_errors": []
}
```

### 6. 번들 패키징

```bash
# 빌드 디렉토리 초기화 (stale artifact 방지)
rm -rf course/build
mkdir -p course/build

# course/ 를 zip으로 (단, build 자체와 _workspace 제외)
cd course
zip -r build/bundle.zip . \
  -x 'build/*' \
  -x '_workspace/*' \
  -x '.DS_Store' \
  -x '*/.*'
cd ..
```

### 7. 빌드 로그

`_workspace/98_build_log.txt`:
```
2026-04-22T14:30:00Z BUILD START
  Marp render: 10/10 classes OK
  SSML validate: 3/3 OK
  Quiz schema: 4/4 OK
  Manifest written
  Bundle: course/build/bundle.zip (1.8 MB)
2026-04-22T14:30:42Z BUILD COMPLETE
```

## 부분 빌드 허용 조건

coherence-reviewer가 `overall: "pass"`라도 `asset_errors`가 있을 수 있음:
- Marp 렌더 실패한 class 1~2개
- SSML 검증 실패 (warning 수준)

이 경우 manifest.asset_errors에 기록하고 번들은 계속 빌드. 사용자에게는 "부분 빌드 완료, N개 이슈 있음" 알림.

## 에러 핸들링

### Marp 미설치
`BUILD_FAILED: marp CLI missing. Install: npm install -g @marp-team/marp-cli`

### zip 실패
재시도 1회. 재실패 시 tar.gz 대체 제안.

### Disk full
즉시 중단, 정리 요청.

## 재호출 (Idempotency)

매 빌드마다:
1. `course/build/` 삭제
2. 모든 slide.html 재생성
3. manifest.json 재생성

`_workspace/`는 절대 건드리지 않음.

## 체크리스트
- [ ] coherence pass 확인
- [ ] marp/xmllint/zip 가용
- [ ] slide.html 전체 재렌더
- [ ] quiz schema 전수 검증
- [ ] manifest.stats 계산 정확
- [ ] bundle.zip 크기 정상 (1~50MB 범위)
- [ ] asset_errors 있으면 manifest에 기록
- [ ] build_log.txt 작성
