from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import OrderRepository
    from models.inventory import InventoryRepository
    from models.production_queue import ProductionQueue
    from views.production_view import ProductionView


class ProductionController:
    def __init__(
        self,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
        production_queue: ProductionQueue,
        view: ProductionView,
    ) -> None:
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._queue = production_queue
        self._view = view

    def run(self) -> None:
        while True:
            tasks = self._queue.list_all()
            self._view.show_queue(tasks)
            choice = self._view.get_input("완료 처리할 주문 ID (0: 뒤로): ")
            if choice == "0":
                break
            try:
                order_id = int(choice)
            except ValueError:
                self._view.show_error("올바른 주문 ID를 입력하세요.")
                continue
            self._complete_production_by_id(order_id)

    def _complete_production_by_id(self, order_id: int) -> None:
        task = None
        for t in self._queue.list_all():
            if t.order_id == order_id:
                task = t
                break
        if task is None:
            self._view.show_error("생산 큐에 해당 주문이 없습니다.")
            return
        self._queue.remove_by_order_id(order_id)
        self._inventory_repo.add_quantity(task.sample_id, task.actual_quantity)
        self._order_repo.update(order_id, {"status": "CONFIRMED"})
        self._view.show_message(
            f"생산 완료. 주문 ID {order_id}이 CONFIRMED 상태로 전환되었습니다.\n"
            f"   재고 {task.actual_quantity} ea 추가됨."
        )
