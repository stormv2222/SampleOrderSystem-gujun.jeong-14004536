class SampleView:
    def show_menu(self) -> None:
        print("=== 시료 관리 ===")
        print("  1. 시료 등록")
        print("  2. 시료 조회")
        print("  3. 시료 검색")
        print("  0. 뒤로")

    def get_input(self, prompt: str) -> str:
        return input(prompt).strip()

    def show_sample_list(self, samples: list[dict]) -> None:
        if not samples:
            print("등록된 시료 없음")
            return
        print(f"[시료 목록] 총 {len(samples)}건")
        for s in samples:
            print(f"  ID: {s['id']} | 이름: {s['name']} | 생산시간: {s['avg_production_time']}분 | 수율: {s['yield_rate']}")

    def show_sample(self, sample: dict) -> None:
        print(f"  ID: {sample['id']} | 이름: {sample['name']} | 생산시간: {sample['avg_production_time']}분 | 수율: {sample['yield_rate']}")

    def show_search_menu(self) -> None:
        print("검색 기준:")
        print("  1. ID")
        print("  2. 이름")
        print("  3. 평균 생산시간")
        print("  4. 수율")

    def show_message(self, message: str) -> None:
        print(message)

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")
