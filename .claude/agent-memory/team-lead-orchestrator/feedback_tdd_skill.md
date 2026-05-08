---
name: Phase 구현 시 /tdd 스킬 사용 필수
description: Phase 개발 진행 시 /tdd 스킬로 오케스트레이션하고, 세부 구현 위임 시 tdd-feature-implementer 에이전트 사용
type: feedback
---

Phase 구현(코드 작성)을 진행할 때는 반드시 `/tdd` 스킬로 오케스트레이션한다.

세부 구현 작업(테스트 추가, 코드 구현)을 서브에이전트에 위임할 때는 일반(general-purpose) 에이전트가 아닌 `tdd-feature-implementer` 에이전트(subagent_type: "tdd-feature-implementer")를 사용한다.

**Why:**
- /tdd 스킬: RED/GREEN/REVIEW 사이클 전체를 올바르게 orchestrate
- tdd-feature-implementer: 세부 구현 위임 시 TDD 원칙에 맞게 작업

**How to apply:**
- 오케스트레이터(team-lead-orchestrator)가 직접 코드를 작성할 때 → Skill 툴로 `tdd` 스킬 호출
- /tdd 사이클 내에서 특정 구현 작업을 서브에이전트에 위임할 때 → Agent(subagent_type: "tdd-feature-implementer") 사용
- 일반(general-purpose) 에이전트에게 코드 작성을 위임하지 말 것
