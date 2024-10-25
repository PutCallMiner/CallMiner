from enum import StrEnum, auto
from functools import cache

from webapp.task_exec.tasks import (
    ASRTask,
    NERTask,
    RecordingTask,
    SpeakerClassifyTask,
    SummarizeTask,
)
from webapp.task_exec.utils import DAG, GraphDict, Schedule


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


class Scheduler:
    dep_graph: GraphDict[TaskType] = {
        TaskType.ASR: set(),
        TaskType.NER: {TaskType.ASR},
        TaskType.SPEAKER_CLASS: {TaskType.ASR},
        TaskType.SUMMARY: {TaskType.ASR, TaskType.SPEAKER_CLASS},
        TaskType.CONFORMITY: {TaskType.ASR, TaskType.SPEAKER_CLASS},
    }
    dep_dag = DAG(dep_graph)

    @classmethod
    def get_execution_schedule(
        cls, target_task_types: set[TaskType]
    ) -> Schedule[TaskType]:
        return cls.dep_dag.get_schedule(target_task_types)
