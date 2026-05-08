import pytest
from models.order import OrderRepository
from models.inventory import InventoryRepository
from models.sample import SampleRepository
from controllers.monitoring_controller import MonitoringController


class FakeMonitoringView:
    def __init__(self, inputs):
        self._inputs = iter(inputs)
        self.dashboards = []  # (orders, inventories, samples) 튜플 리스트
        self.messages = []

    def get_input(self, prompt: str) -> str:
        return next(self._inputs)

    def show_dashboard(self, orders, inventories, samples) -> None:
        self.dashboards.append((list(orders), list(inventories), list(samples)))

    def show_message(self, message: str) -> None:
        self.messages.append(message)


class FakeWatcher:
    def __init__(self):
        self._callback = lambda: None
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


def make_order(order_repo, status="RESERVED", sample_id="1", quantity=50):
    return order_repo.create(
        {"sample_id": sample_id, "customer": "테스트", "quantity": quantity, "status": status}
    )


def make_inventory(inventory_repo, sample_id="1", quantity=10):
    return inventory_repo.create({"sample_id": sample_id, "quantity": quantity})


class TestMonitoringController:

    # TC-1: _do_refresh → show_dashboard 최소 1회 호출
    def test_do_refresh_calls_show_dashboard(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        sample_repo = SampleRepository(str(tmp_path / "sample.json"))
        view = FakeMonitoringView(["q"])
        watcher = FakeWatcher()
        ctrl = MonitoringController(order_repo, inventory_repo, sample_repo, view, [watcher])
        ctrl.run()
        assert len(view.dashboards) >= 1

    # TC-2: REJECTED 주문 집계 제외
    def test_rejected_orders_excluded_from_dashboard(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        sample_repo = SampleRepository(str(tmp_path / "sample.json"))
        make_order(order_repo, status="REJECTED")
        make_order(order_repo, status="RESERVED")
        view = FakeMonitoringView(["q"])
        watcher = FakeWatcher()
        ctrl = MonitoringController(order_repo, inventory_repo, sample_repo, view, [watcher])
        ctrl.run()
        orders_shown = view.dashboards[0][0]
        rejected = [o for o in orders_shown if o.get("status") == "REJECTED"]
        assert len(rejected) == 0, "REJECTED 주문이 대시보드에 포함됨"

    # TC-3: 재고 수량 0 → 고갈 조건 데이터 전달
    def test_inventory_passed_with_zero_quantity(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        sample_repo = SampleRepository(str(tmp_path / "sample.json"))
        make_inventory(inventory_repo, quantity=0)
        view = FakeMonitoringView(["q"])
        watcher = FakeWatcher()
        ctrl = MonitoringController(order_repo, inventory_repo, sample_repo, view, [watcher])
        ctrl.run()
        invs = view.dashboards[0][1]
        assert int(invs[0]["quantity"]) == 0

    # TC-4: 재고 부족 조건 — RESERVED 주문 수량 > 재고
    def test_inventory_shortage_data_passed_correctly(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        sample_repo = SampleRepository(str(tmp_path / "sample.json"))
        make_inventory(inventory_repo, sample_id="1", quantity=10)
        make_order(order_repo, status="RESERVED", sample_id="1", quantity=50)
        view = FakeMonitoringView(["q"])
        watcher = FakeWatcher()
        ctrl = MonitoringController(order_repo, inventory_repo, sample_repo, view, [watcher])
        ctrl.run()
        orders_shown, invs_shown, _ = view.dashboards[0]
        assert int(invs_shown[0]["quantity"]) == 10
        reserved = [o for o in orders_shown if o["status"] == "RESERVED"]
        assert len(reserved) == 1

    # TC-5: Watcher 시작/정지 확인
    def test_watchers_started_and_stopped(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        sample_repo = SampleRepository(str(tmp_path / "sample.json"))
        view = FakeMonitoringView(["q"])
        w1 = FakeWatcher()
        w2 = FakeWatcher()
        ctrl = MonitoringController(order_repo, inventory_repo, sample_repo, view, [w1, w2])
        ctrl.run()
        assert w1.started and w1.stopped
        assert w2.started and w2.stopped

    # TC-6: _on_file_changed → refresh_active=False 시 _do_refresh 호출
    def test_on_file_changed_triggers_refresh(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        sample_repo = SampleRepository(str(tmp_path / "sample.json"))
        view = FakeMonitoringView(["q"])
        watcher = FakeWatcher()
        ctrl = MonitoringController(order_repo, inventory_repo, sample_repo, view, [watcher])
        ctrl.run()
        initial_count = len(view.dashboards)
        ctrl._on_file_changed()
        assert len(view.dashboards) == initial_count + 1

    # TC-7: _on_file_changed → refresh_active=True 시 갱신 억제
    def test_on_file_changed_suppressed_when_refresh_active(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        sample_repo = SampleRepository(str(tmp_path / "sample.json"))
        view = FakeMonitoringView(["q"])
        watcher = FakeWatcher()
        ctrl = MonitoringController(order_repo, inventory_repo, sample_repo, view, [watcher])
        ctrl.run()
        ctrl._refresh_active = True
        count_before = len(view.dashboards)
        ctrl._on_file_changed()
        assert len(view.dashboards) == count_before
