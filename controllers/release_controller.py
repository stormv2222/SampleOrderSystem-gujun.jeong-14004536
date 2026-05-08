from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import OrderRepository
    from models.inventory import InventoryRepository
    from views.release_view import ReleaseView


class ReleaseController:
    def __init__(
        self,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
        view: ReleaseView,
    ) -> None:
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._view = view

    def run(self) -> None:
        while True:
            confirmed = self._order_repo.filter_by_status("CONFIRMED")
            self._view.show_confirmed_orders(confirmed)
            order_id_str = self._view.get_input("출고할 주문 ID (0: 뒤로): ")
            if order_id_str == "0":
                break
            try:
                order_id = int(order_id_str)
            except ValueError:
                self._view.show_error("올바른 주문 ID를 입력하세요.")
                continue
            self._release_order(order_id)

    def _release_order(self, order_id: int) -> None:
        order = self._order_repo.read_one(order_id)
        if order is None or order["status"] != "CONFIRMED":
            self._view.show_error("출고 가능한 주문이 아닙니다.")
            return
        self._order_repo.update(order_id, {"status": "RELEASE"})
        self._view.show_message(
            f"출고 완료. 주문 ID {order_id}이 RELEASE 상태로 전환되었습니다."
        )
