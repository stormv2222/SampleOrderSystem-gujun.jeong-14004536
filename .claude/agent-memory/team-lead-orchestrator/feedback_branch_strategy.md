---
name: Phase 구현 브랜치 전략
description: Phase 구현 시작 전 feature/phase{N} 브랜치를 먼저 생성해야 함
type: feedback
---

Phase 구현을 시작할 때는 반드시 `feature/phase{N}` 브랜치를 먼저 생성하고 해당 브랜치에서 작업해야 한다.

**Why:** 사용자가 Phase 3 진행 중 직접 요청함. CLAUDE.md 브랜치 전략에도 명시된 규칙이지만, orchestrator가 Phase 0 단계에서 자동으로 브랜치를 생성하지 않았음.

**How to apply:** Phase 0 (Task Decomposition) 단계에서 Phase Plan 제시 직후, 일관성 검증(Phase 1)을 시작하기 전에 `git checkout master && git checkout -b feature/phase{N}` 실행. master 기준으로 브랜치를 생성하고 작업은 전부 해당 브랜치에서 진행.
