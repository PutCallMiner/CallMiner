from enum import StrEnum, auto
from functools import cache
from typing import TypeAlias

from graphlib import TopologicalSorter

from webapp.task_exec.tasks import ASRTask, NERTask, SpeakerClassifyTask, SummarizeTask
from webapp.task_exec.tasks.base import RecordingTask


class TaskType(StrEnum):
    ASR = auto()
    NER = auto()
    SPEAKER_CLASS = auto()
    SUMMARY = auto()
    CONFORMITY = auto()


Graph: TypeAlias = dict[TaskType, set[TaskType]]
Schedule: TypeAlias = list[list[TaskType]]


def _inverse_graph(graph: Graph) -> Graph:
    inv_graph: Graph = {key: set() for key in graph.keys()}
    for key, vals in graph.items():
        for val in vals:
            inv_graph[val].add(key)
    return inv_graph


@cache
def get_task_dep_graph() -> Graph:
    return {
        TaskType.ASR: set(),
        TaskType.NER: {TaskType.ASR},
        TaskType.SPEAKER_CLASS: {TaskType.ASR},
        TaskType.SUMMARY: {TaskType.ASR, TaskType.SPEAKER_CLASS},
        TaskType.CONFORMITY: {TaskType.ASR, TaskType.SPEAKER_CLASS},
    }


@cache
def get_task_topological_order() -> list[TaskType]:
    dep_graph = get_task_dep_graph()
    return list(TopologicalSorter(dep_graph).static_order())


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
