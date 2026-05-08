import os
from dataclasses import dataclass
from typing import Optional

from json_lib import load, dump


@dataclass
class Sample:
    id: int
    name: str
    avg_production_time: int
    yield_rate: float


class SampleRepository:
    def __init__(self, file_path: str = "data/sample.json") -> None:
        self._file_path = file_path

    def _load_raw(self) -> dict:
        try:
            return load(self._file_path)
        except FileNotFoundError:
            return {"next_id": 1, "records": []}

    def _load(self) -> list:
        return self._load_raw()["records"]

    def _save(self, raw: dict) -> None:
        dir_path = os.path.dirname(self._file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        dump(raw, self._file_path, indent=2)

    def create(self, fields: dict) -> dict:
        raw = self._load_raw()
        record = {k: str(v) for k, v in fields.items()}
        record["id"] = str(raw["next_id"])
        raw["records"].append(record)
        raw["next_id"] += 1
        self._save(raw)
        return record

    def read_all(self) -> list:
        return self._load()

    def read_one(self, record_id: int) -> Optional[dict]:
        for r in self._load():
            if int(r["id"]) == record_id:
                return r
        return None

    def update(self, record_id: int, fields: dict) -> Optional[dict]:
        raw = self._load_raw()
        for r in raw["records"]:
            if int(r["id"]) == record_id:
                for k, v in fields.items():
                    r[k] = str(v)
                self._save(raw)
                return r
        return None

    def delete(self, record_id: int) -> bool:
        raw = self._load_raw()
        original_len = len(raw["records"])
        raw["records"] = [r for r in raw["records"] if int(r["id"]) != record_id]
        if len(raw["records"]) < original_len:
            self._save(raw)
            return True
        return False

    def search(self, key: str, value: str) -> list:
        return [r for r in self._load() if value.lower() == r[key].lower()]
