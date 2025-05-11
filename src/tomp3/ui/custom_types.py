from pathlib import Path

from .file_status import FileStatus

FileListType = list[tuple[Path, FileStatus]]
ReportType = dict[FileStatus, list[Path]]