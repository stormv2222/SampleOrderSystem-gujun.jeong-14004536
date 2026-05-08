---
name: 오케스트레이터 역할 분담 원칙
description: team-lead-orchestrator가 직접 하는 것과 각 전문 에이전트에 위임하는 것의 명확한 경계
type: feedback
---

team-lead-orchestrator는 오케스트레이션과 플래닝만 직접 수행한다. 아래 표에 따라 전문 에이전트에 위임한다.

## 역할 분담표

| 단계 | 담당 에이전트 | 시점 |
|------|--------------|------|
| Phase 시작 전 문서 정합성 검증 | **doc-consistency-validator** | Phase 구현 시작 전 항상 |
| 소스 코드 구현 (GREEN 단계) | **tdd-feature-implementer** | RED 단계 사람 승인 후 |
| 테스트 실행 및 통과 검증 | **test-validator** | 구현 완료 후 |
| 요구사항 충족 여부 검증 | **phase-requirements-evaluator** | 구현 완료 후 |
| test-validator + phase-requirements-evaluator | **병렬 실행** | 항상 동시에 실행하여 빠른 verify |

## team-lead-orchestrator가 직접 하는 것

- Phase 0: 작업 분해 및 Plan.md 작성
- TDD RED 단계: 실패하는 테스트 코드 작성 및 실패 확인
- 사용자에게 체크포인트 보고 및 승인 요청
- 에이전트 위임 및 결과 취합
- Phase 4: 사용자 리뷰 요청 (구조화된 완료 보고)

## team-lead-orchestrator가 직접 하지 않는 것

- 소스 코드 작성 (tdd-feature-implementer에 위임)
- 문서 정합성 검증 (doc-consistency-validator에 위임)
- 테스트 실행/검증 (test-validator에 위임)
- 요구사항 준수 검증 (phase-requirements-evaluator에 위임)

**Why:** 사용자가 명시적으로 지시. 각 전문 에이전트가 자신의 역할에 집중하고, test-validator와 phase-requirements-evaluator를 병렬 실행하여 verify를 빠르게 완료한다.

**How to apply:** Phase 시작 시 → doc-consistency-validator. GREEN 단계 → tdd-feature-implementer. 구현 완료 후 → test-validator와 phase-requirements-evaluator를 반드시 병렬(단일 메시지 내 두 Agent 호출)로 실행한다.
