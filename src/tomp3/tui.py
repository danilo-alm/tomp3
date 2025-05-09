from rich.console import Console, Group
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from rich.text import Text
import threading
import time
from enum import Enum
from collections import defaultdict


class FileStatus(Enum):
    CONVERTING = 1
    CONVERTED = 2
    ERROR = 3


class ConversionUI:
    def __init__(self, visible_limit=7):
        self.console = Console()
        self.visible_limit = visible_limit
        self._converting_files = []  # (filename, FileStatus)
        self._lock = threading.RLock()  # For accessing file list
        self._running = True

        self._live = Live(self._render_view(), refresh_per_second=2, screen=True)

        self._thread = threading.Thread(target=self._run_live_loop, daemon=True)
        self._thread.start()

    def add_file(self, filename: str):
        with self._lock:
            self._converting_files.append((filename, FileStatus.CONVERTING))
    
    def update_file_status(self, filename: str, status: FileStatus):
        with self._lock:
            for i, (fname, _) in enumerate(self._converting_files):
                if fname == filename:
                    self._converting_files[i] = (fname, status)
                    break
            self._sort_converting_files()

    def stop(self):
        self._running = False
        self._live.stop()
        return self._get_report()

    def _render_view(self):
        with self._lock:
            latest = self._converting_files[-self.visible_limit:]
            items = []
            for filename, status in latest:
                match status:
                    case FileStatus.CONVERTED:
                        item = Text(f"✓ {filename}", style="green")
                    case FileStatus.CONVERTING:
                        item = Spinner("dots", text=f"Converting {filename}",
                                       style="green")
                    case FileStatus.ERROR:
                        item = Text(f"✗ {filename}", style="red")
                items.append(item)

        return Panel(
            Group(*items), title="Current Conversions",border_style="cyan"
        )

    def _run_live_loop(self):
        with self._live:
            while self._running:
                self._live.update(self._render_view())
                time.sleep(0.5)

    def _sort_converting_files(self):
        with self._lock:
            self._converting_files.sort(
                key=lambda x: x[1] == FileStatus.CONVERTING
            )

    def _get_report(self):
        d = defaultdict(list)
        for (fname, status) in self._converting_files:
            d[status].append(fname)
        return d
        