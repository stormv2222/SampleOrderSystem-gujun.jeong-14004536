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
