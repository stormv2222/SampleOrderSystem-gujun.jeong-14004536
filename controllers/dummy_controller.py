from typing import Any
from generator.engine import DummyGenerator
from generator.schema import DEFAULT_SCHEMAS
from views.main_view import MainView


class DummyController:
    def __init__(
        self,
        repos: dict[str, Any],
        view: MainView,
    ) -> None:
        self._repos = repos
        self._view = view

    def run(self) -> None:
        """스키마 선택 → 건수 입력 → 생성 → Repository 저장."""
        self._view.show_message("=== 더미 데이터 생성 ===")
        schema_name = self._view.get_input(
            prompt="스키마 선택 (sample / order / inventory): "
        )
        count_str = self._view.get_input(prompt="생성할 건수: ")
        self.auto_generate_and_insert(schema_name, int(count_str))

    def auto_generate_and_insert(self, schema_name: str, count: int) -> None:
        gen = DummyGenerator(DEFAULT_SCHEMAS[schema_name])
        batch = gen.generate_batch(count)
        repo = self._repos[schema_name]
        for fields in batch:
            repo.create(fields)
        self._view.show_message(f"{count}건의 {schema_name} 더미 데이터를 추가했습니다.")
