import os
import tempfile
import unittest

from models.sample import SampleRepository


class TestSampleRepository(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.path = tmp.name
        tmp.close()
        os.unlink(self.path)          # 파일 없는 상태에서 시작
        self.repo = SampleRepository(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    # 사이클 1 — TC-1: create 후 id 포함, 모든 값 str
    def test_create_returns_record_with_id_and_all_str_values(self):
        record = self.repo.create({
            "name": "A형 시료",
            "avg_production_time": "30",
            "yield_rate": "0.9",
        })
        self.assertIn("id", record)
        for v in record.values():
            self.assertIsInstance(v, str, f"value {v!r} is not str")

    # 사이클 1 — TC-2: create 2회 후 read_all → 2건
    def test_create_twice_then_read_all_returns_two(self):
        self.repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        self.repo.create({"name": "B형 시료", "avg_production_time": "45", "yield_rate": "0.85"})
        records = self.repo.read_all()
        self.assertEqual(len(records), 2)

    # 사이클 2 — TC-3: read_one 존재하는 id → 레코드 반환
    def test_read_one_existing_id_returns_record(self):
        record = self.repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        found = self.repo.read_one(int(record["id"]))
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "A형 시료")

    # 사이클 2 — TC-4: read_one 없는 id → None
    def test_read_one_missing_id_returns_none(self):
        result = self.repo.read_one(9999)
        self.assertIsNone(result)

    # 사이클 3 — TC-5: update 후 read_one으로 변경 확인
    def test_update_modifies_field(self):
        record = self.repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        rid = int(record["id"])
        self.repo.update(rid, {"name": "수정된 시료"})
        updated = self.repo.read_one(rid)
        self.assertEqual(updated["name"], "수정된 시료")

    # 사이클 3 — TC-6: delete 후 read_one → None, 반환값 True
    def test_delete_existing_record(self):
        record = self.repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        rid = int(record["id"])
        result = self.repo.delete(rid)
        self.assertTrue(result)
        self.assertIsNone(self.repo.read_one(rid))

    # 사이클 3 — TC-7: delete 없는 id → False
    def test_delete_missing_id_returns_false(self):
        result = self.repo.delete(9999)
        self.assertFalse(result)

    # 사이클 4 — TC-8: search name 부분 일치
    def test_search_by_name_partial_match(self):
        self.repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        self.repo.create({"name": "B형 시료", "avg_production_time": "45", "yield_rate": "0.85"})
        results = self.repo.search("name", "A형")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "A형 시료")

    # 사이클 4 — TC-9: 파일 없어도 read_all → 빈 리스트, 예외 없음
    def test_read_all_with_no_file_returns_empty(self):
        # setUp에서 이미 파일 없는 상태로 시작
        records = self.repo.read_all()
        self.assertEqual(records, [])

    # 사이클 4 — TC-10: 영속성 — 새 인스턴스로 재로드해도 동일 데이터
    def test_persistence_across_instances(self):
        from models.sample import SampleRepository
        self.repo.create({"name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"})
        new_repo = SampleRepository(self.path)
        records = new_repo.read_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "A형 시료")
