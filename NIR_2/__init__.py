from NIR_1 import struct_expression, weights, DiGraph
from NIR_2.level import Level
from NIR_2.process import Process
from NIR_2.task import Task

import math
import matplotlib.pyplot as plt


def conveyor(graph: DiGraph, count_of_processes, debug=False):

    levels = []
    for level_id in range(1, graph.max_level + 1):

        nodes_names = graph.nodes_level(level_id)
        nodes = [graph.nodes.get(nid) for nid in nodes_names]

        level = Level(nodes)
        levels.append(level)

    process = Process(levels)
    processes = [process]

    for i in range(count_of_processes - 1):

        node_k = {}
        for ps in processes:
            if len(ps.levels) == 1 and len(ps.levels[0].nodes) == 1:
                node_k[ps.levels[0].nodes[0]['name']] = node_k.get(ps.levels[0].nodes[0]['name'], 0) + 1

        processes.sort(key=lambda x: (
            x.time_real / (node_k.get(x.levels[0].nodes[0]['name'], 1) if len(x.levels) == 1 and len(x.levels[0].nodes) == 1 else 1),
            -min(lvl.id for lvl in x.levels)
        ))

        process_to_split = processes.pop()
        new_processes = process_to_split.split()
        processes += new_processes

    processes.sort(key=lambda x: min([lvl.id for lvl in x.levels]))
    if debug:
        print(f'\n\nN={len(processes)}:')
        for p in processes:
            print(p)
    return processes


def modeling(graph, processes, times, debug=False):

    process_statistic = {
        'outage': 0,
        'total': 0,
    }
    schedule = []
    tasks = []
    tasks_created = 0
    tasks_times = []

    task_time = max(float(math.ceil(sum(node['weight'] for node in ps.get_level(1).nodes) / ps.get_level(1).coeff)) for ps in processes if ps.get_level(1))
    Task.id = 0

    t_log_from, t_log_to = (16, 100)
    t_log_dict = {ps.id: [] for ps in processes}

    tt = 0
    while tt < times:

        tt += 1

        if (len(schedule) % task_time) == 0:
            tasks.append(Task(graph))
            tasks_created += 1

        tasks.sort(key=lambda x: (len(x.nodes), -max(x.levels.keys())))

        process_statistic['total'] += len(processes)
        for ps in processes:
            if ps.buzy:
                ps.tick()
            elif len(schedule) > 0:
                process_statistic['outage'] += 1

        tasks_to_remove = []
        for task in tasks:
            task.do(processes)
            if task.ready:
                tasks_times.append(task.live_time)
                tasks_to_remove.append(task)

        magic = [tasks.remove(task) for task in tasks_to_remove]

        schedule_moment = {}
        schedule.append(schedule_moment)
        # print(f'\n\ntask_created: {tasks_created}; task_done: {len(tasks_times)}; time {len(schedule)}')
        for ps in processes:
            # print(ps)
            if ps.buzy:
                schedule_moment[ps.id] = {
                    'nodes': ps.task.process[ps],
                    'task': ps.task.id,
                }

        for index, ps in enumerate(processes):

            now_level = 0
            if ps.task:
                for level in ps.levels:
                    level_nodes = [node['name'] for node in level.nodes]
                    if any(node_name in ps.task.nodes for node_name in level_nodes):
                        now_level = level.id
                        break

            if debug:
                print(f'\n\ntask_created: {tasks_created}; task_done: {len(tasks_times)}; time {len(schedule)}')
                if ps.task:
                    print(f'{index}: Task: {ps.task.id} Level: {now_level} (Time: {ps.buzy})')
                else:
                    print(f'{index}: None')

            if tt >= t_log_from and tt <= t_log_to:
                if ps.task:
                    ps_log = f'T{ps.task.id}[{now_level}]'
                else:
                    ps_log = '-'
                t_log_dict[ps.id].append(ps_log)

    print('%-10s' % '')
    for key in range(len(t_log_dict.keys())):
        print('%-10s' % ('P[%d]' % key), end='')
    print()

    key = list(t_log_dict.keys())[0]
    for t in range(len(t_log_dict[key])):
        print('%-10s' % f't{t_log_from + t}', end='')
        for val in t_log_dict.values():
            print('%-10s' % val[t], end='')
        print()

    return schedule, process_statistic, tasks_times


if __name__ == '__main__':

    expression = '(x1+x2+x3+x4) * (x5+x6+x7+x8+x9) * (x10+x11+x12+x13) * (x14+x15+x16)'
    structed = struct_expression(expression)

    digraph_nw = DiGraph(structed)
    # nx.draw(digraph_nw, pos=digraph_nw.pos, with_labels=True, node_color='w', font_size=10, linewidths=2, node_size=450)
    # ax = plt.gca()  # to get the current axis
    # ax.collections[0].set_edgecolor("#000000")
    # ax.collections[0].set_linewidth(1)
    # plt.show()
    #
    digraph = DiGraph(structed, edge_weight=weights)
    # processes = conveyor(digraph_nw, 3, True)
    # processes = conveyor(digraph_nw, 2, True)
    # schedule, process_statistic, tasks_times = modeling(digraph_nw, processes, 100)

    # easy balance
    times = []
    usage = []
    x = list(range(1, 30))
    for process_count in x:
        print(f'modeling: processes={process_count}')
        processes = conveyor(digraph, process_count, debug=True)
        schedule, process_statistic, tasks_times = modeling(digraph, processes, 200)
        times.append(sum(tasks_times) / len(tasks_times))
        usage.append((process_statistic['total'] - process_statistic['outage']) / process_statistic['total'])

    # === plot Tmin ===
    line, = plt.plot(x, times, 'k', label='$T_{conveyor}$')
    line_min, = plt.plot([min(x), max(x)], [11, 11], 'k--', label='$T_{min}$')
    plt.xlabel('processes')
    plt.ylabel('T')
    plt.legend(handles=[line, line_min])
    plt.xlim([1, max(x)])
    plt.ylim([1, max(times) + 1])
    plt.grid()
    plt.show()

    # === plot K usage ===
    line, = plt.plot(x, usage, 'k', label='$K_{conveyor}$')
    line_min, = plt.plot([min(x), max(x)], [1, 1], 'k--', label='$K_{usage} = 1$')
    plt.xlabel('processes')
    plt.ylabel('$K_{usage}$')
    plt.legend(handles=[line, line_min])
    plt.xlim([1, max(x)])
    plt.ylim([0, 1.5])
    plt.grid()
    plt.show()