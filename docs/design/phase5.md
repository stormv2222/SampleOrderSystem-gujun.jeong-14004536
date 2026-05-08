# Phase 5 세부 설계: 생산 라인 + 출고 처리

> **목표**: 생산 큐를 조회하고 생산 완료를 처리할 수 있다(`PRODUCING` → `CONFIRMED`).  
> `CONFIRMED` 주문에 대해 출고를 실행하면 `RELEASE`로 전환된다.  
> 이 Phase 완료 시 **전체 주문 사이클**이 처음부터 끝까지 동작한다.

---

## 생성 파일 목록

```
semicon/
├── views/
│   ├── production_view.py         # 생산 현황 출력, 생산 완료 입력
│   └── release_view.py            # 출고 대상 주문 출력, 출고 실행 입력
├── controllers/
│   ├── production_controller.py   # 생산 큐 조회, 생산 완료 처리
│   └── release_controller.py      # 출고 처리 흐름
└── tests/
    ├── test_controller_production.py
    └── test_controller_release.py
```

---

## 클래스 설계

### `views/production_view.py` — `ProductionView`

```python
class ProductionView:
    def get_input(self, prompt: str) -> str:
        """사용자 입력 수신. strip() 처리."""

    def show_queue(self, tasks: list[ProductionTask]) -> None:
        """생산 큐 전체 목록 출력. 비어 있으면 "대기 중인 생산 작업이 없습니다." 출력."""

    def show_message(self, message: str) -> None: ...

    def show_error(self, message: str) -> None: ...
```

**생산 큐 출력 형식**:
```
=== 생산 라인 ===
[현재 생산 큐]
  순번 1 | 주문 ID: 1 | 시료 ID: 1 | 실 생산량: 56 ea | 예상 시간: 1680 min
  순번 2 | 주문 ID: 3 | 시료 ID: 2 | 실 생산량: 20 ea | 예상 시간: 900 min
```

**생산 완료 처리 메시지**:
```
>> 생산 완료. 주문 ID 1이 CONFIRMED 상태로 전환되었습니다.
   재고 56 ea 추가됨.
```

---

### `views/release_view.py` — `ReleaseView`

```python
class ReleaseView:
    def get_input(self, prompt: str) -> str:
        """사용자 입력 수신. strip() 처리."""

    def show_confirmed_orders(self, orders: list[dict]) -> None:
        """CONFIRMED 상태 주문 목록 출력. 비어 있으면 "출고 대기 주문이 없습니다." 출력."""

    def show_message(self, message: str) -> None: ...

    def show_error(self, message: str) -> None: ...
```

**출고 대기 주문 출력 형식**:
```
=== 출고 처리 ===
[출고 대기 주문]
  주문 ID: 1 | 시료 ID: 1 | 고객: 서울대 연구소 | 수량: 50
```

**출고 완료 메시지**:
```
>> 출고 완료. 주문 ID 1이 RELEASE 상태로 전환되었습니다.
```

---

### `controllers/production_controller.py` — `ProductionController`

```python
class ProductionController:
    def __init__(
        self,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
        production_queue: ProductionQueue,
        view: ProductionView,
    ) -> None:
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._queue = production_queue
        self._view = view

    def run(self) -> None:
        """생산 라인 서브 메뉴 루프."""

    def _show_queue(self) -> None:
        """현재 생산 큐 목록 출력."""

    def _complete_production(self) -> None:
        """주문 ID 입력 → 큐에서 해당 작업 완료 처리.
        주문 상태 PRODUCING → CONFIRMED, 재고 actual_quantity만큼 증가."""
```

**`run()` 흐름**:
```
while True:
    tasks = queue.list_all()
    view.show_queue(tasks)
    choice = view.get_input("완료 처리할 주문 ID (0: 뒤로): ")
    if choice == "0": break
    self._complete_production_by_id(int(choice))
```

**`_complete_production_by_id(order_id)` 흐름**:
```
# 큐에서 해당 order_id를 가진 작업 탐색
task = None
for t in queue.list_all():
    if t.order_id == order_id:
        task = t
        break

if task is None:
    view.show_error("생산 큐에 해당 주문이 없습니다.")
    return

# 큐에서 제거 (order_id 기준으로 순서 유지하며 제거)
# → ProductionQueue에 remove_by_order_id(order_id) 메서드 추가
queue.remove_by_order_id(order_id)

# 재고 추가
inventory_repo.add_quantity(task.sample_id, task.actual_quantity)

# 주문 상태 변경
order_repo.update(order_id, {"status": "CONFIRMED"})

view.show_message(
    f"생산 완료. 주문 ID {order_id}이 CONFIRMED 상태로 전환되었습니다.\n"
    f"   재고 {task.actual_quantity} ea 추가됨."
)
```

> `ProductionQueue`에 `remove_by_order_id(order_id: int) -> bool` 메서드를 추가한다.

---

### `controllers/release_controller.py` — `ReleaseController`

```python
class ReleaseController:
    def __init__(
        self,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
        view: ReleaseView,
    ) -> None:
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._view = view

    def run(self) -> None:
        """출고 처리 서브 메뉴 루프."""

    def _release_order(self, order_id: int) -> None:
        """CONFIRMED 주문을 RELEASE로 전환. 재고에서 주문 수량 차감."""
```

**`run()` 흐름**:
```
while True:
    confirmed = order_repo.filter_by_status("CONFIRMED")
    view.show_confirmed_orders(confirmed)
    order_id_str = view.get_input("출고할 주문 ID (0: 뒤로): ")
    if order_id_str == "0": break
    self._release_order(int(order_id_str))
```

**`_release_order(order_id)` 흐름**:
```
order = order_repo.read_one(order_id)
if order is None or order["status"] != "CONFIRMED":
    view.show_error("출고 가능한 주문이 아닙니다.")
    return

order_repo.update(order_id, {"status": "RELEASE"})
view.show_message(f"출고 완료. 주문 ID {order_id}이 RELEASE 상태로 전환되었습니다.")
```

---

## 테스트 설계

### `tests/test_controller_production.py`

```python
# view.get_input 람다 교체, tmp_path 사용 실제 파일 I/O, 실제 ProductionQueue 사용

def test_show_queue_outputs_tasks():
    """큐에 작업이 있으면 view.show_queue 호출."""

def test_complete_production_sets_confirmed():
    """완료 처리 → 주문 PRODUCING→CONFIRMED, 재고 actual_quantity 증가."""

def test_complete_production_removes_task_from_queue():
    """완료 처리 후 해당 작업이 큐에서 제거된다."""

def test_complete_production_invalid_order_id():
    """큐에 없는 주문 ID → view.show_error 호출."""
```

### `tests/test_controller_release.py`

```python
def test_release_sets_release_status():
    """CONFIRMED 주문 → 출고 처리 → 상태 RELEASE."""

def test_release_non_confirmed_order():
    """RESERVED/PRODUCING 주문 ID → view.show_error 호출, 상태 변경 없음."""

def test_release_nonexistent_order():
    """존재하지 않는 주문 ID → view.show_error 호출."""

def test_show_confirmed_orders_empty():
    """CONFIRMED 주문 없을 때 "출고 대기 주문이 없습니다." 출력."""
```

---

## `MainController` 연동

```python
# main.py
production_ctrl = ProductionController(order_repo, inventory_repo, production_queue, production_view)
release_ctrl    = ReleaseController(order_repo, inventory_repo, release_view)

# main_controller.py
self._menu["5"] = ("출고 처리",  release_ctrl.run)
self._menu["6"] = ("생산 라인", production_ctrl.run)
```

---

## 전체 주문 사이클 수동 검증 시나리오

```
1. 시료 등록 (ID: 1, avg_time: 30, yield: 0.9)
2. 주문 접수 (sample_id: 1, quantity: 50) → RESERVED
3. 주문 승인 → 재고 0 → 부족분 50 → 실 생산량 ceil(50/0.81)=62, 시간=1860min → PRODUCING
4. 생산 라인 → 주문 ID 1 완료 처리 → CONFIRMED, 재고 +62
5. 출고 처리 → 주문 ID 1 출고 → RELEASE
```

---

## 완료 기준 체크리스트

- [ ] 생산 큐 목록 정상 출력
- [ ] 생산 완료 처리 → 주문 `CONFIRMED` + 재고 증가 확인
- [ ] 출고 처리 → 주문 `RELEASE` 전환 확인
- [ ] `CONFIRMED`가 아닌 주문 출고 시도 → 오류 메시지 출력
- [ ] 전체 주문 사이클 수동 시나리오 정상 동작
- [ ] `pytest tests/test_controller_production.py` 전체 통과
- [ ] `pytest tests/test_controller_release.py` 전체 통과
- [ ] Controller에서 `print`/`input` 직접 호출 없음
