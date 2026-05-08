from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import OrderRepository
    from models.inventory import InventoryRepository
    from models.sample import SampleRepository
    from views.monitoring_view import MonitoringView
    from app.watcher import FileWatcher


class MonitoringController:
    def __init__(
        self,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
        sample_repo: SampleRepository,
        view: MonitoringView,
        watchers: list[FileWatcher],
    ) -> None:
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._sample_repo = sample_repo
        self._view = view
        self._watchers = watchers
        self._refresh_active: bool = False

        for watcher in self._watchers:
            watcher._callback = self._on_file_changed

    def _on_file_changed(self) -> None:
        """파일 변경 감지 시 콜백. 사용자 입력 중에는 갱신 억제."""
        if not self._refresh_active:
            self._do_refresh()

    def _do_refresh(self) -> None:
        """최신 데이터 로드 후 대시보드 재출력. REJECTED 주문 제외."""
        orders = [
            o for o in self._order_repo.read_all()
            if o.get("status") != "REJECTED"
        ]
        inventories = self._inventory_repo.read_all()
        samples = self._sample_repo.read_all()
        self._view.show_dashboard(orders, inventories, samples)

    def run(self) -> None:
        for watcher in self._watchers:
            watcher.start()
        try:
            self._do_refresh()
            while True:
                self._refresh_active = True
                try:
                    cmd = self._view.get_input("명령 (q: 종료) > ")
                finally:
                    self._refresh_active = False

                if cmd.lower() == "q":
                    break
        finally:
            for watcher in self._watchers:
                watcher.stop()
