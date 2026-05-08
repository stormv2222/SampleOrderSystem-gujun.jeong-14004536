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
