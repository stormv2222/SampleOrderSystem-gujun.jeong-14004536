# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

반도체 시료 생산 주문 관리 콘솔 애플리케이션 (Python 3.14).  
요구사항 및 아키텍처 전문은 `docs/SPEC.md`를 참고한다.

## 설계 문서

- 전체 구현 계획: `docs/PLAN.md`
- Phase별 세부 설계: `docs/design/phase{N}.md` (N = 1, 2, …, 7)
  - 각 문서에는 생성 파일 목록, 클래스 시그니처, 테스트 케이스 설계, 완료 기준 체크리스트가 포함된다.
  - 구현 시작 전 반드시 해당 phase의 설계 문서를 확인한다.

## 개발 명령어

```bash
# 테스트 전체 실행
pytest

# 단일 테스트 파일 실행
pytest tests/test_<module>.py

# 단일 테스트 케이스 실행
pytest tests/test_<module>.py::test_<case>

# 첫 번째 실패에서 멈춤
pytest -x
```

## 도메인 모델

핵심 엔티티: `Sample`, `Order`, `Inventory`, `ProductionQueue`

주문 상태 전이:
```
RESERVED → CONFIRMED → RELEASE          (재고 충분)
RESERVED → PRODUCING → CONFIRMED → RELEASE  (재고 부족)
RESERVED → REJECTED                     (거절, 모니터링 제외)
```

생산량 계산 공식 (재고 부족 승인 시):
```python
import math
actual_production = math.ceil(shortage / (yield_rate * 0.9))
total_time = avg_production_time * actual_production
```

엔티티 속성·상태 분류·비즈니스 규칙 세부 내용은 `docs/SPEC.md` → **도메인 모델** / **핵심 비즈니스 규칙** 참고.

## 아키텍처: MVC 패턴

```
semicon/
├── main.py              # 의존성 조립(Composition Root) + run() 호출만 담당
├── models/              # 엔티티(dataclass) + Repository (파일 I/O)
├── views/               # 콘솔 출력·입력 전담 (print/input)
├── controllers/         # 흐름 조율 (View 입력 → Model 조작 → View 출력)
├── generator/           # 테스트용 더미 데이터 생성 엔진
├── app/                 # FileWatcher (백그라운드 파일 감시)
├── json_lib/            # 자체 구현 JSON 라이브러리 — 수정 금지
└── data/                # *.json 데이터 파일
```

**의존 방향**: `main.py → Controller → (Model, View)`. Model ↔ View 간 직접 의존 없음.

**금지 사항**:
- Controller에서 직접 `print` / `input` 호출 금지
- `import json` (표준 라이브러리) 사용 금지 → `from json_lib import load, dump` 사용
- `json_lib/` 내부 코드 수정 금지

폴더 구조·클래스 시그니처·컨벤션 세부 내용은 `docs/SPEC.md` → **아키텍처: MVC 패턴** 참고.

## 데이터 영속성

- JSON 파일 기반 저장 (`data/sample.json`, `data/order.json`, `data/inventory.json`)
- `json_lib.load()` / `json_lib.dump()` 만 사용
- Repository는 **무상태(stateless)** — 매 연산마다 파일을 읽고, 쓰기는 즉시 반영
- 파일이 없으면 `{"next_id": 1, "records": []}` 로 초기화 (예외 없음)
- 테스트 시 `tempfile` 또는 `tmp_path`로 실제 파일과 격리

Repository 메서드 시그니처·파일 구조·에러 처리 세부 내용은 `docs/SPEC.md` → **데이터 영속성** 참고.

## 모니터링 / 실시간 조회

- `app/watcher.py`의 `FileWatcher`가 1초 주기로 파일 변경을 감지 → 콜백 호출 → 화면 자동 갱신
- 사용자 입력 중에는 `_refresh_active` 플래그로 갱신 억제 (`try/finally` 필수)
- `view.show_dashboard()`는 `_clear()` 후 전체 재출력 방식

FileWatcher 구조·흐름·비동기 테스트 패턴 세부 내용은 `docs/SPEC.md` → **모니터링 / 실시간 조회** 참고.

## 테스트 더미 데이터

- `generator/schema.py`: `FieldDef` + `DEFAULT_SCHEMAS` (`sample` / `order` / `inventory`)
- `generator/engine.py`: `DummyGenerator.generate_one()` / `generate_batch(count)` — 모든 반환값은 `str`
- Generator와 Repository는 서로 의존하지 않음 — Controller가 연결
- 정확한 값 대신 **범위·형식·허용 집합**으로 검증 (20회 반복 샘플링 권장)

스키마 정의·Controller 연동·테스트 패턴 세부 내용은 `docs/SPEC.md` → **테스트 더미 데이터 자동 생성** 참고.
