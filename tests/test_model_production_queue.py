import unittest
from models.production_queue import ProductionQueue, ProductionTask


class TestProductionQueue(unittest.TestCase):

    def setUp(self):
        self.q = ProductionQueue()
        self.task1 = ProductionTask(order_id=1, sample_id=1, actual_quantity=56, total_time=1680)
        self.task2 = ProductionTask(order_id=2, sample_id=2, actual_quantity=20, total_time=900)

    # TC-7: 빈 큐 → is_empty() == True
    def test_empty_queue_is_empty(self):
        self.assertTrue(self.q.is_empty())

    # TC-1: enqueue 후 size() == 1, is_empty() == False
    def test_enqueue_increases_size(self):
        self.q.enqueue(self.task1)
        self.assertEqual(self.q.size(), 1)
        self.assertFalse(self.q.is_empty())

    # TC-5: 빈 큐 peek() → None
    def test_peek_empty_queue_returns_none(self):
        self.assertIsNone(self.q.peek())

    # TC-2: peek() → 첫 작업 반환, 큐에서 제거하지 않음
    def test_peek_returns_first_without_removing(self):
        self.q.enqueue(self.task1)
        self.q.enqueue(self.task2)
        result = self.q.peek()
        self.assertEqual(result, self.task1)
        self.assertEqual(self.q.size(), 2)  # 제거 없음

    # TC-4: 빈 큐 dequeue() → None
    def test_dequeue_empty_queue_returns_none(self):
        self.assertIsNone(self.q.dequeue())

    # TC-3: dequeue() → FIFO 순서
    def test_dequeue_follows_fifo_order(self):
        self.q.enqueue(self.task1)
        self.q.enqueue(self.task2)
        first = self.q.dequeue()
        second = self.q.dequeue()
        self.assertEqual(first, self.task1)
        self.assertEqual(second, self.task2)
        self.assertTrue(self.q.is_empty())

    # TC-6: list_all() → 삽입 순서와 동일한 목록
    def test_list_all_returns_fifo_order(self):
        self.q.enqueue(self.task1)
        self.q.enqueue(self.task2)
        result = self.q.list_all()
        self.assertEqual(result, [self.task1, self.task2])

    # TC-8: remove_by_order_id → 해당 작업 제거, True 반환
    def test_remove_by_order_id_removes_correct_task(self):
        self.q.enqueue(self.task1)
        self.q.enqueue(self.task2)
        result = self.q.remove_by_order_id(1)
        self.assertTrue(result)
        self.assertEqual(self.q.size(), 1)
        self.assertEqual(self.q.peek().order_id, 2)

    # TC-9: remove_by_order_id 없는 ID → False 반환, 큐 변화 없음
    def test_remove_by_order_id_nonexistent_returns_false(self):
        self.q.enqueue(self.task1)
        result = self.q.remove_by_order_id(99)
        self.assertFalse(result)
        self.assertEqual(self.q.size(), 1)
