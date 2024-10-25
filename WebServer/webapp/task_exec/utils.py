import asyncio
import time
from functools import cached_property
from typing import Generic, Hashable, TypeAlias, TypeVar

from asgiref.sync import sync_to_async
from celery import Task  # type: ignore[import]
from graphlib import TopologicalSorter

from webapp.errors import TaskTimeoutError


# Converts a Celery tasks to an async function
def task_to_async(timeout: float | None = None):
    def timeout_wrapper(task: Task):
        async def wrapper(*args, **kwargs):
            delay = 0.1
            async_result = await sync_to_async(task.apply_async)(*args, **kwargs)
            start_time = time.time()
            while not async_result.ready():
                if (timeout is not None) and (time.time() - start_time) > timeout:
                    raise TaskTimeoutError(task.name, async_result.id)
                await asyncio.sleep(delay)
                delay = min(delay * 1.5, 2)  # exponential backoff, max 2 seconds
            return async_result.get()

        return wrapper

    return timeout_wrapper


T = TypeVar("T", bound=Hashable)
GraphDict: TypeAlias = dict[T, set[T]]
Schedule: TypeAlias = list[list[T]]


class DAG(Generic[T]):
    def __init__(self, graph_data: GraphDict[T]):
        self._graph_data = graph_data

    @cached_property
    def inverse(self) -> GraphDict[T]:
        inv_graph: GraphDict[T] = {key: set() for key in self._graph_data.keys()}
        for key, vals in self._graph_data.items():
            for val in vals:
                inv_graph[val].add(key)
        return inv_graph

    @cached_property
    def topological_order(self):
        return list(TopologicalSorter(self._graph_data).static_order())

    def _get_all_descendants(self, target_nodes: set[T]) -> set[T]:
        all_deps = set()
        queue = list(target_nodes)
        while len(queue) > 0:
            task_t = queue.pop()
            all_deps.add(task_t)
            all_deps.update(self._graph_data[task_t])
            queue.extend(self._graph_data[task_t] - all_deps)
        return all_deps

    def get_schedule(self, target_nodes: set[T]) -> Schedule:
        schedule: Schedule = []

        all_deps = self._get_all_descendants(target_nodes)
        for task_type in self.topological_order:
            if task_type not in all_deps:
                continue
            if (
                len(schedule) > 0
                and len(self._graph_data[task_type].intersection(schedule[-1])) == 0
            ):
                schedule[-1].append(task_type)
            else:
                schedule.append([task_type])
        return schedule
