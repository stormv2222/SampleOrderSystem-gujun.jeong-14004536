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
