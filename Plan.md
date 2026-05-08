# Phase 7 TDD Plan

## 사이클 1 — FieldDef + DEFAULT_SCHEMAS 정의

### 검증할 동작
`FieldDef` dataclass와 `DEFAULT_SCHEMAS`가 올바른 구조로 정의된다.

### 테스트 시나리오
- Given: `generator/schema.py`가 존재한다
- When: `DEFAULT_SCHEMAS['sample']`, `['order']`, `['inventory']`를 조회한다
- Then: 각 스키마의 필드명 리스트가 설계 문서와 일치한다

### 예상 실패 이유
`generator/schema.py` 파일이 없어서 `ImportError`

---

## 사이클 2 — DummyGenerator.generate_one() 스키마 키 반환

### 검증할 동작
`generate_one()` 반환 dict의 키 집합이 스키마 필드명과 일치한다.

### 예상 실패 이유
`generator/engine.py` 없음 → `ImportError`

---

## 사이클 3 — 모든 값이 str 타입

### 검증할 동작
`generate_one()` 반환 dict의 모든 값이 `str` 타입이다.

### 예상 실패 이유
`_generate_value()` 미구현 → 값 반환 없음

---

## 사이클 4 — int 타입 필드 범위 검증

### 검증할 동작
`int` 타입 필드(quantity, yield_rate 등)가 1~100 범위의 숫자 문자열이다 (20회 반복).

### 예상 실패 이유
`_generate_value('int')` 미구현

---

## 사이클 5 — name 타입 필드 비어 있지 않음

### 검증할 동작
`name` 타입 필드(customer)가 비어 있지 않은 문자열이다 (20회 반복).

### 예상 실패 이유
`_random_name()` 미구현

---

## 사이클 6 — generate_batch(n) / generate_batch(0)

### 검증할 동작
`generate_batch(5)`는 정확히 5건, `generate_batch(0)`은 빈 리스트를 반환한다.

### 예상 실패 이유
`generate_batch()` 미구현

---

## 사이클 7 — DummyController auto_generate_and_insert() + run()

### 검증할 동작
`auto_generate_and_insert('sample', 3)` 호출 시 Repository에 3건이 저장된다.

### 예상 실패 이유
`controllers/dummy_controller.py` 없음

---

## 사이클 8 — MainController 메뉴 "7" 추가

### 검증할 동작
`MainController`에 `dummy_ctrl`을 주입하면 메뉴 "7"이 등록된다.

### 예상 실패 이유
`MainController.__init__`에 `dummy_ctrl` 파라미터 없음

---

## 사이클 9 — 통합 테스트 (전체 주문 사이클)

### 검증할 동작
더미 데이터 생성 → 주문 접수 → 승인(재고 충분/부족) → 생산 완료 → 출고까지 상태 전이가 올바르다.

### 예상 실패 이유
통합 흐름 미검증 상태

---

## 진행 상황

- [x] 사이클 1: FieldDef + DEFAULT_SCHEMAS
- [x] 사이클 2: generate_one() 키 반환
- [x] 사이클 3: 모든 값 str
- [x] 사이클 4: int 범위 검증
- [x] 사이클 5: name 비어 있지 않음
- [x] 사이클 6: generate_batch
- [x] 사이클 7: DummyController
- [x] 사이클 8: MainController 메뉴 "7"
- [x] 사이클 9: 통합 테스트
