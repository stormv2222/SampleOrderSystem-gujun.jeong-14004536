from typing import Literal
from dataclasses import dataclass

FieldType = Literal['name', 'string', 'int']


@dataclass
class FieldDef:
    name: str
    field_type: FieldType


DEFAULT_SCHEMAS: dict[str, list[FieldDef]] = {
    'sample': [
        FieldDef('name',                'string'),
        FieldDef('avg_production_time', 'int'),
        FieldDef('yield_rate',          'int'),
    ],
    'order': [
        FieldDef('sample_id', 'int'),
        FieldDef('customer',  'name'),
        FieldDef('quantity',  'int'),
    ],
    'inventory': [
        FieldDef('sample_id', 'int'),
        FieldDef('quantity',  'int'),
    ],
}
