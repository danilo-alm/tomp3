import threading
from collections import OrderedDict, defaultdict
from pathlib import Path

from .custom_types import FileListType, ReportType
from .file_status import FileStatus


class FilesView:
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