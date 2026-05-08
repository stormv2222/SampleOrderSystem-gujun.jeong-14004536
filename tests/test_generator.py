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
