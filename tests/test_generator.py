"""
tests/test_generator.py — DummyGenerator 단위 테스트 (Phase 7)
"""
import pytest
from generator.schema import FieldDef, DEFAULT_SCHEMAS


# ───────────────────────────────────────────────
# 사이클 1: FieldDef + DEFAULT_SCHEMAS 구조 검증
# ───────────────────────────────────────────────

def test_default_schemas_sample_field_names():
    """DEFAULT_SCHEMAS['sample'] 필드명이 설계 문서와 일치한다."""
    fields = [f.name for f in DEFAULT_SCHEMAS['sample']]
    assert fields == ['name', 'avg_production_time', 'yield_rate']


def test_default_schemas_order_field_names():
    """DEFAULT_SCHEMAS['order'] 필드명이 설계 문서와 일치한다."""
    fields = [f.name for f in DEFAULT_SCHEMAS['order']]
    assert fields == ['sample_id', 'customer', 'quantity']


def test_default_schemas_inventory_field_names():
    """DEFAULT_SCHEMAS['inventory'] 필드명이 설계 문서와 일치한다."""
    fields = [f.name for f in DEFAULT_SCHEMAS['inventory']]
    assert fields == ['sample_id', 'quantity']


def test_fielddef_is_dataclass():
    """FieldDef가 name, field_type 속성을 가지는 dataclass다."""
    f = FieldDef(name='quantity', field_type='int')
    assert f.name == 'quantity'
    assert f.field_type == 'int'


# ───────────────────────────────────────────────
# 사이클 2: generate_one() 반환 dict 키 검증 (TC-1)
# ───────────────────────────────────────────────

from generator.engine import DummyGenerator


@pytest.fixture
def sample_gen():
    return DummyGenerator(DEFAULT_SCHEMAS['sample'])


@pytest.fixture
def order_gen():
    return DummyGenerator(DEFAULT_SCHEMAS['order'])


def test_generate_one_keys_match_schema_sample(sample_gen):
    """generate_one() 반환 dict의 키 집합이 sample 스키마 필드명과 일치한다."""
    result = sample_gen.generate_one()
    expected_keys = {f.name for f in DEFAULT_SCHEMAS['sample']}
    assert set(result.keys()) == expected_keys


def test_generate_one_keys_match_schema_order(order_gen):
    """generate_one() 반환 dict의 키 집합이 order 스키마 필드명과 일치한다."""
    result = order_gen.generate_one()
    expected_keys = {f.name for f in DEFAULT_SCHEMAS['order']}
    assert set(result.keys()) == expected_keys


# ───────────────────────────────────────────────
# 사이클 3: 모든 값이 str 타입 (TC-2)
# ───────────────────────────────────────────────

def test_all_values_are_str_sample(sample_gen):
    """sample generate_one() 반환값이 모두 str 타입이다 (20회 반복)."""
    for _ in range(20):
        result = sample_gen.generate_one()
        assert all(isinstance(v, str) for v in result.values()), \
            f"Non-str value found: {result}"


def test_all_values_are_str_order(order_gen):
    """order generate_one() 반환값이 모두 str 타입이다 (20회 반복)."""
    for _ in range(20):
        result = order_gen.generate_one()
        assert all(isinstance(v, str) for v in result.values()), \
            f"Non-str value found: {result}"


# ───────────────────────────────────────────────
# 사이클 4: int 타입 필드 범위 검증 (TC-3, TC-7)
# ───────────────────────────────────────────────

def test_quantity_is_digit_and_in_range(order_gen):
    """order quantity 필드가 isdigit()이고 1~100 범위다 (20회 반복, TC-3)."""
    for _ in range(20):
        result = order_gen.generate_one()
        qty = result['quantity']
        assert qty.isdigit(), f"quantity not digit: {qty}"
        assert 1 <= int(qty) <= 100, f"quantity out of range: {qty}"


def test_yield_rate_in_range(sample_gen):
    """sample yield_rate 필드가 1~100 범위의 숫자 문자열이다 (20회 반복, TC-7)."""
    for _ in range(20):
        result = sample_gen.generate_one()
        yr = result['yield_rate']
        assert yr.isdigit(), f"yield_rate not digit: {yr}"
        assert 1 <= int(yr) <= 100, f"yield_rate out of range: {yr}"


def test_avg_production_time_in_range(sample_gen):
    """sample avg_production_time 필드가 1~100 범위의 숫자 문자열이다 (20회 반복, TC-3)."""
    for _ in range(20):
        result = sample_gen.generate_one()
        apt = result['avg_production_time']
        assert apt.isdigit(), f"avg_production_time not digit: {apt}"
        assert 1 <= int(apt) <= 100, f"avg_production_time out of range: {apt}"


# ───────────────────────────────────────────────
# 사이클 5: name 타입 필드 비어 있지 않음 (TC-4)
# ───────────────────────────────────────────────

def test_customer_name_not_empty(order_gen):
    """order customer 필드가 비어 있지 않은 문자열이다 (20회 반복, TC-4)."""
    for _ in range(20):
        result = order_gen.generate_one()
        customer = result['customer']
        assert isinstance(customer, str), f"customer is not str: {customer!r}"
        assert customer.strip() != '', f"customer is empty or whitespace: {customer!r}"


# ───────────────────────────────────────────────
# 사이클 6: generate_batch(n) / generate_batch(0) (TC-5, TC-6)
# ───────────────────────────────────────────────

def test_generate_batch_returns_exact_count(order_gen):
    """generate_batch(5)는 정확히 5건을 반환한다 (TC-5)."""
    result = order_gen.generate_batch(5)
    assert len(result) == 5


def test_generate_batch_zero_returns_empty_list(order_gen):
    """generate_batch(0)은 빈 리스트를 반환한다 (TC-6)."""
    result = order_gen.generate_batch(0)
    assert result == []
