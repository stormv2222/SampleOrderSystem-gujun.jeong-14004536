# Phase 7 세부 설계: 더미 데이터 생성기 + 통합 테스트

> **목표**: 시료·주문·재고 더미 데이터를 자동으로 생성하여 삽입할 수 있다.  
> 전체 주문 사이클(접수 → 승인 → 생산 → 출고)이 더미 데이터로 처음부터 끝까지 검증된다.

---

## 생성 파일 목록

```
semicon/
├── generator/
│   ├── __init__.py
│   ├── schema.py              # FieldDef dataclass + DEFAULT_SCHEMAS
│   └── engine.py              # DummyGenerator
└── tests/
    ├── test_generator.py
    └── test_integration.py
```

> `MainController`에 더미 데이터 생성 메뉴 항목(`"7"`)을 추가한다.  
> `controllers/main_controller.py`와 `views/main_view.py`를 수정한다.

---

## 클래스 설계

### `generator/schema.py`

```python
from typing import Literal
from dataclasses import dataclass

FieldType = Literal['name', 'string', 'int']

@dataclass
class FieldDef:
    name: str             # JSON 키 이름 (도메인 엔티티 속성명과 일치해야 함)
    field_type: FieldType # 생성 알고리즘 선택자

DEFAULT_SCHEMAS: dict[str, list[FieldDef]] = {
    # Sample: sample_id는 Repository 자동 부여이므로 제외
    'sample': [
        FieldDef('name',                'string'),  # 시료 이름
        FieldDef('avg_production_time', 'int'),     # 평균 생산 시간 (분)
        FieldDef('yield_rate',          'int'),     # 1~100 범위, 실제 사용 시 /100
    ],
    # Order: order_id 자동 부여, status는 Repository에서 'RESERVED' 고정
    'order': [
        FieldDef('sample_id', 'int'),   # 참조 시료 ID
        FieldDef('customer',  'name'),  # 고객명
        FieldDef('quantity',  'int'),   # 주문 수량
    ],
    # Inventory
    'inventory': [
        FieldDef('sample_id', 'int'),   # 재고 대상 시료 ID
        FieldDef('quantity',  'int'),   # 현재 재고 수량
    ],
}
```

**필드명 규칙**: 더미 데이터의 필드명은 반드시 도메인 엔티티의 속성명과 일치해야 한다.

---

### `generator/engine.py` — `DummyGenerator`

```python
import random
import string

class DummyGenerator:
    def __init__(self, schema: list[FieldDef]) -> None:
        self._schema = schema

    def generate_one(self) -> dict:
        """스키마에 따라 레코드 1건 생성. 모든 값은 str 타입."""
        return {field.name: self._generate_value(field.field_type)
                for field in self._schema}

    def generate_batch(self, count: int) -> list[dict]:
        """N건 일괄 생성."""
        return [self.generate_one() for _ in range(count)]

    def _generate_value(self, field_type: str) -> str:
        """타입별 값 생성. 모든 반환값은 str."""
        if field_type == 'int':
            return str(random.randint(1, 100))
        elif field_type == 'name':
            return self._random_name()
        elif field_type == 'string':
            return self._random_string()
        raise ValueError(f"Unknown field_type: {field_type}")

    def _random_name(self) -> str:
        """한글 성 + 영문 이름 조합 또는 고정 풀에서 선택."""

    def _random_string(self) -> str:
        """무작위 알파벳·숫자 조합 문자열."""
```

**생성 예시**:
```python
gen = DummyGenerator(DEFAULT_SCHEMAS['order'])
gen.generate_one()
# → {"sample_id": "3", "customer": "Alice Kim", "quantity": "15"}

gen.generate_batch(3)
# → [{"sample_id": "1", ...}, {"sample_id": "7", ...}, {"sample_id": "2", ...}]
```

**생성값 범위 (int 타입)**:

| 필드 | 범위 | 비고 |
|------|------|------|
| `avg_production_time` | 1 ~ 100 | 분 단위 str |
| `yield_rate` | 1 ~ 100 | 실제 사용 시 /100 |
| `sample_id` | 1 ~ 100 | str |
| `quantity` | 1 ~ 100 | str |

> `random.seed()` 미설정 — 실행마다 값이 달라짐.  
> 테스트는 정확한 값이 아닌 **범위·형식·허용 집합**으로 검증.

---

### `MainController` 메뉴 확장

```python
# main_controller.py
self._menu["7"] = ("더미 데이터 생성", dummy_ctrl.run)

# main.py — DummyController 조립
from controllers.dummy_controller import DummyController
dummy_ctrl = DummyController(
    repos={"sample": sample_repo, "order": order_repo, "inventory": inventory_repo},
    view=main_view,
)
```

#### `DummyController`

```python
class DummyController:
    def __init__(
        self,
        repos: dict[str, Any],   # {"sample": SampleRepository, ...}
        view: MainView,           # get_input / show_message 재사용
    ) -> None:
        self._repos = repos
        self._view = view

    def run(self) -> None:
        """스키마 선택 → 건수 입력 → 생성 → Repository 저장."""

    def auto_generate_and_insert(self, schema_name: str, count: int) -> None:
        gen = DummyGenerator(DEFAULT_SCHEMAS[schema_name])
        batch = gen.generate_batch(count)
        repo = self._repos[schema_name]
        for fields in batch:
            repo.create(fields)
        self._view.show_message(f"{count}건의 {schema_name} 더미 데이터를 추가했습니다.")
```

**실행 화면**:
```
=== 더미 데이터 생성 ===
스키마 선택 (sample / order / inventory): sample
생성할 건수: 5
>> 5건의 sample 더미 데이터를 추가했습니다.
```

---

## 테스트 설계

### `tests/test_generator.py`

```python
@pytest.fixture
def sample_gen():
    return DummyGenerator(DEFAULT_SCHEMAS['sample'])

@pytest.fixture
def order_gen():
    return DummyGenerator(DEFAULT_SCHEMAS['order'])
```

| TC | 검증 내용 |
|----|-----------|
| TC-1 | `generate_one()` 반환 dict의 key 집합이 스키마 필드명과 일치 |
| TC-2 | 모든 값이 `str` 타입 |
| TC-3 | `int` 타입 필드(quantity 등)는 `isdigit() == True`, 범위 내 숫자 (20회 반복) |
| TC-4 | `name` 타입 필드(customer)는 비어 있지 않음 (20회 반복) |
| TC-5 | `generate_batch(5)` → 정확히 5건 반환 |
| TC-6 | `generate_batch(0)` → 빈 리스트 반환 |
| TC-7 | `yield_rate` 필드 값이 1 이상 100 이하 (20회 반복) |

```python
def test_all_values_are_str(order_gen):
    for _ in range(20):
        result = order_gen.generate_one()
        assert all(isinstance(v, str) for v in result.values())

def test_quantity_range(order_gen):
    for _ in range(20):
        result = order_gen.generate_one()
        assert result['quantity'].isdigit()
        assert 1 <= int(result['quantity']) <= 100
```

### `tests/test_integration.py`

전체 주문 사이클을 실제 파일 I/O와 함께 처음부터 끝까지 검증한다.

```python
@pytest.fixture
def setup(tmp_path):
    sample_repo    = SampleRepository(str(tmp_path / "sample.json"))
    order_repo     = OrderRepository(str(tmp_path / "order.json"))
    inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
    queue          = ProductionQueue()
    return sample_repo, order_repo, inventory_repo, queue
```

| TC | 시나리오 |
|----|----------|
| TC-1 | 더미 시료 5건 생성 → `read_all()` 5건 확인 |
| TC-2 | 재고 충분 경로: 시료 등록 → 재고 등록(100) → 주문 접수(qty=50) → 승인 → `CONFIRMED` + 재고 50 확인 |
| TC-3 | 재고 부족 경로: 시료 등록(yield=0.9) → 주문 접수(qty=50) → 승인 → `PRODUCING` + 생산 큐 등록 |
| TC-4 | 생산량 계산: 부족분=50, yield=0.9 → actual_qty == ceil(50/(0.9×0.9)) == 62 |
| TC-5 | 생산 완료 처리: `PRODUCING` → `CONFIRMED` + 재고 actual_qty 추가 |
| TC-6 | 출고 처리: `CONFIRMED` → `RELEASE` |
| TC-7 | 전체 사이클 end-to-end: 접수 → 승인(부족) → 생산 완료 → 출고 → 최종 상태 `RELEASE` |
| TC-8 | 모니터링 집계: 주문 상태별 건수가 실제 데이터와 일치 |
| TC-9 | `REJECTED` 주문은 모니터링 집계에서 제외 |

```python
def test_full_cycle_insufficient_stock(setup):
    sample_repo, order_repo, inventory_repo, queue = setup

    # 시료 등록
    sample = sample_repo.create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})
    sample_id = int(sample["id"])

    # 주문 접수
    order = order_repo.create({"sample_id": str(sample_id), "customer": "연구소", "quantity": "50"})
    assert order["status"] == "RESERVED"

    # 승인 (재고 없음 → PRODUCING)
    shortage = 50
    actual_qty = math.ceil(shortage / (0.9 * 0.9))  # 62
    task = ProductionTask(int(order["id"]), sample_id, actual_qty, 30 * actual_qty)
    queue.enqueue(task)
    order_repo.update(int(order["id"]), {"status": "PRODUCING"})
    assert order_repo.read_one(int(order["id"]))["status"] == "PRODUCING"

    # 생산 완료
    inventory_repo.add_quantity(sample_id, actual_qty)
    order_repo.update(int(order["id"]), {"status": "CONFIRMED"})
    assert int(inventory_repo.find_by_sample_id(sample_id)["quantity"]) == actual_qty

    # 출고
    order_repo.update(int(order["id"]), {"status": "RELEASE"})
    assert order_repo.read_one(int(order["id"]))["status"] == "RELEASE"
```

---

## `DummyController` 단위 테스트

```python
def test_auto_generate_inserts_n_records(tmp_path):
    repo = SampleRepository(str(tmp_path / "sample.json"))
    view = MainView()
    view.get_input = iter(["sample", "3"]).__next__
    ctrl = DummyController(repos={"sample": repo}, view=view)
    ctrl.run()
    assert len(repo.read_all()) == 3
```

---

## 완료 기준 체크리스트

- [ ] `더미 데이터 생성` 메뉴 진입 → 스키마 선택 → 건수 입력 → 데이터 삽입 확인
- [ ] `sample`, `order`, `inventory` 스키마 모두 정상 생성
- [ ] `pytest tests/test_generator.py` 전체 통과
- [ ] `pytest tests/test_integration.py` 전체 통과
- [ ] 통합 테스트에서 생산량 계산 공식 `ceil(부족분 / (수율 × 0.9))` 결과 검증
- [ ] 통합 테스트에서 전체 주문 사이클 end-to-end 검증
- [ ] 모니터링 집계가 실제 주문 상태와 일치
- [ ] `REJECTED` 주문 모니터링 제외 검증
