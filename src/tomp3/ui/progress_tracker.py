import threading
import time
from pathlib import Path


class ProgressTracker:
    def __init__(self) -> None:
        self._initialized = False
        self._file_sizes: dict[Path, int] = {}
        self._total_bytes = 0
        self._processed_bytes = 0
        self._start_time = 0.0
        self._lock = threading.Lock()

    def start(self, files: list[Path]) -> None:
        with self._lock:
            self._file_sizes = {f: f.stat().st_size for f in files}
            self._total_bytes = sum(self._file_sizes.values())
            self._processed_bytes = 0
            self._start_time = time.time()
            self._initialized = True

    def update_progress(self, fpath: Path) -> None:
        with self._lock:
            self._check_initialized()
            size = self._file_sizes.pop(fpath, None)
            if size is None:
                raise ValueError(f"File {fpath} not found in tracked files.")
            self._processed_bytes += size

    def get_eta(self) -> float:
        with self._lock:
            self._check_initialized()
            if self._processed_bytes == 0 or self._processed_bytes >= self._total_bytes:
                return 0.0
            elapsed = time.time() - self._start_time
            speed = self._processed_bytes / elapsed

            if speed > 0:
                return (self._total_bytes - self._processed_bytes) / speed 

            return float("inf")

    def get_eta_time(self) -> time.struct_time:
        eta = self.get_eta()
        if eta == float("inf"):
            return time.gmtime(0)
        return time.gmtime(eta)

    def _check_initialized(self) -> None:
        if not self._initialized:
            message = "ProgressTracker not initialized. Call start() with files first."
            raise RuntimeError(message)
