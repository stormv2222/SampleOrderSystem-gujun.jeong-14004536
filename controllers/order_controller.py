from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import OrderRepository
    from models.sample import SampleRepository
    from models.inventory import InventoryRepository
    from views.order_view import OrderView


class OrderController:
    def __init__(
        self,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
        inventory_repo: InventoryRepository,
        view: OrderView,
    ) -> None:
        self._order_repo = order_repo
        self._sample_repo = sample_repo
        self._inventory_repo = inventory_repo
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
