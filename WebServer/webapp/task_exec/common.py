from enum import StrEnum, auto
from functools import cache
from typing import TypeAlias

from webapp.task_exec.tasks import (
    ASRTask,
    NERTask,
    RecordingTask,
    SpeakerClassifyTask,
    SummarizeTask,
)
from webapp.task_exec.utils import DAG


class TaskType(StrEnum):
    ASR = auto()
    NER = auto()
    SPEAKER_CLASS = auto()
    SUMMARY = auto()
    CONFORMITY = auto()


@cache
def get_task_by_type(task_type: TaskType):
    component_to_task: dict[TaskType, type[RecordingTask]] = {
        TaskType.ASR: ASRTask,
        TaskType.NER: NERTask,
        TaskType.SPEAKER_CLASS: SpeakerClassifyTask,
        TaskType.SUMMARY: SummarizeTask,
        # TODO: add conformity check
    }
    return component_to_task[task_type]


Schedule: TypeAlias = list[list[TaskType]]


class Scheduler:
    dep_dag = DAG(
        {
            TaskType.ASR: set(),
            TaskType.NER: {TaskType.ASR, TaskType.SPEAKER_CLASS},
            TaskType.SPEAKER_CLASS: {TaskType.ASR},
            TaskType.SUMMARY: {TaskType.ASR, TaskType.SPEAKER_CLASS},
            TaskType.CONFORMITY: {TaskType.ASR, TaskType.SPEAKER_CLASS},
        }
    )

    @classmethod
    def get_execution_schedule(cls, target_task_types: set[TaskType]) -> Schedule:
        schedule: Schedule = []

        all_deps = cls.dep_dag.get_all_descendants(target_task_types)
        for task_type in cls.dep_dag.topological_order:
            if task_type not in all_deps:
                continue
            if (
                len(schedule) > 0
                and len(cls.dep_dag.get_outnodes(task_type).intersection(schedule[-1]))
                == 0
            ):
                schedule[-1].append(task_type)
            else:
                schedule.append([task_type])
        return schedule
