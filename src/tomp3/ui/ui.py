import shutil
import threading
import time
from pathlib import Path
from typing import Optional

from rich import box
from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text

from .custom_types import ReportType
from .file_status import FileStatus
from .files_view import FilesView
from .progress_tracker import ProgressTracker
from .ui_protocol import TUIProtocol


class ConversionUI(TUIProtocol):
    def __init__(self, visible_files: int) -> None:
        self._files_view = FilesView(visible_files)
        self._progress_tracker = ProgressTracker()
        
        self._content_needs_update = False
        self._running = True
        self._lock = threading.Lock()
        
        self._live = Live(self._render_view(), refresh_per_second=7, screen=False)
        self._ui_thread = threading.Thread(target=self._run_live_loop, daemon=True)
        self._ui_thread.start()

    def stop(self) -> Optional[ReportType]:
        self._running = False
        self._live.stop()
        return self._files_view.get_report()

    def set_file_list(self, fpaths: list[Path]) -> None:
        self._files_view.set_files(fpaths)
        self._progress_tracker.start(fpaths)
        self._mark_for_update()

    def update_file_status(self, fpath: Path, status: FileStatus) -> None:
        self._files_view.update_file_status(fpath, status)
        if status in {FileStatus.CONVERTED, FileStatus.ERROR}:
            self._progress_tracker.update_progress(fpath)
        self._mark_for_update()
    
    def force_update(self) -> None:
        self._live.update(self._render_view())
        self._live.refresh()

    def _mark_for_update(self) -> None:
        with self._lock:
            self._content_needs_update = True

    def _should_update(self) -> bool:
        with self._lock:
            result = self._content_needs_update
            self._content_needs_update = False
            return result

    def _run_live_loop(self) -> None:
        with self._live:
            while self._running:
                if self._should_update():
                    self._live.update(self._render_view())
                time.sleep(0.5)

    def _render_view(self) -> Panel:
        items = [
            self._build_file_item(fpath, status)
            for fpath, status in self._files_view.get_visible()
        ]
        items.reverse()
        content = self._layout_items(items)
        return self._build_panel(content)

    def _build_file_item(self, fpath: Path, status: FileStatus) -> Text | Spinner:
        filename = fpath.name
        match status:
            case FileStatus.WAITING:
                return Text(f"• {filename}", style="dim")
            case FileStatus.CONVERTED:
                return Text(f"✓ {filename}", style="green")
            case FileStatus.CONVERTING:
                return Spinner("dots", text=filename, style="green")
            case FileStatus.ERROR:
                return Text(f"✗ {filename}", style="red")
            case _:
                return Text(f"? {filename}", style="yellow")

    def _layout_items(self, items: list[Text | Spinner]) -> Group | Align:
        cols, _ = shutil.get_terminal_size()
        if cols > 95:
            return Align.center(Group(*items), vertical="middle")
        return Group(*items)

    def _build_panel(self, content: Group | Align) -> Panel:
        total, finished = self._files_view.get_status()
        percent = 100 * finished / total if total else 0
        eta = self._format_eta()
        return Panel(
            content,
            title="Current Conversions",
            subtitle=f"{percent:.1f}% Complete ({finished}/{total}) ETA: {eta}",
            border_style="cyan",
            box=box.ROUNDED
        )

    def _format_eta(self) -> str:
        try:
            eta = self._progress_tracker.get_eta_time()
            if eta.tm_hour > 0:
                return time.strftime('%Hh%Mm%Ss', eta)
            elif eta.tm_min > 0:
                return time.strftime('%Mm%Ss', eta)
            else:
                return time.strftime('%Ss', eta)
        except Exception:
            return "--"
