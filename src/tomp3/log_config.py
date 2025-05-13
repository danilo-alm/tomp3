import logging
import sys
from pathlib import Path
from types import TracebackType
from typing import Optional


def setup_logger(
    name: str = "tomp3",
    log_file: Path = Path.home() / ".tomp3.log",
    dry_run: bool = False,
    exceptions: bool = True
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.handlers.clear()
    logger.addHandler(file_handler)

    if dry_run:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.info("DRY RUNNING! NO FILES WILL BE MODIFIED!")
    
    if exceptions:
        sys.excepthook = lambda exc_type, exc_value, exc_traceback: _exception_handling(
            exc_type, exc_value, exc_traceback, logger
        )

    return logger


def _exception_handling(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType],
    logger: logging.Logger
    ) -> None:
    if not isinstance(exc_value, KeyboardInterrupt):
        logger.error("Uncaught exception",
                        exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)