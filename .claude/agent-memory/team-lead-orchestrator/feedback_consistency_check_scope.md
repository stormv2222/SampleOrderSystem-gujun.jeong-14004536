---
name: 일관성 검증 범위 제한
description: doc-consistency-validator는 설계/요구사항 문서만 검증, 구현 소스코드 체크 불필요
type: feedback
---

일관성 검증 시 doc-consistency-validator에 전달하는 검증 대상을 설계·요구사항 문서로만 제한한다. 구현된 소스코드 파일(models/, controllers/, views/ 등)은 검증 대상에서 제외한다.

**Why:** 구현 코드는 이미 TDD로 검증되었으므로 중복 체크가 불필요하다. 설계 문서 간 정합성(SPEC.md ↔ PLAN.md ↔ phase{N}.md ↔ CLAUDE.md)만 확인하면 충분하다.

**How to apply:** doc-consistency-validator 호출 시 prompt에서 "현재 구현된 파일들" 항목과 소스코드 파일 경로 목록을 제거한다. 검증 항목도 문서 간 충돌·누락 위주로만 작성한다.
