import os
import threading
from typing import Callable, Optional


class FileWatcher:
    def __init__(
        self,
        file_path: str,
        callback: Callable[[], None],
        interval: float = 1.0,
    ) -> None:
        self._file_path = file_path
        self._callback = callback
        self._interval = interval
        self._last_mtime: Optional[float] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        while not self._stop_event.wait(self._interval):
            mtime = self._get_mtime()
            if mtime != self._last_mtime:
                self._last_mtime = mtime
                self._callback()

    def _get_mtime(self) -> Optional[float]:
        try:
            return os.path.getmtime(self._file_path)
        except OSError:
            return None
