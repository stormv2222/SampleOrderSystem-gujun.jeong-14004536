# Phase 1 세부 설계: 프로젝트 골격 + 메인 메뉴

> **목표**: `python main.py` 실행 시 메인 메뉴가 표시되고, 숫자 입력으로 항목을 선택할 수 있다.
> 아직 구현되지 않은 항목은 "준비 중" 메시지를 출력하고, `0` 입력 시 종료된다.

---

## 생성 파일 목록

```
semicon/
├── main.py
├── views/
│   ├── __init__.py
│   └── main_view.py
├── controllers/
│   ├── __init__.py
│   └── main_controller.py
└── tests/
    ├── __init__.py
    └── test_main_controller.py
```

> `json_lib/`는 [DataPersistence 참조 레포](https://github.com/stormv2222/DataPersistence-gujun.jeong-14004536)에서 복사만 한다. 내용 수정 금지.

---

## 클래스 설계

### `views/main_view.py` — `MainView`

콘솔 출력·입력 전담. 비즈니스 로직 없음.

```python
class MainView:
    def show_menu(self, menu: dict[str, tuple[str, ...]]) -> None:
        """메뉴 항목 출력. key 순서대로 출력하되 '0'은 마지막."""

    def get_input(self, prompt: str = "선택 > ") -> str:
        """사용자 입력 수신. 앞뒤 공백 제거 후 반환."""

    def show_invalid(self) -> None:
        """잘못된 입력 시 오류 메시지 출력."""

    def show_not_implemented(self) -> None:
        """준비 중 항목 선택 시 안내 메시지 출력."""
```

**출력 형식**:
```
=== S-Semi 시료 생산 주문 관리 시스템 ===
  1. 시료 관리
  2. 주문 접수
  3. 주문 승인/거절
  4. 모니터링
  5. 출고 처리
  6. 생산 라인
  0. 종료
선택 >
```

- 헤더(`===...===`) → 빈 줄 → 메뉴 항목(숫자 오름차순, `0`은 최하단) 순서
- 오류 메시지: `"[오류] 올바른 번호를 입력하세요."`
- 준비 중 메시지: `"[준비 중] 이 기능은 아직 구현되지 않았습니다."`

---

### `controllers/main_controller.py` — `MainController`

View에서 입력 수집 → 메뉴 dict로 디스패치. `print`/`input` 직접 호출 금지.

```python
class MainController:
    def __init__(self, view: MainView) -> None:
        self._view = view
        self._menu: dict[str, tuple[str, Callable | None]] = {
            "1": ("시료 관리",      None),
            "2": ("주문 접수",      None),
            "3": ("주문 승인/거절", None),
            "4": ("모니터링",       None),
            "5": ("출고 처리",      None),
            "6": ("생산 라인",      None),
            "0": ("종료",           None),
        }

    def run(self) -> None:
        """메인 메뉴 루프. '0' 입력 시 종료."""
```

**`run()` 흐름**:
```
while True:
    view.show_menu(self._menu)
    choice = view.get_input()

    if choice == "0":
        break
    elif choice in self._menu:
        label, action = self._menu[choice]
        if action is None:
            view.show_not_implemented()
        else:
            action()
    else:
        view.show_invalid()
```

- Phase 2 이후 실제 Controller가 주입되면 `self._menu["1"] = ("시료 관리", sample_ctrl.run)` 형태로 교체
- `MainController.__init__`은 Phase별로 파라미터가 추가됨. Phase 1에서는 `view`만 받음

---

### `main.py`

의존성 조립(Composition Root)만 담당. 비즈니스 로직 없음.

```python
from views.main_view import MainView
from controllers.main_controller import MainController

if __name__ == "__main__":
    view = MainView()
    ctrl = MainController(view)
    ctrl.run()
```

---

## 테스트 설계 — `tests/test_main_controller.py`

**격리 방법**: `view.get_input`을 람다로 교체하여 stdin 주입. `patch('sys.stdout')`으로 출력 캡처.

```python
def _set_inputs(view: MainView, *values: str) -> None:
    it = iter(values)
    view.get_input = lambda prompt="선택 > ": next(it)
```

### TC-1: `0` 입력 시 루프 종료

```python
def test_exit_on_zero(self):
    view = MainView()
    _set_inputs(view, "0")
    ctrl = MainController(view)
    ctrl.run()   # StopIteration 없이 정상 종료되어야 함
```

- 검증: `run()` 반환 이후 예외 없음 (`StopIteration` 발생하면 실패)

### TC-2: 유효하지 않은 입력 → 오류 메시지 출력 후 계속

```python
def test_invalid_input_shows_error(self):
    view = MainView()
    _set_inputs(view, "9", "0")   # 잘못된 입력 → 오류 → 종료
    messages = []
    view.show_invalid = lambda: messages.append("invalid")
    MainController(view).run()
    assert "invalid" in messages
```

### TC-3: 유효한 메뉴 항목(1~6) → 준비 중 메시지 출력

```python
def test_not_implemented_for_valid_menu(self):
    view = MainView()
    _set_inputs(view, "1", "0")
    shown = []
    view.show_not_implemented = lambda: shown.append(True)
    MainController(view).run()
    assert shown
```

### TC-4: `show_menu` 출력에 모든 메뉴 항목 포함

```python
def test_show_menu_contains_all_items(self):
    view = MainView()
    with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
        _set_inputs(view, "0")
        MainController(view).run()
        output = mock_out.getvalue()
    for label in ["시료 관리", "주문 접수", "주문 승인/거절",
                  "모니터링", "출고 처리", "생산 라인", "종료"]:
        assert label in output
```

---

## 의존성 주입 확장 계획 (Phase 2 이후)

Phase 1에서는 `MainController(view)`만으로 동작한다.  
이후 Phase에서 실제 Controller가 추가될 때 `__init__` 시그니처를 아래와 같이 점진적으로 확장한다.

```python
# Phase 2 이후 예시
class MainController:
    def __init__(
        self,
        view: MainView,
        sample_ctrl: SampleController | None = None,   # Phase 2
        order_ctrl: OrderController | None = None,     # Phase 3~4
        monitoring_ctrl: MonitoringController | None = None,  # Phase 6
        production_ctrl: ProductionController | None = None,  # Phase 5
        release_ctrl: ReleaseController | None = None,        # Phase 5
    ) -> None: ...
```

`None`인 항목은 `show_not_implemented()`로 처리되어 Phase 1 동작과 동일하다.

---

## 완료 기준 체크리스트

- [ ] `python main.py` 실행 시 메인 메뉴 출력
- [ ] `1`~`6` 입력 시 "[준비 중]" 메시지 출력
- [ ] `0` 입력 시 프로그램 종료
- [ ] 숫자 범위 외 입력 시 오류 메시지 출력 후 메뉴 재표시
- [ ] `pytest tests/test_main_controller.py` 전체 통과
- [ ] Controller에서 `print`/`input` 직접 호출 없음
