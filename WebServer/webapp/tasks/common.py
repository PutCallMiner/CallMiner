import asyncio
from copy import deepcopy
from enum import StrEnum, auto
from typing import TypeAlias

from webapp.models.record import Recording


class Component(StrEnum):
    ASR = auto()
    NER = auto()
    SPEAKER_CLASS = auto()
    SUMMARY = auto()
    CONFORMITY = auto()


Graph: TypeAlias = dict[Component, set[Component]]
_Schedule: TypeAlias = list[list[Component]]

dep_graph: Graph = {
    Component.ASR: set(),
    Component.NER: {Component.ASR},
    Component.SPEAKER_CLASS: {Component.ASR},
    Component.SUMMARY: {Component.ASR, Component.SPEAKER_CLASS},
    Component.CONFORMITY: {Component.ASR, Component.SPEAKER_CLASS},
}


# TODO: perhaps move this class to a separate file
class Scheduler:
    @staticmethod
    def _inverse_graph(graph: Graph) -> Graph:
        inv_graph: Graph = {key: set() for key in graph.keys()}
        for key, vals in graph.items():
            for val in vals:
                inv_graph[val].add(key)
        return inv_graph

    @staticmethod
    def _topological_sort(graph: Graph) -> list[Component]:
        graph = deepcopy(graph)
        inv_graph = Scheduler._inverse_graph(graph)

        starting = {key for key, vals in graph.items() if len(vals) == 0}
        if len(starting) == 0:
            raise ValueError("Dependency dict results in a graph with cycles")

        sorted_nodes: list[Component] = []

        while len(starting) > 0:
            n = starting.pop()
            sorted_nodes.append(n)
            for m in inv_graph[n]:
                graph[m].difference_update({n})
                if len(graph[m]) == 0:
                    starting.add(m)
            inv_graph[n].clear()

        if sum(map(len, inv_graph.values())) > 0:
            raise ValueError("Graph has at least one cycle")
        return sorted_nodes

    @staticmethod
    def get_execution_schedule(components: set[Component]) -> _Schedule:
        def _get_all_deps() -> set[Component]:
            all_deps = set()
            queue = list(components)
            while len(queue) > 0:
                comp = queue.pop()
                all_deps.add(comp)
                all_deps.update(dep_graph[comp])
                queue.extend(dep_graph[comp] - all_deps)
            return all_deps

        schedule: _Schedule = []
        top_order = Scheduler._topological_sort(dep_graph)
        all_deps = _get_all_deps()
        for comp in top_order:
            if comp not in all_deps:
                continue
            if (
                len(schedule) > 0
                and len(dep_graph[comp].intersection(schedule[-1])) == 0
            ):
                schedule[-1].append(comp)
            else:
                schedule.append([comp])
        return schedule


class RecordingProcessor:
    def __init__(self, recording: Recording):
        self.recording = recording

    async def _is_component_in_db(self, component: Component) -> bool:
        match component:
            case Component.ASR:
                return self.recording.transcript is not None
            case Component.NER:
                return self.recording.ner is not None
            case Component.SPEAKER_CLASS:
                return self.recording.speaker_mapping is not None
            case Component.SUMMARY:
                return self.recording.summary is not None
            case Component.CONFORMITY:
                # TODO
                return True

    async def execute_component(self, component: Component):
        # TODO: perhaps have each component as a class with methods check_presence(Recording) and execute()
        match component:
            case Component.ASR:
                pass
            case Component.NER:
                pass
            case Component.SUMMARY:
                pass
            case Component.SPEAKER_CLASS:
                pass
            case Component.CONFORMITY:
                pass

    async def run_with_dependencies(self, required_components: list[Component]):
        schedule = Scheduler.get_execution_schedule(set(required_components))
        for step in schedule:
            coroutines = [
                self.execute_component(comp)
                for comp in step
                if not self._is_component_in_db(comp)
            ]
            await asyncio.gather(*coroutines)


if __name__ == "__main__":
    res = Scheduler.get_execution_schedule({Component.SUMMARY, Component.CONFORMITY})
    print(res)
