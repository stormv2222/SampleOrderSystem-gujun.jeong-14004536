# Phase 5 TDD Plan — 묶음 진행

## 묶음 구성
| 묶음 | 사이클 | 대상 |
|------|--------|------|
| A | 1 | Model: ProductionQueue.remove_by_order_id |
| B | 2+3 | View: ProductionView + ReleaseView |
| C | 4+5+6+7 | Controller: ProductionController (전체) |
| D | 8+9+10+11 | Controller: ReleaseController (전체) |
| E | 12+13 | MainController 메뉴 5·6 연결 |
| F | 14 | main.py 의존성 조립 + 전체 pytest |

---


## 사이클 1 — ProductionQueue.remove_by_order_id()

### 검증할 동작
`remove_by_order_id(order_id)`를 호출하면 해당 order_id를 가진 작업이 큐에서 제거되고 `True`를 반환한다.  
존재하지 않는 order_id면 큐가 변경되지 않고 `False`를 반환한다.

### 테스트 시나리오 A — 정상 제거
- Given: 큐에 order_id=1, order_id=2 작업이 있음
- When: `remove_by_order_id(1)` 호출
- Then: 반환값 `True`, 큐 크기 1, 남은 작업 order_id=2

### 테스트 시나리오 B — 없는 ID
- Given: 큐에 order_id=1 작업이 있음
- When: `remove_by_order_id(99)` 호출
- Then: 반환값 `False`, 큐 크기 1 (변화 없음)

### 예상 실패 이유
`ProductionQueue`에 `remove_by_order_id` 메서드가 존재하지 않음 → `AttributeError`

---

## 사이클 2 — ProductionView 신규 생성

### 검증할 동작
`ProductionView`는 생산 큐 목록, 메시지, 오류를 콘솔에 출력하고 사용자 입력을 수신한다.
(View 계층: print/input만 허용. Controller 테스트의 FakeView로 동작 검증)

### 예상 실패 이유
`views/production_view.py` 파일이 없음 → `ImportError`

---

## 사이클 3 — ReleaseView 신규 생성

### 검증할 동작
`ReleaseView`는 CONFIRMED 주문 목록, 메시지, 오류를 콘솔에 출력하고 사용자 입력을 수신한다.
(View 계층: print/input만 허용. Controller 테스트의 FakeView로 동작 검증)

### 예상 실패 이유
`views/release_view.py` 파일이 없음 → `ImportError`

---

## 사이클 4 — ProductionController: 생산 완료 처리 (PRODUCING → CONFIRMED, 재고 증가)

### 검증할 동작
`ProductionController.run()`에서 유효한 주문 ID를 입력하면 주문 상태가 CONFIRMED로 전환되고 재고에 actual_quantity가 추가된다.

### 테스트 시나리오
- Given: PRODUCING 상태 주문(order_id=X), 재고 10, 큐에 actual_quantity=56 작업
- When: `run()`에 order_id 입력 후 "0" 입력
- Then: 주문 상태 CONFIRMED, 재고 66(10+56)

### 예상 실패 이유
`controllers/production_controller.py` 파일이 없음 → `ImportError`

---

## 사이클 5 — ProductionController: 큐에 없는 ID → show_error

### 검증할 동작
큐에 존재하지 않는 주문 ID를 입력하면 view.show_error가 호출된다.

### 테스트 시나리오
- Given: 빈 ProductionQueue
- When: "999" 입력 후 "0"
- Then: view.errors 리스트에 항목 >= 1

### 예상 실패 이유
`production_controller.py` 미존재 → `ImportError` (사이클 4와 동일 파일, 사이클 4 GREEN 후 추가)

---

## 사이클 6 — ProductionController: 완료 처리 후 큐에서 제거

### 검증할 동작
생산 완료 처리 후 해당 작업이 ProductionQueue에서 제거된다.

### 테스트 시나리오
- Given: 큐에 1개 작업
- When: 해당 order_id 입력
- Then: `q.is_empty()` == True

### 예상 실패 이유
사이클 4 구현 후 테스트 추가, 초기에는 remove_by_order_id 미호출 시 실패

---

## 사이클 7 — ProductionController: run() → show_queue 호출 확인

### 검증할 동작
`run()` 호출 시 `view.show_queue`가 최소 한 번 호출된다.

### 예상 실패 이유
사이클 4 이후 추가 테스트; show_queue 미호출 시 실패

---

## 사이클 8 — ReleaseController: CONFIRMED → RELEASE

### 검증할 동작
CONFIRMED 주문 ID를 입력하면 상태가 RELEASE로 전환되고 view.show_message가 호출된다.

### 테스트 시나리오
- Given: CONFIRMED 상태 주문
- When: 해당 order_id 입력
- Then: 주문 상태 RELEASE, view.messages에 "RELEASE" 포함

### 예상 실패 이유
`controllers/release_controller.py` 파일이 없음 → `ImportError`

---

## 사이클 9 — ReleaseController: 비 CONFIRMED 주문 → show_error

### 검증할 동작
RESERVED/PRODUCING 상태 주문 ID를 입력하면 view.show_error가 호출되고 상태가 변경되지 않는다.

### 예상 실패 이유
사이클 8 GREEN 후 추가; 상태 체크 없으면 실패

---

## 사이클 10 — ReleaseController: 존재하지 않는 주문 → show_error

### 검증할 동작
존재하지 않는 주문 ID 입력 시 view.show_error가 호출된다.

### 예상 실패 이유
order is None 미처리 시 실패

---

## 사이클 11 — ReleaseController: 빈 CONFIRMED 목록 → show_confirmed_orders([])

### 검증할 동작
CONFIRMED 주문이 없을 때 show_confirmed_orders가 빈 리스트로 호출된다.

### 예상 실패 이유
run() 루프 내 filter_by_status 결과가 [] 인 경우 show_confirmed_orders 미호출 시 실패

---

## 사이클 12 — MainController: 메뉴 6 → production_ctrl.run() 호출

### 검증할 동작
`production_ctrl`이 주입된 MainController에서 "6" 입력 시 `production_ctrl.run()`이 호출된다.

### 테스트 시나리오
- Given: FakeProductionCtrl 주입
- When: "6" → "0" 입력
- Then: called 리스트에 True

### 예상 실패 이유
MainController 생성자에 `production_ctrl` 파라미터 없음 → TypeError 또는 메뉴 미연결

---

## 사이클 13 — MainController: 메뉴 5 → release_ctrl.run() 호출

### 검증할 동작
`release_ctrl`이 주입된 MainController에서 "5" 입력 시 `release_ctrl.run()`이 호출된다.

### 예상 실패 이유
사이클 12 GREEN 후 추가; release_ctrl 미연결 시 실패

---

## 사이클 14 — main.py: production_ctrl, release_ctrl 조립 및 주입

### 검증할 동작
`python main.py` 실행 시 ImportError 없이 메인 메뉴가 표시된다.
(수동 확인 + 전체 테스트 `pytest -v` 통과)

### 예상 실패 이유
ProductionView, ReleaseView, ProductionController, ReleaseController import 누락 시 ImportError
