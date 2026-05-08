import os
import sys
from datetime import datetime


class MonitoringView:
    def get_input(self, prompt: str) -> str:
        return input(prompt).strip()

    def show_dashboard(
        self,
        orders: list[dict],
        inventories: list[dict],
        samples: list[dict],
    ) -> None:
        self._clear()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"=== 모니터링 대시보드 === (최종 갱신: {now})")
        print()
        self._print_order_status(orders)
        print()
        self._print_inventory_status(inventories, samples, orders)

    def show_message(self, message: str) -> None:
        print(f">> {message}")

    def _clear(self) -> None:
        os.system("cls" if sys.platform == "win32" else "clear")

    def _print_order_status(self, orders: list[dict]) -> None:
        print("[주문 현황]")
        counts = {"RESERVED": 0, "PRODUCING": 0, "CONFIRMED": 0, "RELEASE": 0}
        for o in orders:
            status = o.get("status", "")
            if status in counts:
                counts[status] += 1
        for status, count in counts.items():
            print(f"  {status:<10}:  {count}건")

    def _print_inventory_status(
        self,
        inventories: list[dict],
        samples: list[dict],
        orders: list[dict],
    ) -> None:
        print("[재고 현황]")
        print(f"  {'시료명':<12} | {'재고':^5} | 상태")
        sample_map = {s["id"]: s.get("name", "") for s in samples}
        for inv in inventories:
            sid = inv["sample_id"]
            qty = int(inv["quantity"])
            name = sample_map.get(sid, f"시료 {sid}")
            status = self._stock_status(sid, qty, orders)
            print(f"  {name:<12} | {qty:^5} | {status}")

    @staticmethod
    def _stock_status(sample_id: str, qty: int, orders: list[dict]) -> str:
        if qty == 0:
            return "고갈"
        demand = sum(
            int(o["quantity"])
            for o in orders
            if o.get("sample_id") == sample_id
            and o.get("status") in ("RESERVED", "CONFIRMED")
        )
        return "부족" if demand > qty else "여유"
