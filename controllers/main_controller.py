from typing import Callable
from views.main_view import MainView


class MainController:
    def __init__(self, view: MainView) -> None:
        self._view = view
        self._menu: dict[str, tuple[str, Callable | None]] = {
            "1": ("시료 관리",      None),
            "2": ("주문 접수",      None),
            "3": ("주문 승인/거절", None),
            "4": ("모니터링",       None),
            "5": ("출고 처리",      None),
            "6": ("생산 라인",      None),
            "0": ("종료",           None),
        }

    def run(self) -> None:
        while True:
            self._view.show_menu({k: v[0] for k, v in self._menu.items()})
            choice = self._view.get_input()
            if choice == "0":
                break
            elif choice in self._menu:
                label, action = self._menu[choice]
                if action is None:
                    self._view.show_not_implemented()
                else:
                    action()
            else:
                self._view.show_invalid()
