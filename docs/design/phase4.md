# Phase 4 세부 설계: 주문 승인/거절 + 생산 큐

> **목표**: 접수된 주문(`RESERVED`)에 대해 승인 또는 거절을 처리한다.  
> - 재고 충분 → `CONFIRMED`  
> - 재고 부족 → 생산 큐 등록 + `PRODUCING`  
> - 거절 → `REJECTED`

---

## 생성 파일 목록

```
semicon/
├── models/
│   └── production_queue.py        # ProductionTask dataclass + ProductionQueue (FIFO)
├── views/
│   └── order_view.py              # (기존 파일에 메서드 추가)
├── controllers/
│   └── order_controller.py        # run_approve(), run_reject() 추가
└── tests/
    ├── test_model_production_queue.py
    └── test_controller_order_approve.py
```

---

## 클래스 설계

### `models/production_queue.py`

#### `ProductionTask` dataclass

```python
from dataclasses import dataclass

@dataclass
class ProductionTask:
    order_id: int
    sample_id: int
    actual_quantity: int    # 실 생산량 (ceil(부족분 / (수율 × 0.9)))
    total_time: int         # 총 생산 시간 (분) = avg_production_time × actual_quantity
```

#### `ProductionQueue`

생산 큐는 **인메모리 FIFO** 자료구조다. 파일 영속성 없음(재시작 시 초기화).  
`main.py`에서 단일 인스턴스를 생성하여 `OrderController`와 `ProductionController`에 공유 주입한다.

```python
from collections import deque

class ProductionQueue:
    def __init__(self) -> None:
        self._queue: deque[ProductionTask] = deque()

    def enqueue(self, task: ProductionTask) -> None:
        """큐 끝에 작업 추가."""

    def peek(self) -> ProductionTask | None:
        """큐 앞 작업 반환 (제거하지 않음). 비어 있으면 None."""

    def dequeue(self) -> ProductionTask | None:
        """큐 앞 작업 제거 후 반환. 비어 있으면 None."""

    def list_all(self) -> list[ProductionTask]:
        """현재 큐 전체 목록 반환 (FIFO 순서)."""

    def is_empty(self) -> bool: ...

    def size(self) -> int: ...
```

---

### `views/order_view.py` — 추가 메서드

기존 `OrderView`에 아래 메서드를 추가한다.

```python
def show_approve_menu(self) -> None:
    """승인/거절 선택 메뉴 출력."""

def show_shortage_confirm(self, shortage: int, actual_qty: int, total_time: int) -> None:
    """재고 부족 시 생산 확인 메시지 출력.
    형식: "재고 부족 : 부족분 {shortage} ea 승인하시겠습니까? (실 생산량 {actual_qty} ea / {total_time} min)"
    """

def show_approve_result(self, order_id: int, new_status: str) -> None:
    """승인 결과 메시지 출력."""

def show_reject_result(self, order_id: int) -> None:
    """거절 결과 메시지 출력."""
```

**승인/거절 메뉴 출력 형식**:
```
[접수 주문 목록]
  주문 ID: 1 | 시료: A형 시료 | 고객: 서울대 연구소 | 수량: 50 | 상태: RESERVED

처리할 주문 ID: 
[1] 승인  [2] 거절 >
```

**재고 부족 확인 메시지**:
```
재고 부족 : 부족분 50 ea 승인하시겠습니까? (실 생산량 56 ea / 1680 min)
확인 (y/n) >
```

---

### `controllers/order_controller.py` — 추가 메서드

```python
import math

class OrderController:
    # Phase 3에서 __init__ 유지, production_queue 파라미터 추가

    def __init__(
        self,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
        inventory_repo: InventoryRepository,
        production_queue: ProductionQueue,
        view: OrderView,
    ) -> None: ...

    def run_approve(self) -> None:
        """RESERVED 주문 목록 표시 → 주문 ID 선택 → 승인/거절 처리."""

    def run_reject(self) -> None:
        """run_approve와 동일 진입점. 내부에서 [1]승인/[2]거절 분기."""

    def _approve(self, order: dict) -> None:
        """재고 확인 → 충분: CONFIRMED / 부족: PRODUCING + 생산 큐 등록."""

    def _reject(self, order: dict) -> None:
        """주문 상태를 REJECTED로 변경."""

    def _calc_production(self, shortage: int, yield_rate: float, avg_time: int) -> tuple[int, int]:
        """실 생산량과 총 생산 시간 계산.
        actual_qty = math.ceil(shortage / (yield_rate * 0.9))
        total_time = avg_time * actual_qty
        반환: (actual_qty, total_time)
        """
```

**`run_approve()` 흐름**:
```
reserved = order_repo.filter_by_status("RESERVED")
view.show_order_list(reserved, title="접수 주문 목록")
if not reserved:
    view.show_message("처리할 주문이 없습니다.")
    return

order_id = int(view.get_input("처리할 주문 ID: "))
order = order_repo.read_one(order_id)
if order is None or order["status"] != "RESERVED":
    view.show_error("유효하지 않은 주문 ID입니다.")
    return

view.show_approve_menu()
action = view.get_input("[1] 승인  [2] 거절 > ")
if action == "1":
    self._approve(order)
elif action == "2":
    self._reject(order)
else:
    view.show_error("올바른 번호를 입력하세요.")
```

**`_approve()` 흐름**:
```
sample = sample_repo.read_one(int(order["sample_id"]))
yield_rate = float(sample["yield_rate"])
avg_time   = int(sample["avg_production_time"])
quantity   = int(order["quantity"])

inv = inventory_repo.find_by_sample_id(int(order["sample_id"]))
stock = int(inv["quantity"]) if inv else 0

if stock >= quantity:
    # 재고 충분
    inventory_repo.subtract_quantity(int(order["sample_id"]), quantity)
    order_repo.update(int(order["id"]), {"status": "CONFIRMED"})
    view.show_approve_result(int(order["id"]), "CONFIRMED")
else:
    # 재고 부족
    shortage = quantity - stock
    actual_qty, total_time = self._calc_production(shortage, yield_rate, avg_time)
    view.show_shortage_confirm(shortage, actual_qty, total_time)
    confirm = view.get_input("확인 (y/n) > ")
    if confirm.lower() == "y":
        task = ProductionTask(
            order_id=int(order["id"]),
            sample_id=int(order["sample_id"]),
            actual_quantity=actual_qty,
            total_time=total_time,
        )
        production_queue.enqueue(task)
        order_repo.update(int(order["id"]), {"status": "PRODUCING"})
        view.show_approve_result(int(order["id"]), "PRODUCING")
    else:
        view.show_message("승인이 취소되었습니다.")
```

**생산량 계산 공식**:
```python
actual_qty = math.ceil(shortage / (yield_rate * 0.9))
total_time = avg_time * actual_qty
```

---

## 테스트 설계

### `tests/test_model_production_queue.py`

```python
class TestProductionQueue(unittest.TestCase):
    def setUp(self):
        self.q = ProductionQueue()
        self.task1 = ProductionTask(order_id=1, sample_id=1, actual_quantity=56, total_time=1680)
        self.task2 = ProductionTask(order_id=2, sample_id=2, actual_quantity=20, total_time=900)
```

| TC | 검증 내용 |
|----|-----------|
| TC-1 | `enqueue` 후 `size()` == 1 |
| TC-2 | `peek()` → 첫 작업 반환, 큐에서 제거하지 않음 |
| TC-3 | `dequeue()` → FIFO 순서 (먼저 넣은 것 먼저 나옴) |
| TC-4 | 빈 큐에서 `dequeue()` → `None` |
| TC-5 | 빈 큐에서 `peek()` → `None` |
| TC-6 | `list_all()` → 삽입 순서와 동일한 목록 |
| TC-7 | `is_empty()` 빈 큐 → `True`, 요소 있으면 → `False` |

### `tests/test_controller_order_approve.py`

```python
# view.get_input 람다 교체, tmp_path 사용 실제 파일 I/O

def test_approve_sufficient_stock_sets_confirmed():
    """재고 충분 → 주문 상태 CONFIRMED, 재고 차감."""

def test_approve_insufficient_stock_confirmed_y_sets_producing():
    """재고 부족 → y 입력 → 주문 상태 PRODUCING, 생산 큐 등록."""

def test_approve_insufficient_stock_n_no_change():
    """재고 부족 → n 입력 → 상태 변경 없음, 생산 큐 비어 있음."""

def test_reject_sets_rejected():
    """거절 → 주문 상태 REJECTED."""

def test_calc_production_formula():
    """shortage=50, yield=0.9 → ceil(50/(0.9*0.9)) = ceil(61.7) = 62 확인."""

def test_approve_invalid_order_id():
    """존재하지 않는 주문 ID → view.show_error 호출."""

def test_approve_non_reserved_order():
    """CONFIRMED 상태 주문 ID 입력 → view.show_error 호출."""
```

---

## `MainController` 연동

```python
# main.py
production_queue = ProductionQueue()
order_ctrl = OrderController(order_repo, sample_repo, inventory_repo, production_queue, order_view)

# main_controller.py
self._menu["3"] = ("주문 승인/거절", order_ctrl.run_approve)
```

---

## 완료 기준 체크리스트

- [ ] 재고 충분 승인 → 주문 `CONFIRMED` + 재고 차감 확인
- [ ] 재고 부족 승인(y) → 주문 `PRODUCING` + 생산 큐 등록 확인
- [ ] 재고 부족 승인(n) → 상태 변경 없음
- [ ] 거절 → 주문 `REJECTED` 확인
- [ ] 부족분·실 생산량·총 시간 메시지 형식 확인
- [ ] `pytest tests/test_model_production_queue.py` 전체 통과
- [ ] `pytest tests/test_controller_order_approve.py` 전체 통과
- [ ] Controller에서 `print`/`input` 직접 호출 없음
