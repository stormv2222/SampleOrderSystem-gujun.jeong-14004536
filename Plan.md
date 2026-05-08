# Phase 6 TDD Plan — 묶음 진행

## 묶음 구성
| 묶음 | 사이클 | 대상 |
|------|--------|------|
| A | TC-1~5 | FileWatcher — app/__init__.py + app/watcher.py + tests/test_watcher.py |
| B | — | MonitoringView — views/monitoring_view.py (FakeView로 C묶음에서 검증) |
| C | 6개 TC | MonitoringController — controllers/monitoring_controller.py + tests/test_controller_monitoring.py |
| D | 1 TC | MainController 메뉴 4 연결 + tests/test_main_controller.py 추가 |
| E | — | main.py 의존성 조립 + 전체 pytest |

---

## Bundle A — FileWatcher

### 검증할 동작 (TC-1~5)
- TC-1: 파일 수정 시 1초 내 콜백 호출
- TC-2: stop() 후 스레드 종료
- TC-3: 파일 없어도 예외 없이 동작
- TC-4: 파일 새로 생성 시 콜백 호출
- TC-5: 파일 미변경 시 콜백 추가 호출 없음

### 예상 실패 이유
`app/watcher.py` 미존재 → ModuleNotFoundError

---

## Bundle B — MonitoringView

### 검증할 동작
`views/monitoring_view.py` import 가능. show_dashboard, show_message, _clear, _stock_status 구현.

### 예상 실패 이유
`views/monitoring_view.py` 미존재 → ModuleNotFoundError

---

## Bundle C — MonitoringController (6개 TC)

- show_dashboard 최소 1회 호출
- REJECTED 주문 집계 제외
- 재고 고갈(수량==0) 확인
- 재고 부족(RESERVED 주문 > 재고) 확인
- Watcher 시작/정지 확인
- _on_file_changed → _do_refresh 호출 (refresh_active 플래그 포함)

### 예상 실패 이유
`controllers/monitoring_controller.py` 미존재 → ModuleNotFoundError

---

## Bundle D — MainController 메뉴 4

### 검증할 동작
monitoring_ctrl 주입 시 "4" 입력 → monitoring_ctrl.run() 호출

### 예상 실패 이유
MainController 생성자에 monitoring_ctrl 파라미터 없음 → TypeError

---

## Bundle E — main.py 조립

### 검증할 동작
python main.py 실행 시 ImportError 없이 메인 메뉴 표시 + 전체 pytest 통과
