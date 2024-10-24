from webapp.task_exec.common import (
    Schedule,
    TaskType,
    get_task_dep_graph,
    get_task_topological_order,
)


class Scheduler:
    @staticmethod
    def get_execution_schedule(target_task_types: set[TaskType]) -> Schedule:
        def _get_all_deps() -> set[TaskType]:
            all_deps = set()
            queue = list(target_task_types)
            while len(queue) > 0:
                task_t = queue.pop()
                all_deps.add(task_t)
                all_deps.update(dep_graph[task_t])
                queue.extend(dep_graph[task_t] - all_deps)
            return all_deps

        schedule: Schedule = []
        dep_graph = get_task_dep_graph()
        top_order = get_task_topological_order()

        all_deps = _get_all_deps()
        for task_type in top_order:
            if task_type not in all_deps:
                continue
            if (
                len(schedule) > 0
                and len(dep_graph[task_type].intersection(schedule[-1])) == 0
            ):
                schedule[-1].append(task_type)
            else:
                schedule.append([task_type])
        return schedule


if __name__ == "__main__":
    print(Scheduler.get_execution_schedule({TaskType.CONFORMITY}))
