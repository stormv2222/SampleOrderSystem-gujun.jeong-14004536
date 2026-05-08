from models.sample import SampleRepository
from views.sample_view import SampleView


class SampleController:
    def __init__(self, repo: SampleRepository, view: SampleView) -> None:
        self._repo = repo
        self._view = view

    def run(self) -> None:
        """서브 메뉴 루프. '0' 입력 시 복귀."""
        while True:
            self._view.show_menu()
            choice = self._view.get_input("선택 > ")
            if choice == "0":
                break
            elif choice == "1":
                self._register()
            elif choice == "2":
                self._list()
            elif choice == "3":
                self._search()
            else:
                self._view.show_error("올바른 번호를 입력하세요.")

    def _register(self) -> None:
        name     = self._view.get_input("시료 이름: ")
        avg_time = self._view.get_input("평균 생산 시간(분): ")
        yield_r  = self._view.get_input("수율(0.0~1.0): ")
        record   = self._repo.create({"name": name, "avg_production_time": avg_time, "yield_rate": yield_r})
        self._view.show_message(f"시료가 등록되었습니다. (ID: {record['id']})")

    def _list(self) -> None:
        samples = self._repo.read_all()
        self._view.show_sample_list(samples)

    def _search(self) -> None:
        SEARCH_KEYS = {"1": "id", "2": "name", "3": "avg_production_time", "4": "yield_rate"}
        self._view.show_search_menu()
        key_choice = self._view.get_input("선택 > ")
        if key_choice not in SEARCH_KEYS:
            self._view.show_error("올바른 번호를 입력하세요.")
            return
        key = SEARCH_KEYS[key_choice]
        keyword = self._view.get_input("검색어: ")
        results = self._repo.search(key, keyword)
        self._view.show_sample_list(results)
