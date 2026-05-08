import random
import string
from generator.schema import FieldDef


class DummyGenerator:
    def __init__(self, schema: list[FieldDef]) -> None:
        self._schema = schema

    def generate_one(self) -> dict:
        """스키마에 따라 레코드 1건 생성. 모든 값은 str 타입."""
        return {field.name: self._generate_value(field.field_type)
                for field in self._schema}

    def generate_batch(self, count: int) -> list[dict]:
        """N건 일괄 생성."""
        return [self.generate_one() for _ in range(count)]

    def _generate_value(self, field_type: str) -> str:
        if field_type == 'int':
            return str(random.randint(1, 100))
        elif field_type == 'name':
            return self._random_name()
        elif field_type == 'string':
            return self._random_string()
        raise ValueError(f"Unknown field_type: {field_type}")

    def _random_name(self) -> str:
        first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve",
                       "Frank", "Grace", "Henry", "Iris", "James"]
        last_names = ["Kim", "Lee", "Park", "Choi", "Jung",
                      "Kang", "Yoon", "Lim", "Han", "Oh"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def _random_string(self) -> str:
        length = random.randint(4, 10)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
