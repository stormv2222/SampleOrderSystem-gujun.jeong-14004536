import os
import tempfile
import unittest

from models.sample import SampleRepository
from views.sample_view import SampleView
from controllers.sample_controller import SampleController


def _make_ctrl(inputs: list[str]) -> tuple[SampleController, SampleRepository, SampleView]:
    """임시 파일 + lambda 입력 주입으로 격리된 컨트롤러 생성."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    path = tmp.name
    tmp.close()
    os.unlink(path)
    repo = SampleRepository(path)
    view = SampleView()
    it = iter(inputs)
    view.get_input = lambda prompt="": next(it)
    ctrl = SampleController(repo, view)
    return ctrl, repo, view


class TestSampleController(unittest.TestCase):

    # 사이클 6 — register: 입력 → repo에 레코드 1건 저장
    def test_register_creates_record(self):
        ctrl, repo, _ = _make_ctrl(["A형 시료", "30", "0.9"])
        ctrl._register()
        records = repo.read_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "A형 시료")

    # 사이클 6 — list: _list() 호출 시 show_sample_list가 호출된다
    def test_list_calls_show_sample_list(self):
        ctrl, repo, view = _make_ctrl([])
        repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        called_with = []
        view.show_sample_list = lambda samples: called_with.append(samples)
        ctrl._list()
        self.assertTrue(called_with, "show_sample_list가 호출되지 않음")
        self.assertEqual(len(called_with[0]), 1)

    # 검색 기준 속성 선택("2"=이름) + 검색어 입력 → 정확히 일치하는 시료만 출력
    def test_search_by_attribute_returns_filtered_results(self):
        ctrl, repo, view = _make_ctrl(["2", "A형 시료"])   # "2"=이름, "A형 시료"=검색어(정확 일치)
        repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        repo.create({"name": "B형 시료", "avg_production_time": "45", "yield_rate": "0.85"})
        results_passed = []
        view.show_sample_list = lambda samples: results_passed.append(samples)
        ctrl._search()
        self.assertEqual(len(results_passed[0]), 1)
        self.assertEqual(results_passed[0][0]["name"], "A형 시료")

    # 잘못된 속성 번호 입력 → show_error() 호출
    def test_search_with_invalid_attribute_shows_error(self):
        ctrl, repo, view = _make_ctrl(["9"])   # 유효하지 않은 속성 번호
        errors = []
        view.show_error = lambda msg: errors.append(msg)
        ctrl._search()
        self.assertTrue(errors, "show_error()가 호출되지 않음")
