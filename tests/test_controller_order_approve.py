import os
import tempfile
import unittest

from models.sample import SampleRepository
from models.order import OrderRepository
from models.inventory import InventoryRepository
from models.production_queue import ProductionQueue, ProductionTask
from views.order_view import OrderView
from controllers.order_controller import OrderController


def _make_ctrl(inputs: list[str]):
    def tmp_path():
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        p = f.name
        f.close()
        os.unlink(p)
        return p

    sample_repo = SampleRepository(tmp_path())
    order_repo = OrderRepository(tmp_path())
    inventory_repo = InventoryRepository(tmp_path())
    production_queue = ProductionQueue()
    view = OrderView()
    it = iter(inputs)
    view.get_input = lambda prompt="": next(it)
    # Phase 4: __init__ will accept production_queue between inventory_repo and view
    ctrl = OrderController(order_repo, sample_repo, inventory_repo, production_queue, view)
    return ctrl, sample_repo, order_repo, inventory_repo, production_queue, view


class TestOrderControllerApprove(unittest.TestCase):

    # 사이클 3 — 생산 공식 검증
    def test_calc_production_formula_shortage_50_yield_0_9(self):
        """shortage=50, yield=0.9 → ceil(50/(0.9×0.9))=62, total=62×30=1860"""
        ctrl, *_ = _make_ctrl([])
        actual_qty, total_time = ctrl._calc_production(50, 0.9, 30)
        self.assertEqual(actual_qty, 62)
        self.assertEqual(total_time, 1860)

    def test_calc_production_formula_shortage_10_yield_0_8(self):
        """shortage=10, yield=0.8 → ceil(10/(0.8×0.9))=ceil(13.88)=14, total=14×45=630"""
        ctrl, *_ = _make_ctrl([])
        actual_qty, total_time = ctrl._calc_production(10, 0.8, 45)
        self.assertEqual(actual_qty, 14)
        self.assertEqual(total_time, 630)

    # 사이클 4 — 재고 충분 → 주문 CONFIRMED + 재고 차감
    def test_approve_sufficient_stock_sets_confirmed(self):
        ctrl, sample_repo, order_repo, inventory_repo, production_queue, view = _make_ctrl(["1", "1", "50"])
        # 시료 생성 (yield_rate=0.9, avg_production_time=30)
        sample_repo.create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})
        # 재고 충분 (100 >= 50)
        inventory_repo.create({"sample_id": "1", "quantity": "100"})
        # RESERVED 주문 생성
        order = order_repo.create({"sample_id": "1", "customer": "서울대", "quantity": "50"})
        # _approve 직접 호출
        ctrl._approve(order)
        # 주문 상태 CONFIRMED 확인
        updated = order_repo.read_one(int(order["id"]))
        self.assertEqual(updated["status"], "CONFIRMED")
        # 재고 차감 확인 (100 - 50 = 50)
        inv = inventory_repo.find_by_sample_id(1)
        self.assertEqual(inv["quantity"], "50")

    # 사이클 5 — 재고 부족 + y → PRODUCING + 생산 큐 등록
    def test_approve_insufficient_stock_y_sets_producing(self):
        # inputs: y (재고 부족 확인)
        ctrl, sample_repo, order_repo, inventory_repo, production_queue, view = _make_ctrl(["y"])
        sample_repo.create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})
        # 재고 부족 (10 < 50)
        inventory_repo.create({"sample_id": "1", "quantity": "10"})
        order = order_repo.create({"sample_id": "1", "customer": "서울대", "quantity": "50"})
        # show_shortage_confirm, show_approve_result 람다 교체
        view.show_shortage_confirm = lambda shortage, actual_qty, total_time: None
        view.show_approve_result = lambda order_id, status: None
        ctrl._approve(order)
        # 주문 상태 PRODUCING 확인
        updated = order_repo.read_one(int(order["id"]))
        self.assertEqual(updated["status"], "PRODUCING")
        # 생산 큐에 태스크 1건 등록 확인
        self.assertEqual(production_queue.size(), 1)
        task = production_queue.peek()
        self.assertEqual(task.order_id, int(order["id"]))

    # 사이클 6 — 재고 부족 + n → 상태 변경 없음, 생산 큐 비어 있음
    def test_approve_insufficient_stock_n_no_change(self):
        # inputs: n (취소)
        ctrl, sample_repo, order_repo, inventory_repo, production_queue, view = _make_ctrl(["n"])
        sample_repo.create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})
        inventory_repo.create({"sample_id": "1", "quantity": "10"})
        order = order_repo.create({"sample_id": "1", "customer": "서울대", "quantity": "50"})
        view.show_shortage_confirm = lambda shortage, actual_qty, total_time: None
        view.show_message = lambda msg: None
        ctrl._approve(order)
        # 주문 상태 여전히 RESERVED
        updated = order_repo.read_one(int(order["id"]))
        self.assertEqual(updated["status"], "RESERVED")
        # 생산 큐 비어 있음
        self.assertTrue(production_queue.is_empty())

    # 사이클 7 — _reject → 주문 상태 REJECTED
    def test_reject_sets_rejected(self):
        ctrl, sample_repo, order_repo, _, _, view = _make_ctrl([])
        sample_repo.create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})
        order = order_repo.create({"sample_id": "1", "customer": "서울대", "quantity": "50"})
        view.show_reject_result = lambda order_id: None
        ctrl._reject(order)
        updated = order_repo.read_one(int(order["id"]))
        self.assertEqual(updated["status"], "REJECTED")

    # 사이클 8 — 존재하지 않는 주문 ID → show_error 호출
    def test_approve_invalid_order_id_shows_error(self):
        # inputs: order_id=999 (없는 주문), action=1 (승인 시도)
        ctrl, sample_repo, order_repo, _, _, view = _make_ctrl(["999", "1"])
        errors = []
        view.show_error = lambda msg: errors.append(msg)
        ctrl.run_approve()
        self.assertTrue(errors, "show_error()가 호출되지 않음")

    # 사이클 8 — CONFIRMED 상태 주문 → show_error 호출
    def test_approve_non_reserved_order_shows_error(self):
        ctrl, sample_repo, order_repo, _, _, view = _make_ctrl(["1", "1"])
        sample_repo.create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})
        order = order_repo.create({"sample_id": "1", "customer": "서울대", "quantity": "50", "status": "CONFIRMED"})
        errors = []
        view.show_error = lambda msg: errors.append(msg)
        ctrl.run_approve()
        self.assertTrue(errors, "show_error()가 호출되지 않음")
