from collections import deque
from dataclasses import dataclass


@dataclass
class ProductionTask:
    order_id: int
    sample_id: int
    actual_quantity: int
    total_time: int


class ProductionQueue:
    def __init__(self) -> None:
        self._queue: deque[ProductionTask] = deque()

    def enqueue(self, task: ProductionTask) -> None:
        self._queue.append(task)

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)

    def peek(self) -> ProductionTask | None:
        return self._queue[0] if self._queue else None

    def dequeue(self) -> ProductionTask | None:
        return self._queue.popleft() if self._queue else None

    def list_all(self) -> list[ProductionTask]:
        return list(self._queue)
