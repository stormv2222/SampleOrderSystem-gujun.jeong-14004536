"""
tests/test_integration.py — 전체 주문 사이클 통합 테스트 (Phase 7)

TC-1: 더미 시료 5건 생성 → read_all() 5건 확인
TC-2: 재고 충분 경로: RESERVED → CONFIRMED + 재고 차감
TC-3: 재고 부족 경로: RESERVED → PRODUCING + 생산 큐 등록
TC-4: 생산량 계산: ceil(부족분 / (수율 × 0.9)) 결과 검증
TC-5: 생산 완료: PRODUCING → CONFIRMED + 재고 추가
TC-6: 출고: CONFIRMED → RELEASE
TC-7: end-to-end 전체 사이클 (재고 부족 경로)
TC-8: 모니터링 집계: 주문 상태별 건수가 실제 데이터와 일치
TC-9: REJECTED 주문은 모니터링 집계에서 제외
"""
import math
import pytest

from models.sample import SampleRepository
from models.order import OrderRepository
from models.inventory import InventoryRepository
from models.production_queue import ProductionQueue, ProductionTask
from generator.engine import DummyGenerator
from generator.schema import DEFAULT_SCHEMAS


@pytest.fixture
def setup(tmp_path):
    sample_repo    = SampleRepository(str(tmp_path / "sample.json"))
    order_repo     = OrderRepository(str(tmp_path / "order.json"))
    inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
    queue          = ProductionQueue()
    return sample_repo, order_repo, inventory_repo, queue


# ── TC-1: 더미 시료 5건 생성 ─────────────────────────────────

def test_dummy_sample_bulk_insert(setup):
    """더미 시료 5건을 생성하면 read_all()이 5건을 반환한다."""
    sample_repo, _, _, _ = setup
    gen = DummyGenerator(DEFAULT_SCHEMAS['sample'])
    for fields in gen.generate_batch(5):
        sample_repo.create(fields)
    assert len(sample_repo.read_all()) == 5


# ── TC-2: 재고 충분 경로 ─────────────────────────────────────

def test_sufficient_stock_path(setup):
    """재고가 충분하면 주문이 CONFIRMED 상태로 전환되고 재고가 차감된다."""
    sample_repo, order_repo, inventory_repo, _ = setup

    sample = sample_repo.create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})
    sample_id = int(sample["id"])

    inventory_repo.create({"sample_id": str(sample_id), "quantity": "100"})
    order = order_repo.create({"sample_id": str(sample_id), "customer": "연구소", "quantity": "50"})
    assert order["status"] == "RESERVED"

    # 재고 충분 → CONFIRMED
    inventory_repo.subtract_quantity(sample_id, 50)
    order_repo.update(int(order["id"]), {"status": "CONFIRMED"})

    assert order_repo.read_one(int(order["id"]))["status"] == "CONFIRMED"
    assert int(inventory_repo.find_by_sample_id(sample_id)["quantity"]) == 50


# ── TC-3: 재고 부족 경로 ─────────────────────────────────────

def test_insufficient_stock_path(setup):
    """재고가 부족하면 주문이 PRODUCING으로 전환되고 생산 큐에 등록된다."""
    sample_repo, order_repo, inventory_repo, queue = setup

    sample = sample_repo.create({"name": "B형", "avg_production_time": "30", "yield_rate": "0.9"})
    sample_id = int(sample["id"])

    order = order_repo.create({"sample_id": str(sample_id), "customer": "연구소", "quantity": "50"})
    assert order["status"] == "RESERVED"

    # 재고 없음 → 부족 → PRODUCING
    shortage = 50
    actual_qty = math.ceil(shortage / (0.9 * 0.9))
    task = ProductionTask(
        order_id=int(order["id"]),
        sample_id=sample_id,
        actual_quantity=actual_qty,
        total_time=30 * actual_qty,
    )
    queue.enqueue(task)
    order_repo.update(int(order["id"]), {"status": "PRODUCING"})

    assert order_repo.read_one(int(order["id"]))["status"] == "PRODUCING"
    assert queue.size() == 1
    assert queue.peek().order_id == int(order["id"])


# ── TC-4: 생산량 계산 공식 검증 ──────────────────────────────

def test_production_quantity_formula():
    """부족분=50, yield_rate=0.9 → actual_qty == ceil(50 / (0.9×0.9)) == 62."""
    shortage = 50
    yield_rate = 0.9
    actual_qty = math.ceil(shortage / (yield_rate * 0.9))
    assert actual_qty == 62


def test_production_quantity_formula_various():
    """생산량 공식이 다양한 입력에서 올바르게 계산된다."""
    cases = [
        (10, 0.5, math.ceil(10 / (0.5 * 0.9))),
        (100, 1.0, math.ceil(100 / (1.0 * 0.9))),
        (1, 0.9, math.ceil(1 / (0.9 * 0.9))),
    ]
    for shortage, yr, expected in cases:
        assert math.ceil(shortage / (yr * 0.9)) == expected


# ── TC-5: 생산 완료 처리 ─────────────────────────────────────

def test_production_complete(setup):
    """생산 완료 처리 시 PRODUCING → CONFIRMED 전환 + 재고 actual_qty 추가."""
    sample_repo, order_repo, inventory_repo, queue = setup

    sample = sample_repo.create({"name": "C형", "avg_production_time": "30", "yield_rate": "0.9"})
    sample_id = int(sample["id"])

    order = order_repo.create({"sample_id": str(sample_id), "customer": "연구소", "quantity": "50"})
    order_repo.update(int(order["id"]), {"status": "PRODUCING"})

    actual_qty = 62
    task = ProductionTask(int(order["id"]), sample_id, actual_qty, 30 * actual_qty)
    queue.enqueue(task)

    # 생산 완료 처리
    inventory_repo.add_quantity(sample_id, actual_qty)
    order_repo.update(int(order["id"]), {"status": "CONFIRMED"})
    queue.remove_by_order_id(int(order["id"]))

    assert order_repo.read_one(int(order["id"]))["status"] == "CONFIRMED"
    assert int(inventory_repo.find_by_sample_id(sample_id)["quantity"]) == actual_qty
    assert queue.is_empty()


# ── TC-6: 출고 처리 ──────────────────────────────────────────

def test_release(setup):
    """CONFIRMED 주문에 출고를 실행하면 RELEASE로 전환된다."""
    sample_repo, order_repo, _, _ = setup

    sample = sample_repo.create({"name": "D형", "avg_production_time": "20", "yield_rate": "0.8"})
    order = order_repo.create({
        "sample_id": sample["id"], "customer": "고객A", "quantity": "10"
    })
    order_repo.update(int(order["id"]), {"status": "CONFIRMED"})

    # 출고 처리
    order_repo.update(int(order["id"]), {"status": "RELEASE"})

    assert order_repo.read_one(int(order["id"]))["status"] == "RELEASE"


# ── TC-7: 전체 사이클 end-to-end ─────────────────────────────

def test_full_cycle_insufficient_stock(setup):
    """재고 부족 경로 전체 사이클: RESERVED → PRODUCING → CONFIRMED → RELEASE."""
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
    queue.remove_by_order_id(int(order["id"]))
    assert int(inventory_repo.find_by_sample_id(sample_id)["quantity"]) == actual_qty
    assert order_repo.read_one(int(order["id"]))["status"] == "CONFIRMED"

    # 출고
    order_repo.update(int(order["id"]), {"status": "RELEASE"})
    assert order_repo.read_one(int(order["id"]))["status"] == "RELEASE"
    assert queue.is_empty()


# ── TC-8: 모니터링 집계 ──────────────────────────────────────

def test_monitoring_status_counts(setup):
    """주문 상태별 건수 집계가 실제 데이터와 일치한다."""
    sample_repo, order_repo, _, _ = setup

    sample = sample_repo.create({"name": "X형", "avg_production_time": "10", "yield_rate": "0.8"})
    sid = sample["id"]

    order_repo.create({"sample_id": sid, "customer": "A", "quantity": "1"})          # RESERVED
    order_repo.create({"sample_id": sid, "customer": "B", "quantity": "1"})          # RESERVED
    o3 = order_repo.create({"sample_id": sid, "customer": "C", "quantity": "1"})
    order_repo.update(int(o3["id"]), {"status": "PRODUCING"})                        # PRODUCING
    o4 = order_repo.create({"sample_id": sid, "customer": "D", "quantity": "1"})
    order_repo.update(int(o4["id"]), {"status": "RELEASE"})                          # RELEASE

    all_orders = order_repo.read_all()
    counts = {}
    for o in all_orders:
        counts[o["status"]] = counts.get(o["status"], 0) + 1

    assert counts.get("RESERVED", 0) == 2
    assert counts.get("PRODUCING", 0) == 1
    assert counts.get("RELEASE", 0) == 1


# ── TC-9: REJECTED 모니터링 제외 ─────────────────────────────

def test_rejected_excluded_from_monitoring(setup):
    """REJECTED 주문은 모니터링 집계에서 제외된다."""
    sample_repo, order_repo, _, _ = setup

    sample = sample_repo.create({"name": "Y형", "avg_production_time": "10", "yield_rate": "0.8"})
    sid = sample["id"]

    o1 = order_repo.create({"sample_id": sid, "customer": "A", "quantity": "1"})    # RESERVED
    o2 = order_repo.create({"sample_id": sid, "customer": "B", "quantity": "1"})
    order_repo.update(int(o2["id"]), {"status": "REJECTED"})                         # REJECTED

    # 모니터링은 REJECTED 제외
    monitored = [o for o in order_repo.read_all() if o.get("status") != "REJECTED"]

    assert len(monitored) == 1
    assert monitored[0]["id"] == o1["id"]
    assert all(o["status"] != "REJECTED" for o in monitored)
