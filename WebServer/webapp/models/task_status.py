from enum import StrEnum, auto


class TaskStatus(StrEnum):
    IN_PROGRESS = auto()
    FINISHED = auto()
    FAILED = auto()
