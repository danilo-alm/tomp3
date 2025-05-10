import shutil
import threading
import time
from collections import OrderedDict, defaultdict
from enum import Enum, auto
from pathlib import Path
from typing import Optional

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text


class FileStatus(Enum):
    WAITING = auto()
    CONVERTING = auto()
    CONVERTED = auto()
    ERROR = auto()


FileListType = list[tuple[Path, FileStatus]]
ReportType = dict[FileStatus, list[Path]]


class _FilesView:
    def __init__(self, files: list[Path], visible: int) -> None:
        self.set_files(files)
        self._visible = visible
        self._lock = threading.RLock()

    def set_files(self, files: list[Path]) -> None:
        self._files = OrderedDict((f, FileStatus.WAITING) for f in files)
        self.total = len(files)
        self.finished = 0
    
    def update_file_status(self, fpath: Path, status: FileStatus) -> None:
        with self._lock:
            if fpath not in self._files:
                raise ValueError(f"File {fpath} not found in the list.")
            
            self._files[fpath] = status
            self._files.move_to_end(fpath, last=False)
            
            if status in {FileStatus.CONVERTED, FileStatus.ERROR}:
                self.finished += 1
    
    def get_visible(self) -> FileListType:
        with self._lock:
            return list(self._files.items())[:self._visible]
    
    def get_status(self) -> tuple[int, int]:
        return self.total, self.finished
    
    def get_report(self) -> ReportType:
        d = defaultdict(list)
        with self._lock:
            for (fpath, status) in self._files.items():
                d[status].append(fpath)
        return dict(d)


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
        self._file_view.set_files(fpaths)
    
    def update_file_status(self, fname: Path, status: FileStatus) -> None:
        return self._file_view.update_file_status(fname, status)

    def _start(self) -> None:
        self._running = True
        self._live = Live(self._render_view(), refresh_per_second=2, screen=False)
        self._thread = threading.Thread(target=self._run_live_loop, daemon=True)
        self._thread.start()

    def _render_view(self) -> Panel:
        items: list[ Text | Spinner ] = []

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
        total, finished = self._file_view.get_status()

        cols, _ = shutil.get_terminal_size()
        content = (
            Align.center(Group(*items[::-1]), vertical="middle")
            if cols > 95
            else Group(*items[::-1])
        )
        
        percent = 100 * finished / total if total else 0
        return Panel(
            content ,
            title="Current Conversions",
            border_style="cyan",
            subtitle=f"{percent:.1f}% Complete ({finished}/{total})",
        )

    def _run_live_loop(self) -> None:
        with self._live:
            while self._running:
                self._live.update(self._render_view())
                time.sleep(0.5)
