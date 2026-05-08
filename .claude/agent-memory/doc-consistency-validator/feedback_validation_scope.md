---
name: 정합성 검증 범위 — 설계 문서만 대상
description: 문서 일관성 검증 시 기존 구현 파일을 확인하지 말 것 — 설계 문서 간 교차 검증만 수행
type: feedback
---

문서 정합성 검증은 설계 문서(SPEC.md, CLAUDE.md, PLAN.md, phase*.md) 간 교차 검증에만 집중한다. 기존 구현 파일(models/, controllers/, views/ 등)은 확인하지 않는다.

**Why:** 사용자가 Phase 6 검증 시 "기존 구현 파일들은 체크하지 않아도 돼, 이번 phase의 설계문서에 대해서만 일관성 검증해줘"라고 명시적으로 피드백.

**How to apply:** 각 Phase 검증 시 해당 phase*.md와 상위 문서(SPEC.md, CLAUDE.md, PLAN.md) 간 교차 비교만 수행. Interface contracts 섹션에서 "기존 구현에 메서드가 있는지" 확인은 설계 문서 내에서 언급된 내용으로만 판단. 실제 파일 read 금지.
