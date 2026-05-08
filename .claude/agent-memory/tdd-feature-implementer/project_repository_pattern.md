---
name: Repository pattern for models
description: Stateless repository pattern used in models layer — file I/O via json_lib, all stored values as str
type: project
---

SampleRepository (and by convention all Repository classes in models/) follows a stateless pattern:

- Constructor takes `file_path: str`; no state is cached between calls
- `_load_raw()` calls `load(self._file_path)`, catches `FileNotFoundError` and returns `{"next_id": 1, "records": []}`
- `_load()` returns `_load_raw()["records"]`
- `_save(raw)` calls `dump(raw, self._file_path, indent=2)`
- `create(fields)` reads raw, assigns `str(raw["next_id"])` as id, appends, increments next_id, saves, returns record — ALL values stored as `str`
- `read_one(record_id: int)` iterates records comparing `int(r["id"]) == record_id`
- `update` and `delete` re-read raw (not records only) so they can save the full structure back
- `search(key, value)` does case-insensitive substring match: `value.lower() in r[key].lower()`

**Why:** SPEC requires stateless repositories — every operation reads from and writes to the JSON file directly. No in-memory cache.

**How to apply:** Use the same skeleton for OrderRepository and InventoryRepository.
