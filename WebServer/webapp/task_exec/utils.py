from functools import cached_property
from typing import Generic, Hashable, TypeAlias, TypeVar

import httpx
from graphlib import TopologicalSorter


async def async_request_with_timeout(
    url: str,
    json_data: dict,
    timeout: float | None,
    not_ok_error_t: type[Exception],
):
    """Makes an async request to url with json_data and raises
    corresponding errors on timeout or if response isn't 2XX"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json=json_data,
            timeout=timeout,
        )
    if not resp.is_success:
        raise not_ok_error_t(resp.content.decode())
    return resp.json()


T = TypeVar("T", bound=Hashable)
GraphDict: TypeAlias = dict[T, set[T]]


class DAG(Generic[T]):
    def __init__(self, graph_data: GraphDict[T]):
        self._graph_data = graph_data

    @cached_property
    def inverse(self) -> "DAG[T]":
        inv_graph: GraphDict[T] = {key: set() for key in self._graph_data.keys()}
        for key, vals in self._graph_data.items():
            for val in vals:
                inv_graph[val].add(key)
        return DAG(inv_graph)

    @cached_property
    def topological_order(self):
        return list(TopologicalSorter(self._graph_data).static_order())

    def get_outnodes(self, node: T) -> set[T]:
        return self._graph_data[node]

    def get_all_descendants(self, target_nodes: set[T]) -> set[T]:
        all_deps = set()
        queue = list(target_nodes)
        while len(queue) > 0:
            task_t = queue.pop()
            all_deps.add(task_t)
            all_deps.update(self._graph_data[task_t])
            queue.extend(self._graph_data[task_t] - all_deps)
        return all_deps

    def get_ancestors(self, node: T) -> set[T]:
        ancestors = self.inverse.get_all_descendants({node})
        ancestors.remove(node)
        return ancestors
