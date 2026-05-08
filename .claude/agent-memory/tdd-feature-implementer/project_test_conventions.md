---
name: Test conventions for repository tests
description: unittest.TestCase pattern with tempfile isolation used for all repository tests
type: project
---

All repository test classes use `unittest.TestCase` (not pytest functions), with:

- `setUp`: create a `tempfile.NamedTemporaryFile`, capture the path, close it, then `os.unlink` it so tests start with no file on disk
- `tearDown`: `os.unlink(self.path)` if the file exists — ensures cleanup
- `self.repo = XRepository(self.path)` constructed in setUp
- TC-10 style persistence test: create a second repo instance pointing at the same path and assert it reads back the same data

Test naming convention: `test_<what>_<when>_<expected_outcome>`

Tests live in `tests/test_model_<entity>.py`.
