# Phase 2 TDD Plan — 시료 관리

## 전제 조건 (구현 전 완료 필요)

- `json_lib/` 패키지를 DataPersistence 참조 레포에서 복사
  - 출처: https://github.com/stormv2222/DataPersistence-gujun.jeong-14004536
  - 대상: `semicon/json_lib/`
  - 수정 금지

---

## 사이클 1 — SampleRepository: create + read_all

### 검증할 동작
시료를 생성하면 id가 자동 부여되고 모든 값이 str로 저장되며, read_all로 전체 목록을 조회할 수 있다.

### 테스트 시나리오 (TC-1, TC-2)
- Given: 임시 파일 경로로 SampleRepository 생성 (파일 없음)
- When: `create({"name": "A형", "avg_production_time": "30", "yield_rate": "0.9"})` 호출
- Then: 반환 레코드에 `"id"` 키 존재, 모든 value가 str
- When: 한 번 더 `create(...)` 호출 후 `read_all()`
- Then: 2건 반환

### 예상 실패 이유
`models/sample.py` 미존재 → ImportError

---

## 사이클 2 — SampleRepository: read_one

### 검증할 동작
존재하는 id로 read_one 시 레코드를 반환하고, 없는 id는 None을 반환한다.

### 테스트 시나리오 (TC-3, TC-4)
- Given: create로 레코드 1건 저장
- When: `read_one(1)` (존재하는 id)
- Then: 레코드 dict 반환
- When: `read_one(9999)` (없는 id)
- Then: `None` 반환

### 예상 실패 이유
read_one 미구현 → AttributeError 또는 반환값 불일치

---

## 사이클 3 — SampleRepository: update + delete

### 검증할 동작
update로 특정 필드를 수정할 수 있고, delete 후 read_one은 None을 반환한다.

### 테스트 시나리오 (TC-5, TC-6, TC-7)
- Given: create로 레코드 1건 저장
- When: `update(id, {"name": "수정됨"})` → `read_one(id)`
- Then: name 필드가 "수정됨"
- When: `delete(id)` → `read_one(id)`
- Then: 반환값 True, read_one → None
- When: `delete(9999)`
- Then: False 반환

### 예상 실패 이유
update/delete 미구현 → AttributeError

---

## 사이클 4 — SampleRepository: search + 파일 없음 + 영속성

### 검증할 동작
name 필드로 부분 검색이 가능하고, 파일이 없어도 예외 없이 동작하며, 새 인스턴스로 재로드해도 데이터가 유지된다.

### 테스트 시나리오 (TC-8, TC-9, TC-10)
- Given: "A형 시료", "B형 시료" 2건 저장
- When: `search("name", "A형")`
- Then: 1건만 반환
- Given: 파일 없는 경로로 SampleRepository 생성
- When: `read_all()`
- Then: 빈 리스트 반환, 예외 없음
- Given: create로 레코드 저장 후 같은 경로로 새 SampleRepository 인스턴스 생성
- When: `read_all()`
- Then: 동일 레코드 반환

### 예상 실패 이유
search 미구현 또는 파일 없음 처리 누락

---

## 사이클 5 — SampleView: 목록 출력 형식 + 빈 목록

### 검증할 동작
시료 목록 출력 시 지정 형식(ID, 이름, 생산시간, 수율)이 포함되고, 빈 목록이면 "등록된 시료 없음"을 출력한다.

### 테스트 시나리오
- Given: records = [{"id":"1","name":"A형 시료","avg_production_time":"30","yield_rate":"0.9"}]
- When: `view.show_sample_list(records)`, sys.stdout 캡처
- Then: "ID: 1", "A형 시료", "30분", "0.9" 포함
- Given: records = []
- When: `view.show_sample_list([])`
- Then: "등록된 시료 없음" 포함

### 예상 실패 이유
views/sample_view.py 미존재 → ImportError

---

## 사이클 6 — SampleController: register + list + search 흐름

### 검증할 동작
등록 흐름에서 입력값이 repo에 저장되고, list 흐름에서 show_sample_list가 호출되며, search 흐름에서 필터된 결과가 출력된다.

### 테스트 시나리오
- Given: view.get_input이 "A형", "30", "0.9" 순으로 반환
- When: `ctrl._register()`
- Then: repo.read_all() 결과 1건
- Given: repo에 레코드 존재
- When: `ctrl._list()`
- Then: show_sample_list 호출됨 (lambda 교체로 확인)
- Given: view.get_input이 "A형" 반환, repo에 "A형 시료" 존재
- When: `ctrl._search()`
- Then: show_sample_list에 전달된 목록에 해당 시료 포함

### 예상 실패 이유
controllers/sample_controller.py 미존재 → ImportError

---

## 사이클 7 — MainController: sample_ctrl 연동

### 검증할 동작
MainController에 sample_ctrl 주입 시 "1" 입력이 sample_ctrl.run()을 호출한다.

### 테스트 시나리오
- Given: called = [] 리스트, sample_ctrl.run = lambda: called.append(True)
- When: MainController(view, sample_ctrl=sample_ctrl).run(), "1" → "0" 입력
- Then: called 리스트에 True가 추가됨

### 예상 실패 이유
MainController.__init__이 sample_ctrl 파라미터를 받지 않음 → TypeError
