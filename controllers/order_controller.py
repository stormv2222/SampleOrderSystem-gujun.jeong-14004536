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

    def _approve(self, order: dict) -> None:
        """재고 확인 → 충분: CONFIRMED / 부족: PRODUCING + 생산 큐 등록."""
        from models.production_queue import ProductionTask
        sample = self._sample_repo.read_one(int(order["sample_id"]))
        if sample is None:
            self._view.show_error(f"시료 ID {order['sample_id']}를 찾을 수 없습니다.")
            return
        yield_rate = float(sample["yield_rate"])
        avg_time = int(sample["avg_production_time"])
        quantity = int(order["quantity"])

        inv = self._inventory_repo.find_by_sample_id(int(order["sample_id"]))
        stock = int(inv["quantity"]) if inv else 0

        if stock >= quantity:
            self._inventory_repo.subtract_quantity(int(order["sample_id"]), quantity)
            self._order_repo.update(int(order["id"]), {"status": "CONFIRMED"})
            self._view.show_approve_result(int(order["id"]), "CONFIRMED")
        else:
            shortage = quantity - stock
            actual_qty, total_time = self._calc_production(shortage, yield_rate, avg_time)
            self._view.show_shortage_confirm(shortage, actual_qty, total_time)
            confirm = self._view.get_input("확인 (y/n) > ")
            if confirm.lower() == "y":
                task = ProductionTask(
                    order_id=int(order["id"]),
                    sample_id=int(order["sample_id"]),
                    actual_quantity=actual_qty,
                    total_time=total_time,
                )
                self._production_queue.enqueue(task)
                self._order_repo.update(int(order["id"]), {"status": "PRODUCING"})
                self._view.show_approve_result(int(order["id"]), "PRODUCING")
            else:
                self._view.show_message("승인이 취소되었습니다.")

    def _reject(self, order: dict) -> None:
        """주문 상태를 REJECTED로 변경."""
        self._order_repo.update(int(order["id"]), {"status": "REJECTED"})
        self._view.show_reject_result(int(order["id"]))

    def run_approve(self) -> None:
        """RESERVED 주문 목록 표시 → 주문 ID 선택 → 승인/거절 처리."""
        reserved = self._order_repo.filter_by_status("RESERVED")
        self._view.show_order_list(reserved, title="접수 주문 목록")

        raw_id = self._view.get_input("처리할 주문 ID: ")
        if not raw_id.isdigit():
            self._view.show_error("주문 ID는 숫자로 입력하세요.")
            return
        order_id = int(raw_id)
        order = self._order_repo.read_one(order_id)
        if order is None or order["status"] != "RESERVED":
            self._view.show_error("유효하지 않은 주문 ID입니다.")
            return

        self._view.show_approve_menu()
        action = self._view.get_input("[1] 승인  [2] 거절 > ")
        if action == "1":
            self._approve(order)
        elif action == "2":
            self._reject(order)
        else:
            self._view.show_error("올바른 번호를 입력하세요.")

    def run_reject(self) -> None:
        """run_approve와 동일 진입점."""
        self.run_approve()
