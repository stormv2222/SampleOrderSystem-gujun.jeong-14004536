# Phase 2 세부 설계: 시료 관리

> **목표**: 시료를 등록·조회·검색할 수 있다. 등록된 시료는 `data/sample.json`에 저장되며, 프로그램 재시작 후에도 유지된다.

---

## 생성 파일 목록

```
semicon/
├── models/
│   ├── __init__.py
│   └── sample.py                  # Sample dataclass + SampleRepository
├── views/
│   └── sample_view.py             # 시료 등록 입력, 목록·단건 출력, 검색 결과 출력
├── controllers/
│   └── sample_controller.py       # 시료 등록/조회/검색 흐름 조율
└── tests/
    ├── test_model_sample.py
    ├── test_view_sample.py
    └── test_controller_sample.py
```

> `MainController.__init__`에 `sample_ctrl` 파라미터를 추가하고, `"1"` 키의 action을 `sample_ctrl.run`으로 교체한다.

---

## 클래스 설계

### `models/sample.py`

#### `Sample` dataclass

```python
from dataclasses import dataclass

@dataclass
class Sample:
    id: int
    name: str
    avg_production_time: int   # 분 단위 (정수)
    yield_rate: float          # 0.0 ~ 1.0
```

#### `SampleRepository`

```python
from json_lib import load, dump

class SampleRepository:
    def __init__(self, file_path: str = "data/sample.json") -> None:
        self._file_path = file_path

    def _load_raw(self) -> dict:
        """파일이 없으면 {"next_id": 1, "records": []} 반환."""

    def _load(self) -> list[dict]:
        """records 리스트만 반환."""

    def _save(self, raw: dict) -> None:
        """전체 dict를 파일에 저장. dump(raw, self._file_path, indent=2)"""

    def create(self, fields: dict) -> dict:
        """id 자동 부여. fields 예시: {"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"}
        저장 형식: 모든 값은 str. 반환: 저장된 레코드(id 포함)."""

    def read_all(self) -> list[dict]: ...

    def read_one(self, record_id: int) -> dict | None: ...

    def update(self, record_id: int, fields: dict) -> dict | None: ...

    def delete(self, record_id: int) -> bool: ...

    def search(self, key: str, value: str) -> list[dict]:
        """key 필드가 value를 포함(대소문자 구분 없음)하는 레코드 목록 반환."""
```

**파일 저장 형식**:
```json
{
  "next_id": 3,
  "records": [
    {"id": "1", "name": "A형 시료", "avg_production_time": "30", "yield_rate": "0.9"},
    {"id": "2", "name": "B형 시료", "avg_production_time": "45", "yield_rate": "0.85"}
  ]
}
```
- 모든 값은 `str` 타입으로 저장 (`id` 포함)
- `next_id`는 삭제 후에도 재사용하지 않음

---

### `views/sample_view.py` — `SampleView`

```python
class SampleView:
    def show_menu(self) -> None:
        """시료 관리 서브 메뉴 출력."""

    def get_input(self, prompt: str) -> str:
        """사용자 입력 수신. strip() 처리."""

    def show_sample_list(self, samples: list[dict]) -> None:
        """전체 시료 목록 출력. 비어 있으면 "등록된 시료 없음" 출력."""

    def show_sample(self, sample: dict) -> None:
        """단건 시료 정보 출력."""

    def show_message(self, message: str) -> None:
        """일반 메시지 출력."""

    def show_error(self, message: str) -> None:
        """오류 메시지 출력."""

    def show_search_menu(self) -> None:
        """검색 기준 속성 선택 메뉴 출력."""
```

**서브 메뉴 출력 형식**:
```
=== 시료 관리 ===
  1. 시료 등록
  2. 시료 조회
  3. 시료 검색
  0. 뒤로
선택 >
```

**검색 기준 메뉴 출력 형식**:
```
검색 기준:
  1. ID
  2. 이름
  3. 평균 생산시간
  4. 수율
선택 >
```

**시료 목록 출력 형식**:
```
[시료 목록] 총 N건
  ID: 1 | 이름: A형 시료 | 생산시간: 30분 | 수율: 0.9
  ID: 2 | 이름: B형 시료 | 생산시간: 45분 | 수율: 0.85
```

---

### `controllers/sample_controller.py` — `SampleController`

```python
class SampleController:
    def __init__(self, repo: SampleRepository, view: SampleView) -> None:
        self._repo = repo
        self._view = view

    def run(self) -> None:
        """시료 관리 서브 메뉴 루프. '0' 입력 시 메인 메뉴로 복귀."""

    def _register(self) -> None:
        """시료 이름·평균 생산 시간·수율 입력 → repo.create() → 완료 메시지."""

    def _list(self) -> None:
        """repo.read_all() → view.show_sample_list()."""

    def _search(self) -> None:
        """검색 기준 속성 선택 → 검색어 입력 → repo.search(key, value) → view.show_sample_list()."""
```

**`run()` 흐름**:
```
while True:
    view.show_menu()
    choice = view.get_input("선택 > ")
    if choice == "0": break
    elif choice == "1": self._register()
    elif choice == "2": self._list()
    elif choice == "3": self._search()
    else: view.show_error("올바른 번호를 입력하세요.")
```

**`_register()` 흐름**:
```
name     = view.get_input("시료 이름: ")
avg_time = view.get_input("평균 생산 시간(분): ")
yield_r  = view.get_input("수율(0.0~1.0): ")
record   = repo.create({"name": name, "avg_production_time": avg_time, "yield_rate": yield_r})
view.show_message(f"시료가 등록되었습니다. (ID: {record['id']})")
```

**`_search()` 흐름**:
```
SEARCH_KEYS = {"1": "id", "2": "name", "3": "avg_production_time", "4": "yield_rate"}

view.show_search_menu()
key_choice = view.get_input("선택 > ")
if key_choice not in SEARCH_KEYS:
    view.show_error("올바른 번호를 입력하세요.")
    return
key     = SEARCH_KEYS[key_choice]
keyword = view.get_input("검색어: ")
results = repo.search(key, keyword)
view.show_sample_list(results)
```

---

## 테스트 설계

### `tests/test_model_sample.py`

```python
class TestSampleRepository(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.path = tmp.name
        tmp.close()
        os.unlink(self.path)
        self.repo = SampleRepository(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)
```

| TC | 검증 내용 |
|----|-----------|
| TC-1 | `create` 후 반환 레코드에 `id` 포함, 모든 값이 `str` |
| TC-2 | `create` 2회 → `read_all()` 결과 2건 |
| TC-3 | `read_one(존재하는 id)` → 레코드 반환 |
| TC-4 | `read_one(없는 id)` → `None` |
| TC-5 | `update` 후 `read_one`으로 변경 확인 |
| TC-6 | `delete` 후 `read_one` → `None`, 반환값 `True` |
| TC-7 | `delete(없는 id)` → `False` |
| TC-8 | `search("name", "A형")` → 일치하는 시료만 반환 |
| TC-9 | 파일이 없는 상태에서 `read_all()` → 빈 리스트, 예외 없음 |
| TC-10 | 영속성: 새 인스턴스로 재로드 시 동일 데이터 |

### `tests/test_view_sample.py`

```python
# patch('sys.stdout') 으로 출력 캡처

def test_show_sample_list_output_format():
    """목록에 ID, 이름, 생산시간, 수율이 포함되는지 확인."""

def test_show_sample_list_empty():
    """records 빈 리스트 → "등록된 시료 없음" 출력."""
```

### `tests/test_controller_sample.py`

```python
# view.get_input = lambda로 교체, repo는 실제 파일(tmp_path)

def test_register_creates_record():
    """이름·시간·수율 입력 → repo에 레코드 1건 저장."""

def test_list_calls_show_sample_list():
    """_list() 호출 시 view.show_sample_list가 호출된다."""

def test_search_by_attribute_returns_filtered_results():
    """검색 기준 속성 선택(예: "2"=이름) + 검색어 입력 → 해당 속성 포함 시료만 출력."""

def test_search_with_invalid_attribute_shows_error():
    """잘못된 속성 번호 입력 → show_error() 호출."""
```

---

## `MainController` 연동

```python
# main.py
sample_repo = SampleRepository()
sample_view = SampleView()
sample_ctrl = SampleController(sample_repo, sample_view)
main_ctrl   = MainController(view=main_view, sample_ctrl=sample_ctrl)

# main_controller.py
self._menu["1"] = ("시료 관리", sample_ctrl.run)
```

---

## 완료 기준 체크리스트

- [ ] `시료 관리` 메뉴 진입 → 서브 메뉴 출력
- [ ] 시료 등록 후 `data/sample.json` 생성 및 내용 확인
- [ ] 프로그램 재시작 후 등록된 시료 목록 유지
- [ ] 시료 검색 시 기준 속성(ID·이름·평균 생산시간·수율) 선택 메뉴 출력
- [ ] 선택한 속성으로 검색어 부분 일치 검색 동작 확인
- [ ] 잘못된 속성 번호 입력 시 오류 메시지 출력
- [ ] `pytest tests/test_model_sample.py` 전체 통과
- [ ] `pytest tests/test_view_sample.py` 전체 통과
- [ ] `pytest tests/test_controller_sample.py` 전체 통과
- [ ] Controller에서 `print`/`input` 직접 호출 없음
- [ ] `import json` 미사용 (`json_lib` 사용)
