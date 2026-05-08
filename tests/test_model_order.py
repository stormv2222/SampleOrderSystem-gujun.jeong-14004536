import os
import tempfile
import unittest

from models.order import OrderRepository


class TestOrderRepository(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.path = tmp.name
        tmp.close()
        os.unlink(self.path)
        self.repo = OrderRepository(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    # TC-1: create 시 status가 "RESERVED"로 저장됨
    def test_create_sets_status_to_reserved(self):
        record = self.repo.create({
            "sample_id": "1",
            "customer": "서울대 연구소",
            "quantity": "50",
        })
        self.assertEqual(record["status"], "RESERVED")

    # TC-2: create 후 반환 레코드에 id 포함, 모든 값 str
    def test_create_returns_record_with_id_and_all_str_values(self):
        record = self.repo.create({
            "sample_id": "1",
            "customer": "서울대 연구소",
            "quantity": "50",
        })
        self.assertIn("id", record)
        for v in record.values():
            self.assertIsInstance(v, str, f"value {v!r} is not str")

    # TC-3: read_all() → 전체 주문 목록 반환
    def test_read_all_returns_all_orders(self):
        self.repo.create({"sample_id": "1", "customer": "고객A", "quantity": "10"})
        self.repo.create({"sample_id": "2", "customer": "고객B", "quantity": "20"})
        records = self.repo.read_all()
        self.assertEqual(len(records), 2)

    # TC-4: filter_by_status("RESERVED") → 해당 상태 주문만 반환
    def test_filter_by_status_returns_only_matching_status(self):
        self.repo.create({"sample_id": "1", "customer": "고객A", "quantity": "10"})
        r2 = self.repo.create({"sample_id": "2", "customer": "고객B", "quantity": "20"})
        self.repo.update(int(r2["id"]), {"status": "CONFIRMED"})

        results = self.repo.filter_by_status("RESERVED")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "RESERVED")

    # TC-5: update(id, {"status": "CONFIRMED"}) → 상태 변경 확인
    def test_update_status_changes_status_field(self):
        record = self.repo.create({
            "sample_id": "1",
            "customer": "서울대 연구소",
            "quantity": "50",
        })
        rid = int(record["id"])
        updated = self.repo.update(rid, {"status": "CONFIRMED"})
        self.assertEqual(updated["status"], "CONFIRMED")

    # TC-6: 파일 없는 상태에서 read_all() → 빈 리스트, 예외 없음
    def test_read_all_with_no_file_returns_empty(self):
        records = self.repo.read_all()
        self.assertEqual(records, [])

    # 추가: status 명시하면 명시한 값으로 저장
    def test_create_with_explicit_status_uses_given_status(self):
        record = self.repo.create({
            "sample_id": "1",
            "customer": "고객A",
            "quantity": "10",
            "status": "PRODUCING",
        })
        self.assertEqual(record["status"], "PRODUCING")

    # 추가: search by key/value
    def test_search_returns_matching_records(self):
        self.repo.create({"sample_id": "1", "customer": "서울대", "quantity": "10"})
        self.repo.create({"sample_id": "1", "customer": "카이스트", "quantity": "20"})
        results = self.repo.search("sample_id", "1")
        self.assertEqual(len(results), 2)
