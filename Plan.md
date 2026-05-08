# Phase 1 TDD Plan — 프로젝트 골격 + 메인 메뉴

## 사이클 1 — `0` 입력 시 루프 종료

### 검증할 동작
`MainController.run()`에 `"0"`을 입력하면 루프가 정상 종료된다.

### 테스트 시나리오
- Given: `MainView`의 `get_input`이 `"0"`을 반환하도록 주입
- When: `MainController(view).run()` 호출
- Then: `StopIteration` 없이 함수가 정상 반환된다

### 예상 실패 이유
`MainController`, `MainView` 클래스가 아직 존재하지 않으므로 `ImportError` 또는 `ModuleNotFoundError` 발생

---

## 사이클 2 — 유효하지 않은 입력 시 오류 메시지 출력

### 검증할 동작
메뉴에 없는 번호(`"9"`)를 입력하면 `show_invalid()`가 호출된다.

### 테스트 시나리오
- Given: `get_input`이 `"9"` → `"0"` 순서로 반환
- When: `MainController(view).run()` 호출
- Then: `show_invalid()`가 최소 1회 호출되었다

### 예상 실패 이유
사이클 1 구현 후 `show_invalid` 분기가 없으면 호출되지 않음 → assertion 실패

---

## 사이클 3 — 유효한 메뉴 항목 선택 시 "준비 중" 메시지 출력

### 검증할 동작
`"1"`~`"6"` 중 하나를 입력하면 `show_not_implemented()`가 호출된다.

### 테스트 시나리오
- Given: `get_input`이 `"1"` → `"0"` 순서로 반환
- When: `MainController(view).run()` 호출
- Then: `show_not_implemented()`가 최소 1회 호출되었다

### 예상 실패 이유
`show_not_implemented` 분기가 없으면 호출되지 않음 → assertion 실패

---

## 사이클 4 — `show_menu` 출력에 모든 메뉴 항목 포함

### 검증할 동작
`run()` 실행 시 stdout에 7개 메뉴 레이블이 모두 출력된다.

### 테스트 시나리오
- Given: `get_input`이 `"0"` 반환, `sys.stdout`을 `io.StringIO`로 교체
- When: `MainController(view).run()` 호출
- Then: stdout 캡처 문자열에 `"시료 관리"`, `"주문 접수"`, `"주문 승인/거절"`, `"모니터링"`, `"출고 처리"`, `"생산 라인"`, `"종료"` 7개 레이블이 모두 포함된다

### 예상 실패 이유
`show_menu`가 아직 실제 출력을 하지 않거나, 레이블 중 하나라도 빠지면 assertion 실패
