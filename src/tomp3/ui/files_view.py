import threading
from collections import OrderedDict, defaultdict
from itertools import islice
from pathlib import Path

from .custom_types import FileListType, ReportType
from .file_status import FileStatus


class FilesView:
    def __init__(self, visible: int) -> None:
        self._visible = visible
        self._lock = threading.Lock()
        self._files: OrderedDict[Path, FileStatus] = OrderedDict()
        self._total = 0
        self._finished = 0

    def set_files(self, files: list[Path]) -> None:
        with self._lock:
            self._files = OrderedDict((f, FileStatus.WAITING) for f in files)
            self._total = len(files)
            self._finished = 0

    def update_file_status(self, fpath: Path, status: FileStatus) -> None:
        with self._lock:
            if fpath not in self._files:
                raise ValueError(f"File {fpath} not found in the list.")
            
            self._files[fpath] = status
            self._files.move_to_end(fpath, last=False)

            if status in {FileStatus.CONVERTED, FileStatus.ERROR}:
                self._finished += 1

    def get_visible(self) -> FileListType:
        with self._lock:
            visible = list(islice(self._files.items(), self._visible))
            return sorted(
                visible,
                key=lambda x: 0 if x[1] == FileStatus.CONVERTING else 1
            )

    def get_status(self) -> tuple[int, int]:
        with self._lock:
            return self._total, self._finished

    def get_report(self) -> ReportType:
        with self._lock:
            report = defaultdict(list)
            for fpath, status in self._files.items():
                report[status].append(fpath)
            return dict(report)