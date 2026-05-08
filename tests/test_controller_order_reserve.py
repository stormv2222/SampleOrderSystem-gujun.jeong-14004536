import os
import tempfile
import unittest

from models.sample import SampleRepository
from models.order import OrderRepository
from models.inventory import InventoryRepository
from views.order_view import OrderView
from controllers.order_controller import OrderController


def _make_ctrl(inputs: list[str]) -> tuple[OrderController, SampleRepository, OrderRepository, InventoryRepository, OrderView]:
    """임시 파일 + lambda 입력 주입으로 격리된 컨트롤러 생성."""
    def tmp_path(name):
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        p = f.name
        f.close()
        os.unlink(p)
        return p

    sample_repo = SampleRepository(tmp_path("sample"))
    order_repo = OrderRepository(tmp_path("order"))
    inventory_repo = InventoryRepository(tmp_path("inventory"))
    view = OrderView()
    it = iter(inputs)
    view.get_input = lambda prompt="": next(it)
    ctrl = OrderController(order_repo, sample_repo, inventory_repo, view)
    return ctrl, sample_repo, order_repo, inventory_repo, view


class TestOrderControllerReserve(unittest.TestCase):

    # 사이클 4 — 유효한 시료 ID → 주문 RESERVED 상태로 생성
    def test_reserve_creates_order(self):
        ctrl, sample_repo, order_repo, _, _ = _make_ctrl(["1", "서울대 연구소", "50"])
        sample_repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        ctrl.run_reserve()
        orders = order_repo.read_all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["status"], "RESERVED")
        self.assertEqual(orders[0]["customer"], "서울대 연구소")

    # 사이클 5 — 존재하지 않는 시료 ID → show_error 호출, 주문 미생성
    def test_reserve_invalid_sample_id(self):
        ctrl, sample_repo, order_repo, _, view = _make_ctrl(["999"])
        # sample_repo is empty — no samples exist
        errors = []
        view.show_error = lambda msg: errors.append(msg)
        ctrl.run_reserve()
        self.assertTrue(errors, "show_error()가 호출되지 않음")
        self.assertEqual(order_repo.read_all(), [])

    # 사이클 6 — 접수 완료 메시지에 현재 재고 수량 포함
    def test_reserve_shows_current_inventory(self):
        ctrl, sample_repo, order_repo, inventory_repo, view = _make_ctrl(["1", "서울대 연구소", "50"])
        sample_repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        inventory_repo.create({"sample_id": "1", "quantity": "200"})
        messages = []
        view.show_message = lambda msg: messages.append(msg)
        ctrl.run_reserve()
        self.assertTrue(messages, "show_message()가 호출되지 않음")
        self.assertIn("200 ea", messages[0])
