---
name: Plan.md 라이프사이클 관리
description: Phase 완료 후 Plan.md는 feature 브랜치에만 남기고 master에서는 삭제해야 함
type: feedback
---

Phase가 완료되면 다음 순서로 Plan.md를 처리한다:

1. feature/phase{N} 브랜치에 모든 변경사항 커밋 (Plan.md 포함)
2. master 브랜치로 머지
3. master 브랜치에서 Plan.md 삭제 후 커밋
4. 결과: Plan.md는 feature/phase{N} 브랜치에만 남고, master에는 없음

**Why:** 사용자가 직접 요청. Plan.md는 Phase 임시 설계 파일이므로 master에 올라가면 안 됨. feature 브랜치에는 이력 추적 목적으로 유지.

**How to apply:** Phase 완료 후 master 머지 직후, `git rm Plan.md && git commit` 으로 master에서 제거. feature 브랜치는 삭제하지 않으므로(CLAUDE.md 브랜치 전략) Plan.md 이력이 보존됨.
