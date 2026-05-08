import pytest
from models.order import OrderRepository
from models.inventory import InventoryRepository
from controllers.release_controller import ReleaseController


class FakeReleaseView:
    def __init__(self, inputs):
        self._inputs = iter(inputs)
        self.messages = []
        self.errors = []
        self.confirmed_shown = []

    def get_input(self, prompt: str) -> str:
        return next(self._inputs)

    def show_confirmed_orders(self, orders) -> None:
        self.confirmed_shown.append(list(orders))

    def show_message(self, message: str) -> None:
        self.messages.append(message)

    def show_error(self, message: str) -> None:
        self.errors.append(message)


def make_order(order_repo, status="CONFIRMED", sample_id=1, quantity=50, customer="테스트"):
    return order_repo.create(
        {"sample_id": sample_id, "customer": customer, "quantity": quantity, "status": status}
    )


class TestReleaseController:

    # 사이클 8 — CONFIRMED → RELEASE 전환
    def test_release_sets_release_status(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        order = make_order(order_repo, status="CONFIRMED")

        view = FakeReleaseView([str(order["id"]), "0"])
        ctrl = ReleaseController(order_repo, inventory_repo, view)
        ctrl.run()

        updated = order_repo.read_one(int(order["id"]))
        assert updated["status"] == "RELEASE"
        assert any("RELEASE" in m for m in view.messages)

    # 사이클 9 — RESERVED/PRODUCING 주문 → show_error, 상태 변경 없음
    def test_release_non_confirmed_order(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        order = make_order(order_repo, status="RESERVED")

        view = FakeReleaseView([str(order["id"]), "0"])
        ctrl = ReleaseController(order_repo, inventory_repo, view)
        ctrl.run()

        updated = order_repo.read_one(int(order["id"]))
        assert updated["status"] == "RESERVED"
        assert len(view.errors) >= 1

    # 사이클 10 — 존재하지 않는 주문 ID → show_error
    def test_release_nonexistent_order(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))

        view = FakeReleaseView(["999", "0"])
        ctrl = ReleaseController(order_repo, inventory_repo, view)
        ctrl.run()

        assert len(view.errors) >= 1

    # 사이클 11 — CONFIRMED 주문 없을 때 show_confirmed_orders([]) 호출
    def test_show_confirmed_orders_empty(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))

        view = FakeReleaseView(["0"])
        ctrl = ReleaseController(order_repo, inventory_repo, view)
        ctrl.run()

        assert len(view.confirmed_shown) >= 1
        assert view.confirmed_shown[0] == []
