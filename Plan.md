# Phase 3 TDD Plan — 재고 관리 + 주문 접수

## 사이클 1 — InventoryRepository 기본 CRUD

### 검증할 동작
재고 레코드를 생성하고 sample_id로 조회할 수 있다.

### 테스트 시나리오
- **TC-1**: Given 빈 inventory 파일, When `create({"sample_id": "1", "quantity": "100"})` + `find_by_sample_id(1)` 호출, Then 해당 레코드 반환
- **TC-5**: Given 빈 inventory 파일, When `find_by_sample_id(999)` 호출, Then `None` 반환
- **TC-6**: Given 파일 없음, When `read_all()` 호출, Then 빈 리스트 반환, 예외 없음

### 예상 실패 이유
`models/inventory.py` 파일이 존재하지 않아 `ImportError`

---

## 사이클 2 — InventoryRepository 수량 조작

### 검증할 동작
재고 수량을 증가/차감할 수 있고, 부족 시 ValueError가 발생한다.

### 테스트 시나리오
- **TC-2**: Given 수량 100인 레코드, When `add_quantity(sample_id, 50)` 호출, Then quantity == 150
- **TC-3**: Given 수량 100인 레코드, When `subtract_quantity(sample_id, 30)` 호출, Then quantity == 70
- **TC-4**: Given 수량 10인 레코드, When `subtract_quantity(sample_id, 50)` 호출, Then `ValueError` 발생

### 예상 실패 이유
사이클 1 후 `add_quantity` / `subtract_quantity` 미구현

---

## 사이클 3 — OrderRepository 기본 동작

### 검증할 동작
주문을 생성하면 status가 RESERVED로 저장되고, 상태별 필터링이 동작한다.

### 테스트 시나리오
- **TC-1**: `create({"sample_id": "1", "customer": "서울대", "quantity": "50"})` → status == "RESERVED"
- **TC-2**: create 반환 레코드에 `id` 포함, 모든 값 `str`
- **TC-3**: `read_all()` → 전체 주문 목록 반환
- **TC-4**: `filter_by_status("RESERVED")` → 해당 상태 주문만 반환
- **TC-5**: `update(id, {"status": "CONFIRMED"})` → 상태 변경 확인
- **TC-6**: 파일 없는 상태에서 `read_all()` → 빈 리스트, 예외 없음

### 예상 실패 이유
`models/order.py` 파일이 존재하지 않아 `ImportError`

---

## 사이클 4 — OrderController.run_reserve() 유효한 시료 ID

### 검증할 동작
유효한 시료 ID로 주문 접수 시 RESERVED 상태 주문이 생성된다.

### 테스트 시나리오
- Given 존재하는 sample(id=1), When `run_reserve()` 호출(sample_id="1", customer="서울대", quantity="50"), Then `order_repo.read_all()` 에 RESERVED 주문 1건 존재

### 예상 실패 이유
`controllers/order_controller.py` 파일이 존재하지 않아 `ImportError`

---

## 사이클 5 — OrderController.run_reserve() 잘못된 시료 ID

### 검증할 동작
존재하지 않는 시료 ID 입력 시 에러 메시지를 보여주고 주문을 생성하지 않는다.

### 테스트 시나리오
- Given 존재하지 않는 sample_id="999", When `run_reserve()` 호출, Then `view.show_error` 호출됨, 주문 미생성

### 예상 실패 이유
사이클 4 후 invalid 분기 미구현 (또는 show_error 미호출)

---

## 사이클 6 — OrderController.run_reserve() 현재 재고 표시

### 검증할 동작
주문 접수 완료 메시지에 현재 재고 수량이 포함된다.

### 테스트 시나리오
- Given sample(id=1) + inventory(sample_id=1, quantity=200), When `run_reserve()` 호출, Then show_message 인자에 "200 ea" 포함

### 예상 실패 이유
사이클 4,5 통과 후 재고 조회 로직 검증

---

## 사이클 7 — MainController + main.py 연동

### 검증할 동작
MainController가 order_ctrl을 받아 "2" 메뉴를 order_ctrl.run_reserve로 라우팅한다.

### 테스트 시나리오
- Given `order_ctrl` stub, When `MainController(view, sample_ctrl=..., order_ctrl=order_ctrl)` 생성, Then `self._menu["2"][1] == order_ctrl.run_reserve`

### 예상 실패 이유
`main_controller.py` 에 `order_ctrl` 파라미터 미존재
