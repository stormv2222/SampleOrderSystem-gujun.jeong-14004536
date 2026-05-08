import io
import sys
from unittest.mock import patch

from views.main_view import MainView
from controllers.main_controller import MainController


def _set_inputs(view: MainView, *values: str) -> None:
    it = iter(values)
    view.get_input = lambda prompt="선택 > ": next(it)


class TestMainController:

    # 사이클 1: "0" 입력 시 루프 종료
    def test_exit_on_zero(self):
        view = MainView()
        _set_inputs(view, "0")
        ctrl = MainController(view)
        ctrl.run()  # StopIteration 없이 정상 종료되어야 함

    # 사이클 2: 유효하지 않은 입력 → show_invalid() 호출
    def test_invalid_input_shows_error(self):
        view = MainView()
        _set_inputs(view, "9", "0")   # 잘못된 입력 → 오류 → 종료
        messages = []
        view.show_invalid = lambda: messages.append("invalid")
        MainController(view).run()
        assert "invalid" in messages

    # 사이클 3: 유효한 메뉴 항목(1~6) → show_not_implemented() 호출
    def test_not_implemented_for_valid_menu(self):
        view = MainView()
        _set_inputs(view, "1", "0")
        shown = []
        view.show_not_implemented = lambda: shown.append(True)
        MainController(view).run()
        assert shown

    # 사이클 4: show_menu 출력에 모든 메뉴 항목 포함
    def test_show_menu_contains_all_items(self):
        view = MainView()
        _set_inputs(view, "0")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            MainController(view).run()
            output = mock_out.getvalue()
        for label in ["시료 관리", "주문 접수", "주문 승인/거절",
                      "모니터링", "출고 처리", "생산 라인", "종료"]:
            assert label in output, f"'{label}'이 메뉴 출력에 없음"

    # 사이클 7 — sample_ctrl 주입 시 "1" 입력이 sample_ctrl.run() 호출
    def test_sample_ctrl_is_called_on_menu_1(self):
        view = MainView()
        _set_inputs(view, "1", "0")
        called = []

        class FakeSampleCtrl:
            def run(self):
                called.append(True)

        ctrl = MainController(view, sample_ctrl=FakeSampleCtrl())
        ctrl.run()
        assert called, "sample_ctrl.run()이 호출되지 않음"

    # 사이클 7 — order_ctrl 주입 시 "2" 입력이 order_ctrl.run_reserve() 호출
    def test_order_ctrl_is_called_on_menu_2(self):
        view = MainView()
        _set_inputs(view, "2", "0")
        called = []

        class FakeOrderCtrl:
            def run_reserve(self):
                called.append(True)

        ctrl = MainController(view, order_ctrl=FakeOrderCtrl())
        ctrl.run()
        assert called, "order_ctrl.run_reserve()가 호출되지 않음"

    # 사이클 9 — order_ctrl 주입 시 "3" 입력이 order_ctrl.run_approve() 호출
    def test_order_ctrl_run_approve_is_called_on_menu_3(self):
        view = MainView()
        _set_inputs(view, "3", "0")
        called = []

        class FakeOrderCtrl:
            def run_reserve(self):
                pass
            def run_approve(self):
                called.append(True)

        ctrl = MainController(view, order_ctrl=FakeOrderCtrl())
        ctrl.run()
        assert called, "order_ctrl.run_approve()가 호출되지 않음"

    # 사이클 12 — production_ctrl 주입 시 "6" 입력이 production_ctrl.run() 호출
    def test_production_ctrl_run_is_called_on_menu_6(self):
        view = MainView()
        _set_inputs(view, "6", "0")
        called = []

        class FakeProductionCtrl:
            def run(self):
                called.append(True)

        ctrl = MainController(view, production_ctrl=FakeProductionCtrl())
        ctrl.run()
        assert called, "production_ctrl.run()이 호출되지 않음"

    # 사이클 13 — release_ctrl 주입 시 "5" 입력이 release_ctrl.run() 호출
    def test_release_ctrl_run_is_called_on_menu_5(self):
        view = MainView()
        _set_inputs(view, "5", "0")
        called = []

        class FakeReleaseCtrl:
            def run(self):
                called.append(True)

        ctrl = MainController(view, release_ctrl=FakeReleaseCtrl())
        ctrl.run()
        assert called, "release_ctrl.run()이 호출되지 않음"

    # Bundle D — monitoring_ctrl 주입 시 "4" 입력이 monitoring_ctrl.run() 호출
    def test_monitoring_ctrl_run_is_called_on_menu_4(self):
        view = MainView()
        _set_inputs(view, "4", "0")
        called = []

        class FakeMonitoringCtrl:
            def run(self):
                called.append(True)

        ctrl = MainController(view, monitoring_ctrl=FakeMonitoringCtrl())
        ctrl.run()
        assert called, "monitoring_ctrl.run()이 호출되지 않음"

    # 사이클 8 — dummy_ctrl 주입 시 "7" 입력이 dummy_ctrl.run() 호출
    def test_dummy_ctrl_run_is_called_on_menu_7(self):
        view = MainView()
        _set_inputs(view, "7", "0")
        called = []

        class FakeDummyCtrl:
            def run(self):
                called.append(True)

        ctrl = MainController(view, dummy_ctrl=FakeDummyCtrl())
        ctrl.run()
        assert called, "dummy_ctrl.run()이 호출되지 않음"

    # 사이클 8 — 메뉴 출력에 "더미 데이터 생성" 포함
    def test_show_menu_contains_dummy_data_label(self):
        view = MainView()
        _set_inputs(view, "0")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            class FakeDummyCtrl:
                def run(self): pass
            MainController(view, dummy_ctrl=FakeDummyCtrl()).run()
            output = mock_out.getvalue()
        assert "더미 데이터 생성" in output, "'더미 데이터 생성'이 메뉴 출력에 없음"
