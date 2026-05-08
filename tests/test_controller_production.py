import pytest
from models.order import OrderRepository
from models.inventory import InventoryRepository
from models.production_queue import ProductionQueue, ProductionTask
from controllers.production_controller import ProductionController


class FakeProductionView:
    def __init__(self, inputs):
        self._inputs = iter(inputs)
        self.messages = []
        self.errors = []
        self.queues_shown = []

    def get_input(self, prompt: str) -> str:
        return next(self._inputs)

    def show_queue(self, tasks) -> None:
        self.queues_shown.append(list(tasks))

    def show_message(self, message: str) -> None:
        self.messages.append(message)

    def show_error(self, message: str) -> None:
        self.errors.append(message)


def make_order(order_repo, sample_id=1, status="PRODUCING", quantity=50, customer="테스트"):
    return order_repo.create(
        {"sample_id": sample_id, "customer": customer, "quantity": quantity, "status": status}
    )


def make_inventory(inventory_repo, sample_id=1, quantity=0):
    return inventory_repo.create({"sample_id": sample_id, "quantity": quantity})


class TestProductionController:

    # 사이클 4 — 생산 완료 처리: PRODUCING → CONFIRMED, 재고 actual_quantity 증가
    def test_complete_production_sets_confirmed(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        order = make_order(order_repo)
        make_inventory(inventory_repo, quantity=10)
        q = ProductionQueue()
        q.enqueue(ProductionTask(order_id=int(order["id"]), sample_id=1, actual_quantity=56, total_time=1680))

        view = FakeProductionView([str(order["id"]), "0"])
        ctrl = ProductionController(order_repo, inventory_repo, q, view)
        ctrl.run()

        updated = order_repo.read_one(int(order["id"]))
        assert updated["status"] == "CONFIRMED"
        inv = inventory_repo.find_by_sample_id(1)
        assert int(inv["quantity"]) == 66  # 10 + 56

    # 사이클 5 — 큐에 없는 주문 ID → show_error
    def test_complete_production_invalid_order_id(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        q = ProductionQueue()

        view = FakeProductionView(["999", "0"])
        ctrl = ProductionController(order_repo, inventory_repo, q, view)
        ctrl.run()

        assert len(view.errors) >= 1

    # 사이클 6 — 완료 처리 후 큐에서 제거
    def test_complete_production_removes_task_from_queue(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        order = make_order(order_repo)
        make_inventory(inventory_repo)
        q = ProductionQueue()
        q.enqueue(ProductionTask(order_id=int(order["id"]), sample_id=1, actual_quantity=56, total_time=1680))

        view = FakeProductionView([str(order["id"]), "0"])
        ctrl = ProductionController(order_repo, inventory_repo, q, view)
        ctrl.run()

        assert q.is_empty()

    # 사이클 7 — run() 호출 시 show_queue 최소 1회 호출
    def test_show_queue_called_on_run(self, tmp_path):
        order_repo = OrderRepository(str(tmp_path / "order.json"))
        inventory_repo = InventoryRepository(str(tmp_path / "inventory.json"))
        q = ProductionQueue()

        view = FakeProductionView(["0"])
        ctrl = ProductionController(order_repo, inventory_repo, q, view)
        ctrl.run()

        assert len(view.queues_shown) >= 1
