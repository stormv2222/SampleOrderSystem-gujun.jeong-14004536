---
name: Phase 5 정합성 검증 결과 및 확정 결정
description: Phase 5 구현 전 검증에서 발견된 이슈와 해결 결정 — 구현 시 반드시 반영
type: project
---

## 검증 완료일: 2026-05-08

## 검증 결과: PROCEED (CRITICAL 0건, WARNING 3건 자체 해결, INFO 3건)

## 자체 해결된 이슈

### W-01: ReleaseController._release_order에서 재고 차감 없음 확정
- **결정**: `_release_order` 내부에서 `inventory_repo` 호출 없음. 재고 차감 구현하지 않음.
- **근거**: SPEC.md 출고 처리 섹션이 "주문 상태가 RELEASE로 전환"만 명시. 재고 차감 불명시.
  PLAN.md Phase 5 실행 확인 예시에도 재고 차감 메시지 없음.
  phase5.md 주석 "재고에서 주문 수량 차감"은 오기(誤記).
- **구현 방향**: `inventory_repo` 파라미터는 시그니처에 유지 (향후 확장), 내부 미사용.

### W-02: MainController 시그니처 확장 — 기존 패턴 동일 적용
- **확정 시그니처**:
  ```python
  def __init__(
      self,
      view: MainView,
      sample_ctrl=None,
      order_ctrl=None,
      production_ctrl=None,
      release_ctrl=None,
  ) -> None:
  ```
- **확정 main.py wiring**:
  ```python
  production_view  = ProductionView()
  release_view     = ReleaseView()
  production_ctrl  = ProductionController(order_repo, inventory_repo, production_queue, production_view)
  release_ctrl     = ReleaseController(order_repo, inventory_repo, release_view)
  ctrl = MainController(main_view, sample_ctrl=sample_ctrl, order_ctrl=order_ctrl,
                        production_ctrl=production_ctrl, release_ctrl=release_ctrl)
  ```
- **메뉴 연결**: `menu["5"] = ("출고 처리", release_ctrl.run)`, `menu["6"] = ("생산 라인", production_ctrl.run)`
- **근거**: 기존 `sample_ctrl`, `order_ctrl` 주입 패턴과 동일하게 `__init__` 파라미터로 수신.

### W-03: 기존 test_main_controller.py 안전성 확인
- **결론**: 기존 `test_not_implemented_for_valid_menu` 테스트는 `MainController(view)` (컨트롤러 미주입) 기준이므로
  `production_ctrl=None`, `release_ctrl=None` 기본값 유지 시 영향 없음.
- **Phase 5 신규 테스트**: test_main_controller.py에 메뉴 5·6 주입 테스트 2건 추가 필요.

## INFO 이슈

### I-01: 예시 숫자 불일치 (PLAN.md Phase 4 예시 vs phase5.md 시나리오)
- PLAN.md Phase 4 예시: `56 ea / 1680 min` (설명용, 부정확)
- phase5.md 시나리오: `62 ea / 1860 min` (공식 `ceil(50/0.81)=62` 정확)
- **결론**: 공식 `math.ceil(shortage / (yield_rate * 0.9))` 구현만 참조. 예시 숫자 무시.

### I-02: ProductionView 출력 형식 — 시료 ID 표기가 올바름
- phase5.md: `시료 ID: 1` 표기
- PLAN.md: `시료: A형 시료` 표기 (사용자 경험 관점 예시)
- **결론**: View는 `ProductionTask`의 `sample_id`만 출력. 이름 조회 불필요.
  아키텍처상 View → Repository 의존 불가.

### I-03: remove_by_order_id 권장 구현 패턴
- `self._queue = deque(t for t in self._queue if t.order_id != order_id)` 방식으로 FIFO 유지하며 제거.
- 제거된 항목 없으면 `False`, 있으면 `True` 반환.

## PASS 처리된 체크

- CHECK 1: PRODUCING → CONFIRMED 전이 SPEC.md FSM 부합
- CHECK 2: CONFIRMED → RELEASE 전이 SPEC.md FSM 부합
- CHECK 3: ProductionController 파라미터 (order_repo, inventory_repo, production_queue, view) — Repository 메서드 호환
- CHECK 4: ReleaseController 파라미터 (order_repo, inventory_repo, view) — filter_by_status, read_one, update 모두 존재
- CHECK 5: Controller → (Model, View) 의존 방향 적법. View → Repository 의존 없음
- CHECK 6: Controller에 print/input 직접 호출 없음 (phase5.md 흐름 코드 준수)
- CHECK 7: import json 없음, json_lib/ 수정 없음
