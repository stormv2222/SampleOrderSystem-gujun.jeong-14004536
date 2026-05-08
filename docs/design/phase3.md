# Phase 3 세부 설계: 재고 관리 + 주문 접수

> **목표**: 주문을 접수(`RESERVED`)할 수 있다. 접수 시 해당 시료의 재고를 함께 표시한다.  
> 재고는 `data/inventory.json`, 주문은 `data/order.json`에 저장된다.

---

## 생성 파일 목록

```
semicon/
├── models/
│   ├── inventory.py               # Inventory dataclass + InventoryRepository
│   └── order.py                   # Order dataclass + OrderRepository
├── views/
│   └── order_view.py              # 주문 접수 입력, 주문 목록 출력
├── controllers/
│   └── order_controller.py        # run_reserve() 흐름 조율
└── tests/
    ├── test_model_inventory.py
    ├── test_model_order.py
    └── test_controller_order_reserve.py
```

> `MainController`의 `"2"` 키 action을 `order_ctrl.run_reserve`로 교체한다.

---

## 클래스 설계

### `models/inventory.py`

#### `Inventory` dataclass

```python
from dataclasses import dataclass

@dataclass
class Inventory:
    id: int
    sample_id: int
    quantity: int
```

#### `InventoryRepository`

```python
class InventoryRepository:
    def __init__(self, file_path: str = "data/inventory.json") -> None:
        self._file_path = file_path

    def _load_raw(self) -> dict: ...
    def _load(self) -> list[dict]: ...
    def _save(self, raw: dict) -> None: ...

    def create(self, fields: dict) -> dict:
        """fields 예시: {"sample_id": "1", "quantity": "100"}"""

    def read_all(self) -> list[dict]: ...

    def read_one(self, record_id: int) -> dict | None: ...

    def find_by_sample_id(self, sample_id: int) -> dict | None:
        """특정 시료 ID의 재고 레코드 반환. 없으면 None."""

    def update(self, record_id: int, fields: dict) -> dict | None: ...

    def delete(self, record_id: int) -> bool: ...

    def add_quantity(self, sample_id: int, amount: int) -> dict | None:
        """재고 수량 증가. 레코드가 없으면 신규 생성."""

    def subtract_quantity(self, sample_id: int, amount: int) -> dict | None:
        """재고 수량 차감. 부족 시 ValueError. 레코드가 없으면 None."""
```

**파일 저장 형식**:
```json
{
  "next_id": 2,
  "records": [
    {"id": "1", "sample_id": "1", "quantity": "100"},
    {"id": "2", "sample_id": "2", "quantity": "0"}
  ]
}
```

---

### `models/order.py`

#### `Order` dataclass

```python
from dataclasses import dataclass

@dataclass
class Order:
    id: int
    sample_id: int
    customer: str
    quantity: int
    status: str   # RESERVED | REJECTED | PRODUCING | CONFIRMED | RELEASE
```

#### `OrderRepository`

```python
class OrderRepository:
    def __init__(self, file_path: str = "data/order.json") -> None:
        self._file_path = file_path

    def _load_raw(self) -> dict: ...
    def _load(self) -> list[dict]: ...
    def _save(self, raw: dict) -> None: ...

    def create(self, fields: dict) -> dict:
        """status는 fields에 없으면 "RESERVED"로 고정 설정.
        fields 예시: {"sample_id": "1", "customer": "서울대", "quantity": "50"}"""

    def read_all(self) -> list[dict]: ...

    def read_one(self, record_id: int) -> dict | None: ...

    def update(self, record_id: int, fields: dict) -> dict | None: ...

    def delete(self, record_id: int) -> bool: ...

    def filter_by_status(self, status: str) -> list[dict]:
        """특정 상태의 주문 목록 반환."""

    def search(self, key: str, value: str) -> list[dict]: ...
```

**파일 저장 형식**:
```json
{
  "next_id": 2,
  "records": [
    {"id": "1", "sample_id": "1", "customer": "서울대 연구소",
     "quantity": "50", "status": "RESERVED"}
  ]
}
```

---

### `views/order_view.py` — `OrderView`

```python
class OrderView:
    def show_reserve_prompt(self) -> None:
        """주문 접수 화면 헤더 출력."""

    def get_input(self, prompt: str) -> str:
        """사용자 입력 수신. strip() 처리."""

    def show_order_list(self, orders: list[dict], title: str = "주문 목록") -> None:
        """주문 목록 출력. 비어 있으면 "접수된 주문 없음" 출력."""

    def show_order(self, order: dict) -> None:
        """단건 주문 정보 출력."""

    def show_message(self, message: str) -> None: ...

    def show_error(self, message: str) -> None: ...
```

**주문 접수 화면**:
```
=== 주문 접수 ===
시료 ID: 
고객명: 
주문 수량: 
```

**주문 접수 완료 메시지**:
```
>> 주문이 접수되었습니다. (주문 ID: 1, 상태: RESERVED)
   현재 재고: 0 ea
```

**주문 목록 출력 형식**:
```
[접수 주문 목록] 총 N건
  주문 ID: 1 | 시료 ID: 1 | 고객: 서울대 연구소 | 수량: 50 | 상태: RESERVED
```

---

### `controllers/order_controller.py` — `OrderController`

Phase 3에서는 `run_reserve`만 구현한다. Phase 4에서 `run_approve`, `run_reject`를 추가한다.

```python
class OrderController:
    def __init__(
        self,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
        inventory_repo: InventoryRepository,
        view: OrderView,
    ) -> None:
        self._order_repo = order_repo
        self._sample_repo = sample_repo
        self._inventory_repo = inventory_repo
        self._view = view

    def run_reserve(self) -> None:
        """주문 접수 흐름. 시료 ID 검증 후 RESERVED 주문 생성."""
```

**`run_reserve()` 흐름**:
```
view.show_reserve_prompt()
sample_id = view.get_input("시료 ID: ")
sample = sample_repo.read_one(int(sample_id))
if sample is None:
    view.show_error("존재하지 않는 시료 ID입니다.")
    return

customer = view.get_input("고객명: ")
quantity = view.get_input("주문 수량: ")
order = order_repo.create({"sample_id": sample_id, "customer": customer, "quantity": quantity})

inv = inventory_repo.find_by_sample_id(int(sample_id))
current_qty = int(inv["quantity"]) if inv else 0
view.show_message(f"주문이 접수되었습니다. (주문 ID: {order['id']}, 상태: RESERVED)\n   현재 재고: {current_qty} ea")
```

---

## 테스트 설계

### `tests/test_model_inventory.py`

| TC | 검증 내용 |
|----|-----------|
| TC-1 | `create` 후 `find_by_sample_id` → 해당 레코드 반환 |
| TC-2 | `add_quantity` → 수량 증가 확인 |
| TC-3 | `subtract_quantity` → 수량 차감 확인 |
| TC-4 | `subtract_quantity` 수량 부족 시 `ValueError` |
| TC-5 | 존재하지 않는 `sample_id` → `find_by_sample_id` → `None` |
| TC-6 | 파일 없는 상태에서 `read_all()` → 빈 리스트, 예외 없음 |

### `tests/test_model_order.py`

| TC | 검증 내용 |
|----|-----------|
| TC-1 | `create` 시 `status`가 `"RESERVED"`로 저장됨 |
| TC-2 | `create` 후 반환 레코드에 `id` 포함, 모든 값 `str` |
| TC-3 | `read_all()` → 전체 주문 목록 반환 |
| TC-4 | `filter_by_status("RESERVED")` → 해당 상태 주문만 반환 |
| TC-5 | `update(id, {"status": "CONFIRMED"})` → 상태 변경 확인 |
| TC-6 | 파일 없는 상태에서 `read_all()` → 빈 리스트, 예외 없음 |

### `tests/test_controller_order_reserve.py`

```python
# view.get_input 람다 교체, tmp_path 사용

def test_reserve_creates_order():
    """유효한 시료 ID → 주문 RESERVED 상태로 생성."""

def test_reserve_invalid_sample_id():
    """존재하지 않는 시료 ID → view.show_error 호출, 주문 미생성."""

def test_reserve_shows_current_inventory():
    """접수 완료 메시지에 현재 재고 수량 포함."""
```

---

## `MainController` 연동

```python
# main.py
order_ctrl = OrderController(order_repo, sample_repo, inventory_repo, order_view)

# main_controller.py
self._menu["2"] = ("주문 접수", order_ctrl.run_reserve)
```

---

## 완료 기준 체크리스트

- [ ] 시료 ID 입력 시 존재 여부 검증
- [ ] 주문 접수 후 `data/order.json` 생성 및 `RESERVED` 상태 확인
- [ ] 접수 완료 메시지에 주문 ID와 현재 재고 표시
- [ ] `pytest tests/test_model_inventory.py` 전체 통과
- [ ] `pytest tests/test_model_order.py` 전체 통과
- [ ] `pytest tests/test_controller_order_reserve.py` 전체 통과
- [ ] Controller에서 `print`/`input` 직접 호출 없음
- [ ] `import json` 미사용 (`json_lib` 사용)
