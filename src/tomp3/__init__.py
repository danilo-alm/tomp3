"""tomp3 - A tool for converting audio files to MP3 format."""

import sys

from tomp3.exceptions import exception_handling
from tomp3.logging import setup_logger

__version__ = "0.1.0"
__author__ = "Danilo Almeida"

logger = setup_logger()
sys.excepthook = lambda exc_type, exc_value, exc_traceback: exception_handling(
    exc_type, exc_value, exc_traceback, logger
)

__all__ = ["logger"]
