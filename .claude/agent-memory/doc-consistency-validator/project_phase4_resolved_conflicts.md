---
name: Phase 4 정합성 검증 결과 및 확정 결정
description: Phase 4 구현 전 검증에서 발견된 이슈와 해결 결정 — 구현 시 반드시 반영
type: project
---

## 검증 완료일: 2026-05-08

## 검증 결과: PROCEED (CRITICAL 0건, WARNING 2건 자체 해결, INFO 1건)

## 자체 해결된 이슈

### W-01: OrderController __init__ 시그니처 변경과 main.py 동기화 필수
- **결정**: `production_queue: ProductionQueue` 파라미터를 `inventory_repo`와 `view` 사이에 삽입.
  `main.py`도 함께 수정해야 하며, Phase 4 구현 대상 목록에 포함되어 있어 인지됨.
- **확정 시그니처**:
  ```python
  def __init__(
      self,
      order_repo: OrderRepository,
      sample_repo: SampleRepository,
      inventory_repo: InventoryRepository,   # SPEC.md의 inventory: Inventory는 무시
      production_queue: ProductionQueue,
      view: OrderView,
  ) -> None:
  ```
- **확정 main.py wiring**:
  ```python
  production_queue = ProductionQueue()
  order_ctrl = OrderController(order_repo, sample_repo, inventory_repo, production_queue, order_view)
  ```
- **근거**: Phase 3 구현체가 `inventory_repo: InventoryRepository`를 사용하며, Phase 3 정합성 검증(I-01)에서 Repository 참조가 아키텍처상 올바름으로 확정.

### W-02: run_reject 데드코드 위험 — 위임 래퍼로 구현 결정
- **결정**: `run_reject()`는 별도 로직 없이 `run_approve()`를 위임 호출하는 래퍼로 구현.
  메뉴 "3"은 `run_approve`에만 연결. `run_reject`는 테스트 등 외부 진입점 확보 목적으로만 존재.
  ```python
  def run_reject(self) -> None:
      """run_approve와 동일 진입점. 내부에서 [1]승인/[2]거절 분기."""
      return self.run_approve()
  ```
- **근거**: phase4.md MainController 연동 섹션이 `menu["3"] = run_approve`만 명시.
  `_reject(order)` (밑줄 접두사, private)가 실제 거절 처리를 담당하며 `run_approve` 내부 분기에서 호출됨.

### I-01: subtract_quantity ValueError와 _approve() 행복 경로 안전성
- **결정**: 현행 구현 유지. 변경 불필요.
- **근거**: `_approve()` 선행 검사(`stock >= quantity`)가 성립할 때만 `subtract_quantity` 호출.
  `inv is None → stock = 0`이므로 레코드 없음 케이스도 자연 처리됨.
  단일 스레드 콘솔 앱이므로 TOCTOU 레이스 컨디션 위험 없음.

## PASS 처리된 체크

- CHECK 1: ProductionTask 속성(order_id, sample_id, actual_quantity, total_time) SPEC 부합
- CHECK 2: 생산 공식 `math.ceil(shortage / (yield_rate * 0.9))` 3문서 완전 일치
- CHECK 3: 상태 전이(RESERVED→CONFIRMED/PRODUCING/REJECTED) FSM 완전 일치
- CHECK 4: Controller→ProductionQueue(Model) 의존 방향 적법
- CHECK 5: import math 허용, print/input 금지 준수, json_lib 변경 없음
