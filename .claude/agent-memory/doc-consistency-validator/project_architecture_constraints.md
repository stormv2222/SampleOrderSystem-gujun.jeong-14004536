---
name: 아키텍처 제약 및 금지 사항
description: 프로젝트 전체에 적용되는 하드 아키텍처 제약 — 구현 검토 시 체크리스트로 활용
type: project
---

## MVC 레이어 규칙

- Controller: `print`/`input` 직접 호출 금지 → 반드시 View 메서드 경유
- View: 비즈니스 로직 없음. Model의 dataclass만 참조 가능 (Repository import 금지)
- Model(Repository): View, Controller import 금지

## 의존 방향

`main.py → Controller → (Repository, View)`

View는 Repository를 모름. Controller만 두 레이어를 모두 참조.

## JSON 라이브러리

- `import json` 금지
- `from json_lib import load, dump` 만 사용
- `json_lib/` 내부 코드 수정 금지

## Repository 무상태(Stateless) 원칙

- 인스턴스에 데이터 캐시 없음
- 매 연산마다 파일 읽기
- 쓰기 연산은 즉시 파일에 반영

## 메뉴 디스패치 컨벤션

- `if/elif` 체인 금지
- dict 기반 커맨드 매핑 사용 (MainController 구현체가 참조 구현)

## MainController 확장 패턴

Phase별로 __init__에 Optional 파라미터 추가:
```python
def __init__(
    self,
    view: MainView,
    sample_ctrl: SampleController | None = None,   # Phase 2 (구현 완료)
    order_ctrl: OrderController | None = None,     # Phase 3 (구현 예정)
    monitoring_ctrl: MonitoringController | None = None,  # Phase 6
    production_ctrl: ProductionController | None = None,  # Phase 5
    release_ctrl: ReleaseController | None = None,        # Phase 5
) -> None: ...
```
None인 항목은 show_not_implemented()로 처리.

순환 import 방지: TYPE_CHECKING 블록 사용 패턴 (main_controller.py 기존 구현 참조).

## Phase별 확장 이력

- Phase 2: sample_ctrl 파라미터 추가, self._menu["1"] 교체 — 구현 완료
- Phase 3: order_ctrl 파라미터 추가, self._menu["2"] 교체 — 검증 완료, 구현 예정

## 테스트 격리

- Repository 테스트: tempfile / tmp_path 사용, 파일 mock 금지
- Controller 테스트: `view.get_input`을 람다로 교체하여 stdin 주입
- `data/` 하위 실제 파일 절대 수정 금지
