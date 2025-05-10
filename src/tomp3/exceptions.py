import logging
import sys
from types import TracebackType
from typing import Optional


def exception_handling(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[TracebackType],
        logger: logging.Logger
    ) -> None:
    if not isinstance(exc_value, KeyboardInterrupt):
        logger.error("Uncaught exception",
                        exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)