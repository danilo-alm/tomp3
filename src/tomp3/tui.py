import shutil
import threading
import time
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Optional

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text


class FileStatus(Enum):
    WAITING = 1
    CONVERTING = 2
    CONVERTED = 3
    ERROR = 4


FileListType = list[tuple[Path, FileStatus]]
ReportType = dict[FileStatus, list[Path]]


class _FilesView:

    SORTING_PRIORITY = {
        FileStatus.WAITING: 3,
        FileStatus.CONVERTING: 1,
        FileStatus.CONVERTED: 2,
        FileStatus.ERROR: 2
    }

    def __init__(self, files: list[Path], visible: int) -> None:
        self._files = [(f, FileStatus.WAITING) for f in files]
        self._visible = visible
        self._lock = threading.RLock()
        self.total = len(files)
        self.remaining = len(files)
    
    def update_file_status(self, fpath: Path, status: FileStatus) -> None:
        self._lock.acquire()
        idx = -1
        for i, (_fpath, _) in enumerate(self._files):
            if _fpath == fpath:
                idx = i
                break
        
        if idx == -1:
            raise ValueError(f"File {fpath} not found in the list.")
        
        self._files.pop(idx)
        self._files.insert(0, (fpath, status))

        if status == FileStatus.CONVERTED or status == FileStatus.ERROR:
            self.remaining -= 1
        
        self._sort_visible()
        self._lock.release()
    
    def get_visible(self) -> FileListType:
        return self._files[:self._visible]
    
    def get_status(self) -> tuple[int, int]:
        return self.total, self.remaining
    
    def get_report(self) -> ReportType:
        d = defaultdict(list)
        for (fpath, status) in self._files:
            d[status].append(fpath)
        return dict(d)
    
    def _sort_visible(self) -> None:
        with self._lock:
            self._files[:self._visible] = sorted(
                self._files[:self._visible],
                key=lambda x: self.SORTING_PRIORITY[x[1]]
            )
    

class ConversionUI:
    def __init__(self, visible_files: int = 20) -> None:
        self._file_view = _FilesView([], visible_files)
        self._console = Console()
        self._visible_files = visible_files
        self._start()
    
    def stop(self) -> Optional[ReportType]:
        self._running = False
        self._live.stop()
        return self._file_view.get_report()

    def set_file_list(self, fpaths: list[Path]) -> None:
        self._file_view = _FilesView(fpaths, self._visible_files)
    
    def update_file_status(self, fname: Path, status: FileStatus) -> None:
        return self._file_view.update_file_status(fname, status)

    def _start(self) -> None:
        self._running = True
        self._live = Live(self._render_view(), refresh_per_second=2, screen=False)
        self._thread = threading.Thread(target=self._run_live_loop, daemon=True)
        self._thread.start()

    def _render_view(self) -> Panel:
        items: list[ Text | Spinner ] = []
        total, remaining = 0, 0

        for fpath, status in self._file_view.get_visible():
            filename = fpath.name
            match status:
                case FileStatus.WAITING:
                    items.append(Text(f"• {filename}", style="dim"))
                case FileStatus.CONVERTED:
                    items.append(Text(f"✓ {filename}", style="green"))
                case FileStatus.CONVERTING:
                    items.append(Spinner("dots", text=f"{filename}", style="green"))
                case FileStatus.ERROR:
                    items.append(Text(f"✗ {filename}", style="red"))
        total, remaining = self._file_view.get_status()

        cols, _ = shutil.get_terminal_size()
        content = (
            Align.center(Group(*items[::-1]), vertical="middle")
            if cols > 95
            else Group(*items[::-1])
        )
        
        return Panel(
            content ,
            title="Current Conversions",
            border_style="cyan",
            subtitle=f"Total: {total} | Remaining: {remaining}",
        )

    def _run_live_loop(self) -> None:
        with self._live:
            while self._running:
                self._live.update(self._render_view())
                time.sleep(0.5)
