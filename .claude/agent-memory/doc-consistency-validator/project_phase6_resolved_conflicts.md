---
name: Phase 6 정합성 검증 결과 및 확정 결정
description: Phase 6 구현 전 검증에서 발견된 이슈와 해결 결정 — 구현 시 반드시 반영
type: project
---

## 검증 완료일: 2026-05-08

## 검증 결과: PROCEED (CRITICAL 0건, WARNING 3건 자체 해결, INFO 2건)

## 자체 해결된 이슈

### W-01: 재고 "부족" 판단 기준 — phase6.md 기준 채택
- **결정**: RESERVED + CONFIRMED 상태 주문의 sample_id별 quantity 합산 > 현재 재고 → 부족.
- **근거**: SPEC.md는 "주문 대비" 기준만 명시하고 집계 대상 상태 미명시.
  phase6.md가 최신 상세 설계로 RESERVED + CONFIRMED만 명시. PRODUCING은 이미 생산 큐 등록으로 처리 완료이므로 제외 타당.
- **구현**: `relevant_statuses = {"RESERVED", "CONFIRMED"}`. 고갈(재고==0) 먼저 판정 후 부족 판정.

### W-02: MonitoringController 시그니처 — phase6.md 시그니처 채택
- **결정**:
  ```python
  class MonitoringController:
      def __init__(
          self,
          order_repo: OrderRepository,
          inventory_repo: InventoryRepository,
          sample_repo: SampleRepository,
          view: MonitoringView,
          watchers: list[FileWatcher],
      ) -> None:
  ```
- **근거**: SPEC.md의 MonitorController(단일 repository, 단일 watcher)는 DataMonitor 참조 구현 예시.
  이 프로젝트의 대시보드는 주문+재고+시료 3종 조합 필요. phase6.md가 정확.

### W-03: MainController — monitoring_ctrl 파라미터 추가 확정
- **결정**: 기존 패턴과 동일하게 Optional 파라미터로 추가.
  ```python
  # controllers/main_controller.py 수정 내용
  # TYPE_CHECKING 블록:
  from controllers.monitoring_controller import MonitoringController
  # __init__ 파라미터:
  monitoring_ctrl: MonitoringController | None = None
  # 생성자 본문:
  if monitoring_ctrl is not None:
      self._menu["4"] = ("모니터링", monitoring_ctrl.run)
  ```
- **main.py 추가 wiring**:
  ```python
  order_watcher     = FileWatcher("data/order.json",     callback=lambda: None)
  inventory_watcher = FileWatcher("data/inventory.json", callback=lambda: None)
  monitoring_view   = MonitoringView()
  monitoring_ctrl   = MonitoringController(
      order_repo, inventory_repo, sample_repo,
      monitoring_view,
      watchers=[order_watcher, inventory_watcher],
  )
  # MainController(…, monitoring_ctrl=monitoring_ctrl)
  ```
- **근거**: 기존 sample_ctrl, order_ctrl, production_ctrl, release_ctrl와 동일 패턴.
  기존 테스트는 MainController(view) 기본 파라미터 기준 → 영향 없음.

## INFO 이슈

### I-01: MonitorView vs MonitoringView 시그니처 차이
- SPEC.md: `show_dashboard(records: list[Record])`, `show_record` 존재
- phase6.md: `show_dashboard(orders, inventories, samples)`, `show_record` 없음
- **결론**: phase6.md 시그니처 사용. SPEC.md는 참조 구현 기반 일반 예시.

### I-02: FileWatcher callback lambda → Controller에서 교체 패턴
- main.py에서 `lambda: None`으로 생성 후 MonitoringController.__init__에서
  `watcher._callback = self._on_file_changed`로 교체.
- 의도된 설계 패턴 (FileWatcher → 다른 레이어 의존 없이 연결). 그대로 구현.

## PASS 처리된 체크

- CHECK 1: SampleRepository.read_all() 존재 확인 (models/sample.py line 44)
- CHECK 2: OrderRepository.read_all(), filter_by_status() 존재 확인 (models/order.py line 47, 75)
- CHECK 3: InventoryRepository.read_all() 존재 확인 (models/inventory.py line 43)
- CHECK 4: MainController 메뉴 "4" 현재 None — monitoring_ctrl 주입 시 교체 슬롯 준비됨
- CHECK 5: app/watcher.py는 os, threading, typing만 import → 다른 레이어 의존 없음
- CHECK 6: MonitoringController에 print/input 직접 호출 없음 (view 메서드 경유)
- CHECK 7: REJECTED 주문 집계 제외 — phase6.md show_dashboard 주석 및 테스트 케이스 명시
- CHECK 8: run()의 try/finally 구조 — watchers.stop() 보장, _refresh_active try/finally 관리
- CHECK 9: import json 없음, json_lib/ 수정 없음
