import io
import unittest
from unittest.mock import patch

from views.sample_view import SampleView


class TestSampleView(unittest.TestCase):

    # 사이클 5 — 목록 출력 형식: ID, 이름, 생산시간, 수율 포함
    def test_show_sample_list_output_format(self):
        view = SampleView()
        samples = [{"id": "1", "name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"}]
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            view.show_sample_list(samples)
            output = mock_out.getvalue()
        self.assertIn("ID: 1", output)
        self.assertIn("A형 시료", output)
        self.assertIn("30분", output)
        self.assertIn("0.9", output)

    # 사이클 5 — 빈 목록 → "등록된 시료 없음"
    def test_show_sample_list_empty(self):
        view = SampleView()
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            view.show_sample_list([])
            output = mock_out.getvalue()
        self.assertIn("등록된 시료 없음", output)
