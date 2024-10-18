from copy import deepcopy
from enum import StrEnum, auto


class Component(StrEnum):
    ASR = auto()
    NER = auto()
    SPEAKER_CLASS = auto()
    SUMMARY = auto()
    CONFORMITY = auto()


DepGraph = dict[Component, set[Component]]
dep_graph: DepGraph = {
    Component.ASR: set(),
    Component.NER: {Component.ASR},
    Component.SPEAKER_CLASS: {Component.ASR},
    Component.SUMMARY: {Component.ASR, Component.SPEAKER_CLASS},
    Component.CONFORMITY: {Component.ASR, Component.SPEAKER_CLASS},
}


def _inverse_graph(graph: DepGraph) -> DepGraph:
    inv_graph: DepGraph = {key: set() for key in graph.keys()}
    for key, vals in graph.items():
        for val in vals:
            inv_graph[val].add(key)
    return inv_graph


def _topological_sort(graph: DepGraph) -> list[Component]:
    graph = deepcopy(graph)
    inv_graph = _inverse_graph(graph)

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


def get_execution_schedule(components: set[Component]) -> list[list[Component]]:
    def _get_all_deps() -> set[Component]:
        all_deps = set()
        queue = list(components)
        while len(queue) > 0:
            comp = queue.pop()
            all_deps.add(comp)
            all_deps.update(dep_graph[comp])
            queue.extend(dep_graph[comp] - all_deps)
        return all_deps

    schedule: list[list[Component]] = []
    top_order = _topological_sort(dep_graph)
    all_deps = _get_all_deps()
    for comp in top_order:
        if comp not in all_deps:
            continue
        if len(schedule) > 0 and len(dep_graph[comp].intersection(schedule[-1])) == 0:
            schedule[-1].append(comp)
        else:
            schedule.append([comp])
    return schedule


if __name__ == "__main__":
    res = get_execution_schedule({Component.SUMMARY, Component.CONFORMITY})
    print(res)
