from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import OrderRepository
    from models.sample import SampleRepository
    from models.inventory import InventoryRepository
    from models.production_queue import ProductionQueue, ProductionTask
    from views.order_view import OrderView


class OrderController:
    def __init__(
        self,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
        inventory_repo: InventoryRepository,
        production_queue: ProductionQueue,
        view: OrderView,
    ) -> None:
        self._order_repo = order_repo
        self._sample_repo = sample_repo
        self._inventory_repo = inventory_repo
        self._production_queue = production_queue
        self._view = view

    def run_reserve(self) -> None:
        """주문 접수 흐름. 시료 ID 검증 후 RESERVED 주문 생성."""
        self._view.show_reserve_prompt()
        sample_id = self._view.get_input("시료 ID: ")

        sample = self._sample_repo.read_one(int(sample_id))
        if sample is None:
            self._view.show_error("존재하지 않는 시료 ID입니다.")
            return

        customer = self._view.get_input("고객명: ")
        quantity = self._view.get_input("주문 수량: ")
        order = self._order_repo.create({
            "sample_id": sample_id,
            "customer": customer,
            "quantity": quantity,
        })

        inv = self._inventory_repo.find_by_sample_id(int(sample_id))
        current_qty = int(inv["quantity"]) if inv else 0
        self._view.show_message(
            f"주문이 접수되었습니다. (주문 ID: {order['id']}, 상태: RESERVED)\n"
            f"   현재 재고: {current_qty} ea"
        )

    def _calc_production(self, shortage: int, yield_rate: float, avg_time: int) -> tuple[int, int]:
        actual_qty = math.ceil(shortage / (yield_rate * 0.9))
        total_time = avg_time * actual_qty
        return actual_qty, total_time
