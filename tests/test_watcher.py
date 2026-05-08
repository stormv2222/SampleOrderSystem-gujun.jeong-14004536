import os
import tempfile
import threading
import time
import unittest
from app.watcher import FileWatcher


class TestFileWatcher(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.path = tmp.name
        tmp.close()

    def tearDown(self):
        try:
            os.unlink(self.path)
        except OSError:
            pass

    # TC-1: 파일 수정 시 1초 내에 콜백 호출
    def test_callback_called_on_file_change(self):
        called = threading.Event()
        watcher = FileWatcher(self.path, callback=called.set, interval=0.1)
        watcher.start()
        time.sleep(0.15)  # 초기 mtime 기록 대기
        with open(self.path, "w") as f:
            f.write("changed")
        triggered = called.wait(timeout=2.0)
        watcher.stop()
        self.assertTrue(triggered, "파일 변경 후 콜백이 호출되지 않음")

    # TC-2: stop() 후 스레드 종료
    def test_stop_joins_thread(self):
        watcher = FileWatcher(self.path, callback=lambda: None, interval=0.1)
        watcher.start()
        watcher.stop()
        self.assertFalse(watcher._thread.is_alive(), "stop() 후 스레드가 살아있음")

    # TC-3: 파일 없어도 예외 없이 start/stop
    def test_no_exception_when_file_missing(self):
        missing = self.path + "_missing.json"
        watcher = FileWatcher(missing, callback=lambda: None, interval=0.1)
        try:
            watcher.start()
            time.sleep(0.2)
            watcher.stop()
        except Exception as e:
            self.fail(f"파일 없을 때 예외 발생: {e}")

    # TC-4: 파일 새로 생성되면 콜백 호출
    def test_callback_called_on_file_creation(self):
        new_path = self.path + "_new.json"
        called = threading.Event()
        watcher = FileWatcher(new_path, callback=called.set, interval=0.1)
        watcher.start()
        time.sleep(0.15)
        with open(new_path, "w") as f:
            f.write("{}")
        triggered = called.wait(timeout=2.0)
        watcher.stop()
        try:
            os.unlink(new_path)
        except OSError:
            pass
        self.assertTrue(triggered, "파일 생성 후 콜백이 호출되지 않음")

    # TC-5: 파일 미변경 시 콜백 추가 호출 없음
    def test_no_callback_when_file_unchanged(self):
        call_count = [0]

        def counter():
            call_count[0] += 1

        watcher = FileWatcher(self.path, callback=counter, interval=0.1)
        watcher.start()
        time.sleep(0.15)  # 초기 mtime 기록 (최초 1회 가능)
        count_after_init = call_count[0]
        time.sleep(0.5)   # 추가 대기 (파일 미변경)
        watcher.stop()
        self.assertEqual(call_count[0], count_after_init, "파일 미변경인데 콜백이 추가 호출됨")
