# Phase 4 TDD Plan — 주문 승인/거절 + 생산 큐

## 사이클 1 — ProductionQueue 기본 동작 (enqueue, size, is_empty)

### 검증할 동작
태스크를 큐에 넣으면 size가 증가하고, is_empty로 상태를 확인할 수 있다.

### 테스트 시나리오
- Given 빈 ProductionQueue, When `enqueue(task)` 호출, Then `size() == 1`, `is_empty() == False`
- Given 빈 ProductionQueue, Then `is_empty() == True`

### 예상 실패 이유
`models/production_queue.py` 미존재 → ImportError

---

## 사이클 2 — ProductionQueue FIFO (peek, dequeue, list_all)

### 검증할 동작
FIFO 순서로 peek/dequeue가 동작하고, 빈 큐에서 None을 반환한다.

### 테스트 시나리오
- task1, task2 순서로 enqueue → `peek()` → task1 반환 (제거 없음)
- `dequeue()` → task1 반환, `dequeue()` → task2 반환 (FIFO)
- 빈 큐 `dequeue()` → None, `peek()` → None
- `list_all()` → 삽입 순서와 동일한 목록

### 예상 실패 이유
사이클 1 후 peek/dequeue/list_all 미구현

---

## 사이클 3 — _calc_production 공식 검증

### 검증할 동작
shortage=50, yield_rate=0.9 → actual_qty = ceil(50/(0.9×0.9)) = 62, total_time = avg_time × 62

### 테스트 시나리오
- `_calc_production(50, 0.9, 30)` → `(62, 1860)`
- `_calc_production(10, 0.8, 45)` → `ceil(10/(0.8×0.9))=ceil(13.88)=14` → `(14, 630)`

### 예상 실패 이유
`controllers/order_controller.py`에 `_calc_production` 미구현

---

## 사이클 4 — _approve 재고 충분 → CONFIRMED + 재고 차감

### 검증할 동작
재고가 충분할 때 주문이 CONFIRMED 상태가 되고 재고가 차감된다.

### 테스트 시나리오
- Given RESERVED 주문(quantity=50) + inventory(quantity=100), When `_approve(order)`, Then 주문 status=="CONFIRMED", inventory quantity=="50"

### 예상 실패 이유
`_approve` 미구현

---

## 사이클 5 — _approve 재고 부족 → y → PRODUCING + 생산 큐 등록

### 검증할 동작
재고 부족 시 y 입력하면 주문이 PRODUCING이 되고 생산 큐에 태스크가 등록된다.

### 테스트 시나리오
- Given RESERVED 주문(quantity=50) + inventory(quantity=10) + y 입력, When `_approve(order)`, Then 주문 status=="PRODUCING", production_queue.size()==1

### 예상 실패 이유
_approve 부족 분기 미구현

---

## 사이클 6 — _approve 재고 부족 → n → 상태 변경 없음

### 검증할 동작
재고 부족 시 n 입력하면 주문 상태와 생산 큐에 변경이 없다.

### 테스트 시나리오
- Given RESERVED 주문(quantity=50) + inventory(quantity=10) + n 입력, When `_approve(order)`, Then 주문 status=="RESERVED", production_queue.is_empty()==True

### 예상 실패 이유
사이클 5 후 n 분기 미구현

---

## 사이클 7 — _reject → REJECTED

### 검증할 동작
거절 시 주문 상태가 REJECTED로 변경된다.

### 테스트 시나리오
- Given RESERVED 주문, When `_reject(order)` 호출, Then 주문 status=="REJECTED"

### 예상 실패 이유
`_reject` 미구현

---

## 사이클 8 — run_approve 유효하지 않은 주문 ID / 비RESERVED 주문

### 검증할 동작
존재하지 않는 주문 ID 또는 RESERVED 아닌 주문 선택 시 show_error를 호출한다.

### 테스트 시나리오
- Given 빈 order_repo, When `run_approve()` 호출(order_id="999"), Then show_error 호출됨
- Given CONFIRMED 상태 주문, When `run_approve()` 호출, Then show_error 호출됨

### 예상 실패 이유
run_approve 유효성 검증 미구현

---

## 사이클 9 — MainController "3" 연동 + main.py ProductionQueue 주입

### 검증할 동작
MainController가 order_ctrl을 받아 "3" 메뉴를 order_ctrl.run_approve로 라우팅한다.

### 테스트 시나리오
- Given `order_ctrl` stub, When `MainController(view, order_ctrl=order_ctrl)` 생성 후 "3" 입력, Then `order_ctrl.run_approve` 호출됨

### 예상 실패 이유
MainController에 "3" 라우팅 미구현
