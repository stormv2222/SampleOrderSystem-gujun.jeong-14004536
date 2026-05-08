from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.production_queue import ProductionTask


class ProductionView:
    def get_input(self, prompt: str) -> str:
        return input(prompt).strip()

    def show_queue(self, tasks: list[ProductionTask]) -> None:
        print("=== 생산 라인 ===")
        print("[현재 생산 큐]")
        if not tasks:
            print("  대기 중인 생산 작업이 없습니다.")
            return
        for i, t in enumerate(tasks, 1):
            print(
                f"  순번 {i} | 주문 ID: {t.order_id} | 시료 ID: {t.sample_id}"
                f" | 실 생산량: {t.actual_quantity} ea | 예상 시간: {t.total_time} min"
            )

    def show_message(self, message: str) -> None:
        print(f">> {message}")

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")
