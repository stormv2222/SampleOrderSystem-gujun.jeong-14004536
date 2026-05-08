class OrderView:
    def show_reserve_prompt(self) -> None:
        """주문 접수 화면 헤더 출력."""
        print("=== 주문 접수 ===")

    def get_input(self, prompt: str) -> str:
        """사용자 입력 수신. strip() 처리."""
        return input(prompt).strip()

    def show_order_list(self, orders: list[dict], title: str = "주문 목록") -> None:
        """주문 목록 출력. 비어 있으면 '접수된 주문 없음' 출력."""
        if not orders:
            print("접수된 주문 없음")
            return
        print(f"[{title}] 총 {len(orders)}건")
        for o in orders:
            print(
                f"  주문 ID: {o['id']} | 시료 ID: {o['sample_id']} | "
                f"고객: {o['customer']} | 수량: {o['quantity']} | 상태: {o['status']}"
            )

    def show_order(self, order: dict) -> None:
        """단건 주문 정보 출력."""
        print(
            f"주문 ID: {order['id']} | 시료 ID: {order['sample_id']} | "
            f"고객: {order['customer']} | 수량: {order['quantity']} | 상태: {order['status']}"
        )

    def show_message(self, message: str) -> None:
        print(f">> {message}")

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")

    def show_approve_menu(self) -> None:
        print("[1] 승인  [2] 거절 > ", end="")

    def show_shortage_confirm(self, shortage: int, actual_qty: int, total_time: int) -> None:
        print(f"재고 부족 : 부족분 {shortage} ea 승인하시겠습니까? (실 생산량 {actual_qty} ea / {total_time} min)")

    def show_approve_result(self, order_id: int, new_status: str) -> None:
        print(f">> 주문 ID {order_id} 처리 완료 (상태: {new_status})")

    def show_reject_result(self, order_id: int) -> None:
        print(f">> 주문 ID {order_id} 거절 처리 완료")
