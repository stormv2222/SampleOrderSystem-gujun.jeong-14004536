# 반도체 시료 생산 주문 관리 시스템 — 구현 계획

> 각 Phase는 완료 시 `python main.py`로 직접 실행하여 해당 기능을 눈으로 확인할 수 있어야 한다.  
> 모든 구현은 TDD(Red → Green → Review) 사이클을 따른다. 자세한 규칙은 `/tdd` 스킬 참고.

---

## Phase 1: 프로젝트 골격 + 메인 메뉴

### 목표

`python main.py` 실행 시 메인 메뉴가 표시되고, 숫자 입력으로 항목을 선택할 수 있다.  
아직 구현되지 않은 항목은 "준비 중" 메시지를 출력하고, `0` 입력 시 종료된다.

### 구현 대상

| 파일 | 내용 |
|------|------|
| `json_lib/` | DataPersistence 참조 레포에서 복사 (수정 금지) |
| `main.py` | 의존성 조립 + `main_controller.run()` 호출 |
| `views/main_view.py` | 메뉴 출력, 입력 수신 |
| `controllers/main_controller.py` | dict 기반 메뉴 루프, 각 항목 진입 |

### 테스트 목록

- `tests/test_main_controller.py`
  - 메뉴 항목 목록이 올바르게 출력된다
  - `0` 입력 시 루프가 종료된다
  - 유효하지 않은 입력 시 오류 메시지를 출력한다

### 실행 확인

```
$ python main.py

=== S-Semi 시료 생산 주문 관리 시스템 ===
  1. 시료 관리
  2. 주문 접수
  3. 주문 승인/거절
  4. 모니터링
  5. 출고 처리
  6. 생산 라인
  0. 종료
선택 > 1
[준비 중] 이 기능은 아직 구현되지 않았습니다.
```

---

## Phase 2: 시료 관리

### 목표

시료를 등록·조회·검색할 수 있다. 등록된 시료는 `data/sample.json`에 저장되며, 프로그램 재시작 후에도 유지된다.

### 구현 대상

| 파일 | 내용 |
|------|------|
| `models/sample.py` | `Sample` dataclass + `SampleRepository` (CRUD + search) |
| `views/sample_view.py` | 시료 등록 입력, 목록·단건 출력, 검색 결과 출력 |
| `controllers/sample_controller.py` | 시료 등록/조회/검색 흐름 조율 |

### 테스트 목록

- `tests/test_model_sample.py`
  - `create`: 시료가 저장되고 id가 자동 부여된다
  - `read_all`: 전체 시료 목록을 반환한다
  - `read_one`: 존재하는 id → 시료 반환, 없는 id → `None`
  - `update`: 특정 필드를 수정하고 저장된다
  - `delete`: 삭제 후 조회 시 `None`
  - `search`: 이름으로 검색하면 일치하는 시료 목록을 반환한다
  - 파일 없는 상태에서 시작해도 오류 없이 동작한다

- `tests/test_view_sample.py`
  - 시료 목록이 올바른 형식으로 출력된다
  - 시료가 없을 때 "등록된 시료 없음" 메시지를 출력한다

- `tests/test_controller_sample.py`
  - 등록 흐름: 입력 → 저장 → 완료 메시지 출력
  - 조회 흐름: `read_all` 호출 → 목록 출력
  - 검색 흐름: 키워드 입력 → 결과 출력

### 실행 확인

```
=== 시료 관리 ===
  1. 시료 등록
  2. 시료 조회
  3. 시료 검색
  0. 뒤로
선택 > 1
시료 이름: A형 시료
평균 생산 시간(분): 30
수율(0.0~1.0): 0.9
>> 시료가 등록되었습니다. (ID: 1)

선택 > 2
[시료 목록] 총 1건
  ID: 1 | 이름: A형 시료 | 생산시간: 30분 | 수율: 0.9
```

---

## Phase 3: 재고 관리 + 주문 접수

### 목표

주문을 접수(`RESERVED`)할 수 있다. 접수 시 해당 시료의 재고를 함께 표시한다.  
재고는 `data/inventory.json`, 주문은 `data/order.json`에 저장된다.

### 구현 대상

| 파일 | 내용 |
|------|------|
| `models/inventory.py` | `Inventory` dataclass + `InventoryRepository` |
| `models/order.py` | `Order` dataclass + `OrderRepository` |
| `views/order_view.py` | 주문 접수 입력, 주문 목록 출력 |
| `controllers/order_controller.py` | 주문 접수(`run_reserve`) 흐름 조율 |

### 테스트 목록

- `tests/test_model_inventory.py`
  - 시료별 재고 수량을 조회한다
  - 재고를 추가·차감할 수 있다
  - 존재하지 않는 시료 ID → `None`

- `tests/test_model_order.py`
  - `create`: 주문이 `RESERVED` 상태로 저장된다
  - `read_all`: 전체 주문 목록을 반환한다
  - `filter_by_status`: 특정 상태의 주문만 반환한다

- `tests/test_controller_order_reserve.py`
  - 접수 흐름: 시료 ID·고객명·수량 입력 → `RESERVED` 주문 생성
  - 존재하지 않는 시료 ID 입력 시 오류 메시지 출력

### 실행 확인

```
=== 주문 접수 ===
시료 ID: 1
고객명: 서울대 연구소
주문 수량: 50
>> 주문이 접수되었습니다. (주문 ID: 1, 상태: RESERVED)
   현재 재고: 0 ea
```

---

## Phase 4: 주문 승인/거절 + 생산 큐

### 목표

접수된 주문(`RESERVED`)에 대해 승인 또는 거절을 처리한다.  
- 재고 충분 → `CONFIRMED`  
- 재고 부족 → 생산 큐 등록 + `PRODUCING`  
- 거절 → `REJECTED`

### 구현 대상

| 파일 | 내용 |
|------|------|
| `models/production_queue.py` | `ProductionTask` dataclass + `ProductionQueue` (FIFO) |
| `controllers/order_controller.py` | 승인(`run_approve`) · 거절(`run_reject`) 흐름 추가 |
| `views/order_view.py` | 재고 부족 확인 메시지, 승인/거절 결과 출력 |

### 테스트 목록

- `tests/test_model_production_queue.py`
  - `enqueue`: 생산 작업이 큐에 추가된다
  - `peek` / `dequeue`: FIFO 순서로 꺼낸다
  - 빈 큐에서 `dequeue` → `None`

- `tests/test_controller_order_approve.py`
  - 재고 충분 시 주문 상태가 `CONFIRMED`로 전환된다
  - 재고 부족 시 부족분·실 생산량·예상 시간 메시지를 출력하고 `PRODUCING`으로 전환된다
  - 거절 시 주문 상태가 `REJECTED`로 전환된다
  - 생산량 계산: `ceil(부족분 / (수율 × 0.9))` 결과가 정확하다

### 실행 확인

```
=== 주문 승인/거절 ===
[접수 주문 목록]
  주문 ID: 1 | 시료: A형 시료 | 고객: 서울대 연구소 | 수량: 50 | 상태: RESERVED

처리할 주문 ID: 1
[1] 승인  [2] 거절 > 1

재고 부족 : 부족분 50 ea 승인하시겠습니까? (실 생산량 56 ea / 1680 min)
확인 (y/n) > y
>> 주문 ID 1이 PRODUCING 상태로 전환되었습니다.
   생산 큐에 등록되었습니다.
```

---

## Phase 5: 생산 라인 + 출고 처리

### 목표

생산 큐를 조회하고 생산 완료를 처리할 수 있다(`PRODUCING` → `CONFIRMED`).  
`CONFIRMED` 주문에 대해 출고를 실행하면 `RELEASE`로 전환된다.  
이 Phase 완료 시 **전체 주문 사이클**이 처음부터 끝까지 동작한다.

### 구현 대상

| 파일 | 내용 |
|------|------|
| `views/production_view.py` | 생산 현황 출력, 생산 완료 입력 |
| `controllers/production_controller.py` | 생산 큐 조회, 생산 완료 처리 흐름 |
| `views/release_view.py` | 출고 대상 주문 출력, 출고 실행 입력 |
| `controllers/release_controller.py` | 출고 처리 흐름 |

### 테스트 목록

- `tests/test_controller_production.py`
  - 생산 큐 목록이 올바르게 출력된다
  - 생산 완료 처리 시 주문 상태가 `PRODUCING` → `CONFIRMED`로 전환된다
  - 재고에 생산 완료 수량이 반영된다

- `tests/test_controller_release.py`
  - `CONFIRMED` 상태 주문 목록이 표시된다
  - 출고 실행 시 주문 상태가 `CONFIRMED` → `RELEASE`로 전환된다
  - `CONFIRMED`가 아닌 주문 ID 입력 시 오류 메시지 출력

### 실행 확인

```
=== 생산 라인 ===
[현재 생산 큐]
  순번 1 | 주문 ID: 1 | 시료: A형 시료 | 실 생산량: 56 ea | 예상 시간: 1680 min

완료 처리할 주문 ID: 1
>> 생산 완료. 주문 ID 1이 CONFIRMED 상태로 전환되었습니다.
   재고 56 ea 추가됨.

=== 출고 처리 ===
[출고 대기 주문]
  주문 ID: 1 | 시료: A형 시료 | 고객: 서울대 연구소 | 수량: 50

출고할 주문 ID: 1
>> 출고 완료. 주문 ID 1이 RELEASE 상태로 전환되었습니다.
```

---

## Phase 6: 모니터링 (실시간 자동 갱신)

### 목표

주문 상태별 현황과 시료별 재고 상태를 한 화면에서 확인한다.  
`data/order.json` 또는 `data/inventory.json`이 변경되면 1초 이내에 화면이 자동 갱신된다.

### 구현 대상

| 파일 | 내용 |
|------|------|
| `app/watcher.py` | `FileWatcher` — `os.path.getmtime()` 1초 폴링, 데몬 스레드 |
| `views/monitoring_view.py` | 대시보드 출력 (`_clear()` + 전체 재출력), 재고 상태 표기 |
| `controllers/monitoring_controller.py` | FileWatcher 콜백 → `_do_refresh()`, `_refresh_active` 플래그 관리 |

### 테스트 목록

- `tests/test_watcher.py`
  - 파일 수정 시 1초 내에 콜백이 호출된다 (`threading.Event.wait(timeout=2.0)`)
  - `stop()` 호출 후 스레드가 종료된다
  - 파일이 없어도 예외 없이 동작한다
  - 파일이 새로 생성되면 콜백이 호출된다

- `tests/test_controller_monitoring.py`
  - 주문 상태별 건수가 올바르게 집계된다
  - 재고 상태(여유/부족/고갈)가 올바르게 분류된다
  - `REJECTED` 주문은 집계에서 제외된다

### 실행 확인

```
=== 모니터링 대시보드 === (최종 갱신: 2026-05-08 15:32:01)

[주문 현황]
  RESERVED  :  2건
  PRODUCING :  1건
  CONFIRMED :  0건
  RELEASE   :  3건

[재고 현황]
  시료명       | 재고  | 상태
  A형 시료     |   6   | 부족
  B형 시료     |  20   | 여유
  C형 시료     |   0   | 고갈

명령 (q: 종료) >
```

---

## Phase 7: 더미 데이터 생성기 + 통합 테스트

### 목표

시료·주문·재고 더미 데이터를 자동으로 생성하여 삽입할 수 있다.  
전체 주문 사이클(접수 → 승인 → 생산 → 출고)이 더미 데이터로 처음부터 끝까지 검증된다.

### 구현 대상

| 파일 | 내용 |
|------|------|
| `generator/schema.py` | `FieldDef` dataclass + 프로젝트 `DEFAULT_SCHEMAS` |
| `generator/engine.py` | `DummyGenerator` — `generate_one()` / `generate_batch(count)` |
| `controllers/main_controller.py` | 더미 데이터 삽입 메뉴 항목 추가 |

### `DEFAULT_SCHEMAS` 필드명 (엔티티 속성명과 일치)

```python
DEFAULT_SCHEMAS = {
    'sample':    [FieldDef('name', 'string'),
                  FieldDef('avg_production_time', 'int'),
                  FieldDef('yield_rate', 'int')],     # 1~100, 실제 사용 시 /100
    'order':     [FieldDef('sample_id', 'int'),
                  FieldDef('customer', 'name'),
                  FieldDef('quantity', 'int')],
    'inventory': [FieldDef('sample_id', 'int'),
                  FieldDef('quantity', 'int')],
}
```

### 테스트 목록

- `tests/test_generator.py`
  - `generate_one()`: 스키마 필드명과 일치하는 키를 반환한다
  - 모든 값이 `str` 타입이다
  - `int` 타입 필드는 범위 내 숫자 문자열이다 (20회 반복 샘플링)
  - `name` 타입 필드는 비어 있지 않다
  - `generate_batch(n)`: 정확히 n건을 반환한다

- `tests/test_integration.py` — 전체 주문 사이클 통합 검증
  - 더미 시료 등록 → 더미 주문 접수 → 승인(재고 충분/부족) → 생산 완료 → 출고까지 상태 전이가 올바르다
  - 재고 부족 승인 시 생산량 계산 결과가 `ceil(부족분 / (수율 × 0.9))`와 일치한다
  - 모니터링 집계가 실제 주문 상태와 일치한다

### 실행 확인

```
=== 더미 데이터 생성 ===
스키마 선택 (sample / order / inventory): sample
생성할 건수: 5
>> 5건의 시료 더미 데이터를 추가했습니다.

스키마 선택 (sample / order / inventory): order
생성할 건수: 10
>> 10건의 주문 더미 데이터를 추가했습니다.
```

---

## Phase별 완료 기준 요약

| Phase | 실행 확인 핵심 | 신규 파일 수 |
|-------|--------------|------------|
| 1 | 메인 메뉴 표시·종료 | 4 |
| 2 | 시료 등록·조회·검색, JSON 저장 확인 | 3 |
| 3 | 주문 접수(RESERVED), 재고 표시 | 4 |
| 4 | 승인(CONFIRMED/PRODUCING), 거절(REJECTED), 재고 부족 메시지 | 3 |
| 5 | 생산 완료(→CONFIRMED), 출고(→RELEASE), 전체 사이클 완성 | 4 |
| 6 | 모니터링 대시보드, 파일 변경 시 자동 갱신 | 3 |
| 7 | 더미 데이터 자동 삽입, 통합 테스트 통과 | 3 |
