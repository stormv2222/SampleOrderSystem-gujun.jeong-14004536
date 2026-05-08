---
name: Phase 시작 전 세부 설계 문서 존재 확인
description: Phase 구현 시작 전 docs/design/phase{N}.md 파일이 존재하는지 반드시 확인하고, 없으면 사용자에게 작성 필요를 알린다
type: feedback
---

Phase 구현을 시작하기 전에 항상 `docs/design/phase{N}.md` 파일이 존재하는지 확인한다.

파일이 없으면 즉시 사용자에게 알리고, 설계 문서가 작성될 때까지 구현을 진행하지 않는다.

**Why:** 세부 설계 문서 없이 구현을 시작하면 클래스 시그니처, 테스트 케이스, 완료 기준이 불명확해져 일관성 검증과 요구사항 평가가 불가능해진다. 사용자가 명시적으로 지시함.

**How to apply:** Phase 0 (작업 분해) 단계 맨 처음에 `docs/design/phase{N}.md` 파일 존재 여부를 확인한다. 파일이 없으면 아래 메시지로 사용자에게 알린다:

> "⚠️ `docs/design/phase{N}.md` 세부 설계 문서가 존재하지 않습니다. 구현을 시작하기 전에 설계 문서 작성이 필요합니다. 작성 후 다시 요청해 주세요."

파일이 존재하면 정상적으로 doc-consistency-validator → Plan.md → TDD 사이클을 진행한다.
