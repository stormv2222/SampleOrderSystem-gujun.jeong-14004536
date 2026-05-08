# Phase 6 세부 설계: 모니터링 (실시간 자동 갱신)

> **목표**: 주문 상태별 현황과 시료별 재고 상태를 한 화면에서 확인한다.  
> `data/order.json` 또는 `data/inventory.json`이 변경되면 1초 이내에 화면이 자동 갱신된다.

---

## 생성 파일 목록

```
semicon/
├── app/
│   ├── __init__.py
│   └── watcher.py                 # FileWatcher — os.path.getmtime() 1초 폴링, 데몬 스레드
├── views/
│   └── monitoring_view.py         # 대시보드 출력 (_clear() + 전체 재출력), 재고 상태 표기
├── controllers/
│   └── monitoring_controller.py   # FileWatcher 콜백 → _do_refresh(), _refresh_active 플래그
└── tests/
    ├── test_watcher.py
    └── test_controller_monitoring.py
```

---

## 클래스 설계

### `app/watcher.py` — `FileWatcher`

```python
import os
import threading
from typing import Callable, Optional

class FileWatcher:
    def __init__(
        self,
        file_path: str,
        callback: Callable[[], None],
        interval: float = 1.0,
    ) -> None:
        self._file_path = file_path
        self._callback = callback
        self._interval = interval
        self._last_mtime: Optional[float] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """백그라운드 데몬 스레드 시작."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """stop_event set → thread.join(timeout=2.0)."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        """폴링 루프. stop_event가 set되면 즉시 종료."""
        while not self._stop_event.wait(self._interval):
            mtime = self._get_mtime()
            if mtime != self._last_mtime:
                self._last_mtime = mtime
                self._callback()

    def _get_mtime(self) -> Optional[float]:
        """파일이 없으면 None 반환 (예외 없음)."""
        try:
            return os.path.getmtime(self._file_path)
        except OSError:
            return None
```

**설계 원칙**:
- `threading.Event.wait(interval)` — busy-wait 없음, stop 시 즉시 반응
- 스레드는 `daemon=True` — 메인 프로세스 종료 시 자동 소멸
- 파일이 없어도 예외 없이 동작 (`_get_mtime()` → `None`)
- 파일이 새로 생성되면 `None → float` 변화로 감지하여 콜백 호출
- 여러 파일 감시 시 `FileWatcher` 인스턴스를 파일마다 하나씩 생성

---

### `views/monitoring_view.py` — `MonitoringView`

```python
import os
import sys
from datetime import datetime

class MonitoringView:
    def get_input(self, prompt: str) -> str:
        """사용자 입력 수신. strip() 처리."""

    def show_dashboard(
        self,
        orders: list[dict],
        inventories: list[dict],
        samples: list[dict],
    ) -> None:
        """_clear() 후 전체 대시보드 재출력."""

    def show_message(self, message: str) -> None: ...

    def _clear(self) -> None:
        """Windows: os.system('cls') / 기타: os.system('clear')"""
```

**대시보드 출력 형식**:
```
=== 모니터링 대시보드 === (최종 갱신: 2026-05-08 15:32:01)

[주문 현황]
  RESERVED  :  2건
  PRODUCING :  1건
  CONFIRMED :  0건
  RELEASE   :  3건

[재고 현황]
  시료명       | 재고  | 상태
  A형 시료     |   6   | 부족
  B형 시료     |  20   | 여유
  C형 시료     |   0   | 고갈

명령 (q: 종료) >
```

**재고 상태 판단 기준**:

| 상태 | 조건 |
|------|------|
| 고갈 | 재고 수량 == 0 |
| 부족 | RESERVED 또는 CONFIRMED 주문의 총 요구량 > 현재 재고 |
| 여유 | 그 외 |

> `show_dashboard`는 `orders`, `inventories`, `samples` 세 리스트를 받아 조합 출력한다.  
> `REJECTED` 주문은 집계에서 제외한다.

---

### `controllers/monitoring_controller.py` — `MonitoringController`

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
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._sample_repo = sample_repo
        self._view = view
        self._watchers = watchers
        self._refresh_active: bool = False

        for watcher in self._watchers:
            watcher._callback = self._on_file_changed

    def _on_file_changed(self) -> None:
        """파일 변경 감지 시 콜백. 사용자 입력 중에는 갱신 억제."""
        if not self._refresh_active:
            self._do_refresh()

    def _do_refresh(self) -> None:
        """최신 데이터 로드 후 대시보드 재출력."""
        orders = self._order_repo.read_all()
        inventories = self._inventory_repo.read_all()
        samples = self._sample_repo.read_all()
        self._view.show_dashboard(orders, inventories, samples)

    def run(self) -> None:
        """모니터링 루프. watchers 시작 → 초기 출력 → 입력 대기 → watchers 정지."""
```

**`run()` 흐름**:
```python
for watcher in self._watchers:
    watcher.start()
try:
    self._do_refresh()          # 초기 화면 출력
    while True:
        self._refresh_active = True
        try:
            cmd = self._view.get_input("명령 (q: 종료) > ")
        finally:
            self._refresh_active = False

        if cmd.lower() == "q":
            break
        # 다른 명령 확장 가능
finally:
    for watcher in self._watchers:
        watcher.stop()
```

**`main.py`에서 FileWatcher 생성**:
```python
order_watcher     = FileWatcher("data/order.json",     callback=lambda: None)
inventory_watcher = FileWatcher("data/inventory.json", callback=lambda: None)
monitoring_ctrl = MonitoringController(
    order_repo, inventory_repo, sample_repo, monitoring_view,
    watchers=[order_watcher, inventory_watcher],
)
```

---

## 테스트 설계

### `tests/test_watcher.py`

```python
class TestFileWatcher(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.path = tmp.name
        tmp.name; tmp.close()
```

| TC | 검증 내용 |
|----|-----------|
| TC-1 | 파일 수정 시 1초 내에 콜백이 호출된다 (`threading.Event.wait(timeout=2.0)`) |
| TC-2 | `stop()` 호출 후 스레드가 종료된다 (`thread.is_alive() == False`) |
| TC-3 | 파일이 없어도 예외 없이 `start()`/`stop()` 동작 |
| TC-4 | 파일이 새로 생성되면 콜백이 호출된다 |
| TC-5 | 파일 미변경 시 콜백이 호출되지 않는다 (일정 시간 대기 후 확인) |

```python
def test_callback_called_on_change(self):
    called = threading.Event()
    watcher = FileWatcher(self.path, callback=called.set, interval=0.1)
    watcher.start()
    with open(self.path, "w") as f:
        f.write("changed")
    triggered = called.wait(timeout=2.0)
    watcher.stop()
    self.assertTrue(triggered)

def test_stop_joins_thread(self):
    watcher = FileWatcher(self.path, callback=lambda: None, interval=0.1)
    watcher.start()
    watcher.stop()
    self.assertFalse(watcher._thread.is_alive())
```

### `tests/test_controller_monitoring.py`

```python
# tmp_path 사용, 실제 파일 I/O

def test_order_status_count_excludes_rejected():
    """REJECTED 주문은 집계에서 제외된다."""

def test_inventory_status_exhausted():
    """재고 수량 0 → 고갈 표시."""

def test_inventory_status_short():
    """RESERVED 주문 수량 > 재고 → 부족 표시."""

def test_inventory_status_ok():
    """재고 충분 → 여유 표시."""

def test_dashboard_output_contains_all_statuses():
    """대시보드 출력에 RESERVED/PRODUCING/CONFIRMED/RELEASE 모두 포함."""
```

---

## 자동 갱신 흐름 요약

```
JSON 파일 수정
  └─ FileWatcher._run() 폴링 (1초)
       └─ getmtime() 변화 감지
            └─ _callback() → MonitoringController._on_file_changed()
                 └─ _refresh_active == False 이면 _do_refresh()
                      ├─ order_repo.read_all()       ← 파일 전량 재읽기 (캐시 없음)
                      ├─ inventory_repo.read_all()
                      ├─ sample_repo.read_all()
                      └─ view.show_dashboard()
                           └─ _clear() + 전체 재출력
```

---

## `MainController` 연동

```python
# main.py
monitoring_ctrl = MonitoringController(
    order_repo, inventory_repo, sample_repo, monitoring_view,
    watchers=[order_watcher, inventory_watcher],
)

# main_controller.py
self._menu["4"] = ("모니터링", monitoring_ctrl.run)
```

---

## 완료 기준 체크리스트

- [ ] 모니터링 진입 시 대시보드 출력 (주문 현황 + 재고 현황)
- [ ] `REJECTED` 주문 집계 제외 확인
- [ ] 재고 상태 (여유/부족/고갈) 정확히 표기
- [ ] 타 메뉴에서 주문 접수 → 모니터링 화면 자동 갱신 (1초 내)
- [ ] `q` 입력 시 모니터링 종료 후 메인 메뉴 복귀
- [ ] `pytest tests/test_watcher.py` 전체 통과
- [ ] `pytest tests/test_controller_monitoring.py` 전체 통과
- [ ] Controller에서 `print`/`input` 직접 호출 없음
