class ReleaseView:
    def get_input(self, prompt: str) -> str:
        return input(prompt).strip()

    def show_confirmed_orders(self, orders: list[dict]) -> None:
        print("=== 출고 처리 ===")
        print("[출고 대기 주문]")
        if not orders:
            print("  출고 대기 주문이 없습니다.")
            return
        for o in orders:
            print(
                f"  주문 ID: {o['id']} | 시료 ID: {o['sample_id']}"
                f" | 고객: {o['customer']} | 수량: {o['quantity']}"
            )

    def show_message(self, message: str) -> None:
        print(f">> {message}")

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")
