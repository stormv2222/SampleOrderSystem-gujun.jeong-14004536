from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from views.main_view import MainView

if TYPE_CHECKING:
    from controllers.sample_controller import SampleController
    from controllers.order_controller import OrderController
    from controllers.production_controller import ProductionController
    from controllers.release_controller import ReleaseController
    from controllers.monitoring_controller import MonitoringController
    from controllers.dummy_controller import DummyController


class MainController:
    def __init__(
        self,
        view: MainView,
        sample_ctrl: SampleController | None = None,
        order_ctrl: OrderController | None = None,
        production_ctrl: ProductionController | None = None,
        release_ctrl: ReleaseController | None = None,
        monitoring_ctrl: MonitoringController | None = None,
        dummy_ctrl: DummyController | None = None,
    ) -> None:
        self._view = view
        self._menu: dict[str, tuple[str, Callable | None]] = {
            "1": ("시료 관리",        None),
            "2": ("주문 접수",        None),
            "3": ("주문 승인/거절",   None),
            "4": ("모니터링",         None),
            "5": ("출고 처리",        None),
            "6": ("생산 라인",        None),
            "7": ("더미 데이터 생성", None),
            "0": ("종료",             None),
        }
        if sample_ctrl is not None:
            self._menu["1"] = ("시료 관리", sample_ctrl.run)
        if order_ctrl is not None:
            self._menu["2"] = ("주문 접수", order_ctrl.run_reserve)
            if hasattr(order_ctrl, "run_approve"):
                self._menu["3"] = ("주문 승인/거절", order_ctrl.run_approve)
        if monitoring_ctrl is not None:
            self._menu["4"] = ("모니터링", monitoring_ctrl.run)
        if release_ctrl is not None:
            self._menu["5"] = ("출고 처리", release_ctrl.run)
        if production_ctrl is not None:
            self._menu["6"] = ("생산 라인", production_ctrl.run)
        if dummy_ctrl is not None:
            self._menu["7"] = ("더미 데이터 생성", dummy_ctrl.run)

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
