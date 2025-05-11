import shutil
import threading
import time
from pathlib import Path
from typing import Optional

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text

from .custom_types import ReportType
from .file_status import FileStatus
from .files_view import FilesView


class ConversionUI:
    def __init__(self, visible_files: int = 20) -> None:
        self._file_view = FilesView([], visible_files)
        self._console = Console()
        self._visible_files = visible_files
        self._content_needs_update = False
        self._start()
    
    def stop(self) -> Optional[ReportType]:
        self._running = False
        self._live.stop()
        return self._file_view.get_report()

    def set_file_list(self, fpaths: list[Path]) -> None:
        self._file_view.set_files(fpaths)
        self._content_needs_update = True
    
    def update_file_status(self, fname: Path, status: FileStatus) -> None:
        self._file_view.update_file_status(fname, status)
        self._content_needs_update = True

    def _start(self) -> None:
        self._running = True
        self._live = Live(self._render_view(), refresh_per_second=7, screen=False)
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
                if self._content_needs_update:
                    self._live.update(self._render_view())
                    self._content_needs_update = False
                time.sleep(0.5)
