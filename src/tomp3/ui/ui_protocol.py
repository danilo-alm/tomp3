from pathlib import Path
from typing import Optional, Protocol

from .custom_types import ReportType
from .file_status import FileStatus


class TUIProtocol(Protocol):
    def set_file_list(self, file_list: list[Path]) -> None:
        """Set the list of files to be converted."""
        pass

    def update_file_status(self, fpath: Path, status: FileStatus) -> None:
        """Update the status of a file being converted."""
        pass

    def stop(self) -> Optional[ReportType]:
        """Stop the TUI and clean up resources."""
        pass
    
    def force_update(self) -> None:
        """Force an update of the TUI display."""
        pass