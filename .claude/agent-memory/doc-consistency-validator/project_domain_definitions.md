---
name: 도메인 정의 및 확정된 필드명/저장 형식
description: 반도체 시료 관리 프로젝트의 확정된 도메인 모델, 필드명, JSON 저장 규칙 — 다중 문서 교차 검증으로 확정
type: project
---

## 확정된 Sample 필드명

- `id` — Repository 자동 부여, 문자열로 저장
- `name` — 시료 이름
- `avg_production_time` — 평균 생산 시간 (분). SPEC.md JSON 예시의 `avg_time`은 오타로 확정
- `yield_rate` — 수율 (0.0~1.0)

**Why:** SPEC.md 저장 파일 구조 예시에서 `avg_time`이 사용되었으나, 동일 문서의 더미 데이터 필드명 표, DEFAULT_SCHEMAS, phase2.md 전체가 `avg_production_time`을 사용. 오타로 확정.

**How to apply:** JSON 저장 및 코드 어디서든 `avg_production_time`만 사용. `avg_time` 사용 코드 발견 시 즉시 지적.

## JSON 저장 형식 규칙

- 모든 필드 값은 `str` 타입으로 저장 (`id` 포함)
- SPEC.md JSON 예시의 `{"id": 1, ...}` (정수)는 오타. phase2.md의 `{"id": "1", ...}` (문자열)이 정확
- `next_id`는 정수로 저장 (dict의 최상위 키)
- 파일 없음 → `{"next_id": 1, "records": []}` 반환, 예외 없음
- 파일 존재하나 `records` 없거나 배열 아님 → `ValueError`

**Why:** SPEC.md 본문 "모든 값은 문자열로 저장" + phase2.md TC-1 "모든 값이 str" + 이후 Order의 sample_id가 문자열로 Sample.id와 비교되므로 타입 일관성 필요.

## 주문 상태 정의 (확정)

```
RESERVED → CONFIRMED → RELEASE          (재고 충분)
RESERVED → PRODUCING → CONFIRMED → RELEASE  (재고 부족)
RESERVED → REJECTED                     (거절, 모니터링 제외)
```

상태명: RESERVED, CONFIRMED, PRODUCING, RELEASE, REJECTED (RELEASED 아님)

## 생산량 계산 공식 (확정)

```python
import math
actual_production = math.ceil(shortage / (yield_rate * 0.9))
total_time = avg_production_time * actual_production
```

## 재고 상태 분류 (확정)

- 여유: 재고 >= 주문 수량
- 부족: 0 < 재고 < 주문 수량
- 고갈: 재고 = 0
