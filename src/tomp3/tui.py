import threading
import time
from collections import defaultdict
from enum import Enum
from pathlib import Path

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text


class FileStatus(Enum):
    CONVERTING = 1
    CONVERTED = 2
    ERROR = 3


class ConversionUI:
    def __init__(self, visible_limit: int = 7) -> None:
        self.console = Console()
        self.visible_limit = visible_limit

        self._converting_files: list[tuple[Path, FileStatus]] = []
        self._lock = threading.RLock()  # For file list
        self._running = True
        self._total_files = 0
        self._remaining_files = 0

        self._live = Live(self._render_view(), refresh_per_second=2, screen=True)

        self._thread = threading.Thread(target=self._run_live_loop, daemon=True)
        self._thread.start()
    
    def set_total_files(self, total_files: int) -> None:
        self._total_files = total_files
        self._remaining_files = total_files

    def add_file(self, fpath: Path) -> None:
        with self._lock:
            self._converting_files.append((fpath, FileStatus.CONVERTING))

    def update_file_status(self, fpath_to_update: Path, status: FileStatus) -> None:
        with self._lock:
            found = False
            for i, (fpath, _) in enumerate(self._converting_files):
                if fpath == fpath_to_update:
                    self._converting_files[i] = (fpath, status)
                    found = True
                    break
                
            if not found:
                raise ValueError(f"File {fpath_to_update} not found in the list.")
            
            if status == FileStatus.CONVERTED or status == FileStatus.ERROR:
                self._remaining_files -= 1

            self._sort_converting_files()

    def stop(self) -> dict[FileStatus, list[Path]]:
        self._running = False
        self._live.stop()
        return self._get_report()

    def _render_view(self) -> Panel:
        with self._lock:
            latest = self._converting_files[-self.visible_limit:]
            items: list[ Text | Spinner ] = []
            for fpath, status in latest:
                filename = fpath.name
                match status:
                    case FileStatus.CONVERTED:
                        items.append(Text(f"✓ {filename}", style="green"))
                    case FileStatus.CONVERTING:
                        items.append(Spinner("dots", text=f"Converting {filename}",
                                       style="green"))
                    case FileStatus.ERROR:
                        items.append(Text(f"✗ {filename}", style="red"))

        content = Align.center(Group(*items), vertical="middle")
        return Panel(
            content,
            title="Current Conversions",
            border_style="cyan",
            subtitle=f"Total: {self._total_files} | Remaining: {self._remaining_files}",
        )

    def _run_live_loop(self) -> None:
        with self._live:
            while self._running:
                self._live.update(self._render_view())
                time.sleep(0.5)

    def _sort_converting_files(self) -> None:
        with self._lock:
            self._converting_files.sort(
                key=lambda x: x[1] == FileStatus.CONVERTING,
            )

    def _get_report(self) -> dict[FileStatus, list[Path]]:
        d = defaultdict(list)
        for (fpath, status) in self._converting_files:
            d[status].append(fpath)
        return dict(d)
