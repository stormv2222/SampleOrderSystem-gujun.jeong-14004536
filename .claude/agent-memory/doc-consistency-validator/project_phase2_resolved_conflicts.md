---
name: Phase 2 정합성 검증 결과 및 확정 결정
description: Phase 2 구현 전 검증에서 발견된 이슈와 해결 결정 — 구현 시 반드시 반영
type: project
---

## 검증 완료일: 2026-05-08

## 자체 해결된 이슈

### W-01: SampleRepository 기본값 파라미터
- **결정**: `def __init__(self, file_path: str = "data/sample.json") -> None` 채택
- **근거**: phase2.md의 main.py 예시 `SampleRepository()` 와 일관성 유지. SPEC.md 시그니처는 추상 정의로 해석.

### W-02: id 저장 형식
- **결정**: id 포함 모든 필드를 문자열로 저장
- **근거**: SPEC.md 본문 규칙 + phase2.md TC-1 명시. SPEC.md JSON 예시의 정수 id는 오타.

### W-03: SampleController.run() 디스패치 방식
- **결정**: SPEC.md의 dict 기반 커맨드 매핑 컨벤션 준수. phase2.md 의사코드는 설명 목적.
- **근거**: SPEC.md "if/elif 대신 dict 기반 커맨드 매핑 사용" 강제 규칙 + Phase 1 구현체와 일관성.

### I-01: avg_time vs avg_production_time
- **결정**: `avg_production_time` 사용
- **근거**: SPEC.md 오타. 나머지 전체 문서가 avg_production_time 사용.

### I-02: main.py 잉여 문자 `1`
- **권장**: Phase 2에서 main.py 수정 시 8번째 줄의 `1` 제거

## 사용자 확인이 필요한 이슈

### C-01: MainController.__init__ 시그니처 확장 방식
- **현재 구현**: `def __init__(self, view: MainView) -> None`
- **Phase 2 필요 시그니처**: `sample_ctrl: SampleController | None = None` 파라미터 추가
- **권장 Option A**: phase1.md 확장 계획대로 생성자에 Optional 파라미터 추가
- **상태**: 2026-05-08 검증 시점에 사용자 확인 대기 중

**How to apply:** Phase 2 구현 시작 전 이 결정이 확정되어야 함. 확정되면 이 파일 업데이트.
