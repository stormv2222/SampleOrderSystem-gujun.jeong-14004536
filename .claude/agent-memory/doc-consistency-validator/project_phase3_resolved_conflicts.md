---
name: Phase 3 정합성 검증 결과 및 확정 결정
description: Phase 3 구현 전 검증에서 발견된 이슈와 해결 결정 — 구현 시 반드시 반영
type: project
---

## 검증 완료일: 2026-05-08

## 자체 해결된 이슈

### C-01: MainController order_ctrl 파라미터 확장 방식
- **결정**: Optional 파라미터 방식으로 확장
  ```python
  def __init__(
      self,
      view: MainView,
      sample_ctrl: SampleController | None = None,
      order_ctrl: OrderController | None = None,
  ) -> None:
      ...
      if order_ctrl is not None:
          self._menu["2"] = ("주문 접수", order_ctrl.run_reserve)
  ```
- **근거**: Phase 2에서 확립된 sample_ctrl Optional 패턴과 동일. phase3.md가 self._menu["2"] 직접 대입만 기술하여 방식이 불명확했으나, 기존 구현체 패턴으로 자체 해결.
- **main.py wiring**: `MainController(main_view, sample_ctrl=sample_ctrl, order_ctrl=order_ctrl)`

### W-01: Inventory id 필드 타입
- **결정**: id 포함 전 필드 문자열 저장
- **근거**: phase3.md inventory JSON 예시 `{"id": "1", ...}` + sample.py 구현체 `record["id"] = str(raw["next_id"])` 패턴 일치.

### W-02: next_id 타입
- **결정**: next_id는 정수 저장
- **근거**: phase3.md 예시, SPEC.md, sample.py 모두 정수 next_id 사용. 일치.

### W-03: PLAN.md 신규 파일 수 4 vs phase3.md 실제 파일 7
- **결정**: PLAN.md는 테스트 파일 제외 카운팅 관례. 충돌 없음.
- **근거**: Phase 1(4개), Phase 2(3개)와 동일 패턴 확인.

### I-01: OrderController 생성자 시그니처 SPEC vs phase3 차이
- **결정**: phase3.md 시그니처 기준 (`inventory_repo: InventoryRepository` 사용)
- **근거**: SPEC.md 예시는 완성 시그니처, Phase 3은 점진적 구현. Repository 참조가 아키텍처상 올바름.

### I-02: add_quantity 신규 생성 동작 SPEC 미명시
- **결정**: phase3.md 설계 결정 유효 ("레코드가 없으면 신규 생성")
- **근거**: SPEC 위배 없음. 실용적이며 Phase 5 생산 완료 처리 시 필요.

## 구현 시 추가 확정 사항

- `OrderRepository.create()`: status 필드 없으면 "RESERVED" 고정 삽입
- `main_controller.py`에서 TYPE_CHECKING 패턴으로 OrderController import (순환 import 방지)
- 모든 Repository 구현은 sample.py 패턴 동일하게 적용
