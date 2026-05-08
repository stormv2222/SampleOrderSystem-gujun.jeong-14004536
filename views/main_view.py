class MainView:
    def show_menu(self, menu: dict[str, str]) -> None:
        print("=== S-Semi 시료 생산 주문 관리 시스템 ===")
        print()
        non_zero = sorted(k for k in menu if k != "0")
        for key in non_zero:
            print(f"  {key}. {menu[key]}")
        if "0" in menu:
            print(f"  0. {menu['0']}")

    def get_input(self, prompt: str = "선택 > ") -> str:
        return input(prompt).strip()

    def show_invalid(self) -> None:
        print("[오류] 올바른 번호를 입력하세요.")

    def show_not_implemented(self) -> None:
        print("[준비 중] 이 기능은 아직 구현되지 않았습니다.")

    def show_message(self, message: str) -> None:
        print(f">> {message}")
