import random


class IDGenerator:
    def __init__(self, start: int = 10001, count: int = 4096) -> None:
        self.available_ids: list[int] = list(range(start, start + count))
        random.shuffle(self.available_ids)

    def next_id(self) -> int:
        if not self.available_ids:
            error = "No IDs left to allocate"
            raise RuntimeError(error)
        return self.available_ids.pop()
