"""tomp3 - A tool for converting audio files to MP3 format."""

from tomp3.converter import Converter
from tomp3.logging import setup_logger

__version__ = "0.1.0"
__author__ = "Danilo Almeida"

logger = setup_logger()

__all__ = ["Converter", "logger"]
