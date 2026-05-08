import os
import tempfile
import unittest

from models.inventory import InventoryRepository


class TestInventoryRepository(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.path = tmp.name
        tmp.close()
        os.unlink(self.path)
        self.repo = InventoryRepository(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    # TC-1: create 후 find_by_sample_id → 해당 레코드 반환
    def test_create_then_find_by_sample_id_returns_record(self):
        self.repo.create({"sample_id": "1", "quantity": "100"})
        result = self.repo.find_by_sample_id(1)
        self.assertIsNotNone(result)
        self.assertEqual(result["sample_id"], "1")
        self.assertEqual(result["quantity"], "100")

    # TC-2: add_quantity → 수량 증가 확인
    def test_add_quantity_increases_quantity(self):
        self.repo.create({"sample_id": "2", "quantity": "50"})
        updated = self.repo.add_quantity(2, 30)
        self.assertEqual(updated["quantity"], "80")

    # TC-3: subtract_quantity → 수량 차감 확인
    def test_subtract_quantity_decreases_quantity(self):
        self.repo.create({"sample_id": "3", "quantity": "100"})
        updated = self.repo.subtract_quantity(3, 40)
        self.assertEqual(updated["quantity"], "60")

    # TC-4: subtract_quantity 수량 부족 시 ValueError
    def test_subtract_quantity_insufficient_stock_raises_value_error(self):
        self.repo.create({"sample_id": "4", "quantity": "10"})
        with self.assertRaises(ValueError):
            self.repo.subtract_quantity(4, 20)

    # TC-5: 존재하지 않는 sample_id → find_by_sample_id → None
    def test_find_by_sample_id_nonexistent_returns_none(self):
        result = self.repo.find_by_sample_id(9999)
        self.assertIsNone(result)

    # TC-6: 파일 없는 상태에서 read_all() → 빈 리스트, 예외 없음
    def test_read_all_with_no_file_returns_empty(self):
        records = self.repo.read_all()
        self.assertEqual(records, [])

    # 추가: add_quantity 레코드 없으면 신규 생성
    def test_add_quantity_creates_record_when_none_exists(self):
        result = self.repo.add_quantity(5, 25)
        self.assertIsNotNone(result)
        self.assertEqual(result["quantity"], "25")
        self.assertEqual(result["sample_id"], "5")

    # 추가: subtract_quantity 레코드 없으면 None 반환
    def test_subtract_quantity_nonexistent_sample_returns_none(self):
        result = self.repo.subtract_quantity(9999, 10)
        self.assertIsNone(result)
