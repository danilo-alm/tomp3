from enum import Enum, auto


class FileStatus(Enum):
    WAITING = auto()
    CONVERTING = auto()
    CONVERTED = auto()
    ERROR = auto()