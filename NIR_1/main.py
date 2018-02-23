import networkx as nx
import matplotlib.pyplot as plt
import shlex
import re
from copy import deepcopy


weights = {
    '+': 1,
    '*': 3,
}


class DiGraph(nx.DiGraph):

    max_level = 0
    edge_weight = {}

    def __init__(self, structed_expression, edge_weight=None):

        super().__init__()

        self.pos = {}
        if edge_weight:
            self.edge_weight = edge_weight

        for operations in structed_expression:
            for name, edges, expression, level, act in operations:

                if level > self.max_level:
                    self.max_level = level

                if self.node_with_expression(expression) is None:
                    weight = self.edge_weight.get(act, 1)
                    self.add_node(name, expression=expression, edges=edges, level=level, act=act, weight=weight)

        self.rebuild()

    def invert(self):
        edges = list(self.edges())
        for edge in edges:
            u, v = edge
            weight = self.get_edge_data(u, v).get('weight', 1)
            self.remove_edge(u, v)
            self.add_edge(v, u, weight=weight)

    @property
    def node_end(self):
        nodes = self.nodes()
        for node_name in nodes:
            if nodes[node_name]['level'] == self.max_level:
                return node_name

    def node_with_expression(self, expression):
        nodes = self.nodes()
        for node_name in nodes:
            if nodes[node_name]['expression'] == expression:
                return node_name

        return None

    def nodes_level(self, level):

        nodes = self.nodes()
        nodes_level = []

        for node_name in nodes:
            if nodes[node_name]['level'] == level:
                nodes_level.append(node_name)

        return nodes_level

    def nodes_root(self):

        root_nodes = []

        def _tree_struct(root):
            neighbors = list(self.neighbors(root))
            # if parent != None:   #this should be removed for directed graphs.
            #     neighbors.remove(parent)  #if directed, then parent not in neighbors.

            if len(neighbors) != 0:
                for neighbor in neighbors:
                    if len(list(self.neighbors(neighbor))) == 0:
                        root_nodes.append(neighbor)
                    _tree_struct(neighbor)

        self.invert()
        _tree_struct(self.nodes_level(self.max_level)[0])
        self.invert()

        return root_nodes

    def rebuild(self):

        nodes = self.nodes()
        for node_index in nodes:
            node_dict = nodes[node_index]

            for from_node in node_dict['edges']:
                weight = self.edge_weight.get(node_dict['act'], 1)
                if from_node in list(self.nodes):
                    self.add_edge(from_node, node_index, weight=weight)

        self.rebuild_pos()

    def rebuild_pos(self, xcenter=0, level_height=1, level_width=1):

        nodes = self.nodes(data=True)

        # root nodes
        nodes_root = self.nodes_root()
        xstart = xcenter - (len(nodes_root) * level_width) / 2
        for index, node_name in enumerate(nodes_root):
            self.pos[node_name] = (xstart + index * level_width, 0)

        # levels
        for level in range(1, self.max_level+1):
            nodes_level = self.nodes_level(level)
            for index, node_name in enumerate(nodes_level):
                edges = nodes[node_name]['edges']
                middle = sum([self.pos[edge][0] for edge in edges])/len(edges)
                self.pos[node_name] = (middle, level*level_height)

    def shortest_longest_path(self, allowed=None, disallowed=None):

        max_cost = 0
        shortest_longest_path = None

        for node_name in self.nodes_root():

            if allowed and node_name not in allowed:
                continue

            if disallowed and node_name in disallowed:
                continue

            path_cost = nx.dijkstra_path_length(self, node_name, self.node_end)
            if path_cost >= max_cost:
                path = nx.dijkstra_path(self, node_name, self.node_end)
                if not shortest_longest_path or len(path) < len(shortest_longest_path) or path_cost > max_cost:
                    shortest_longest_path = path

                max_cost = path_cost

        return shortest_longest_path


def struct_expression(expression: str):

    args = []
    for val in shlex.shlex(expression):
        if re.findall(r'^\w+\d+$', val):
            arg = val, [], val, 0, None
            args.append(arg)

    structed = [args]

    expression = expression.replace(' ', '')
    multed_expression = expression.split('*')

    for index, expr in enumerate(multed_expression):
        expr = expr.replace('(', '')
        expr = expr.replace(')', '')
        multed_expression[index] = expr.split('+')

    y = 0
    # multed_expression = sorted(multed_expression, key=len)
    while len(multed_expression) > 1:

        operations = []

        # processing inner sums
        sums = [(index, value) for index, value in enumerate(multed_expression) if isinstance(value, str)]
        for sumindex, sum_tuple in enumerate(sums):
            valindex_1, value_1 = sum_tuple
            if sumindex + 1 < len(sums):
                valindex_2, value_2 = sums[sumindex+1]
                a, b = multed_expression[valindex_1], multed_expression.pop(valindex_2)
                multed_expression[valindex_1] = f'y{y}'
                operations.append( (multed_expression[valindex_1], (a, b), f'{a}*{b}', len(structed), '*') )
                y += 1
                sums.pop(valindex_2), sums.pop(valindex_1)

        for index, expr in enumerate(multed_expression):

            # processing inner list
            if isinstance(expr, list):

                for valindex, value in enumerate(expr):
                    if valindex+1 < len(expr):
                        a, b = expr[valindex], expr.pop(valindex+1)
                        expr[valindex] = f'y{y}'
                        operations.append( (expr[valindex], (a, b), f'{a}+{b}', len(structed), '+') )
                        y += 1

                if len(expr) == 1:
                    multed_expression[index] = expr.pop(0)

        structed.append(operations)

    return structed


def make_threads(graph_origin: DiGraph, processes=1):

    graph = deepcopy(graph_origin)
    nodes = graph.nodes(data=True)

    locked_nodes = {}
    threads = []
    time_moment = 0
    while graph.number_of_nodes() > 1:

        allowed = graph.nodes_root()

        decrement = [(node_name, lock_time) for node_name, lock_time in locked_nodes.items() if lock_time > 0]
        for node_name, lock_time in decrement:
            if lock_time > 1:
                locked_nodes[node_name] = lock_time - 1
            else:
                del locked_nodes[node_name]

        removed_temp = []
        if len(threads) <= time_moment:
            thread = []
            threads.append(thread)
        else:
            thread = threads[time_moment]

        while len(thread) < processes:
            path = graph.shortest_longest_path(allowed=allowed, disallowed=locked_nodes)

            if not path:
                break

            if path[0] not in allowed or path[1] in locked_nodes.keys():
                data = path[0], nodes[path[0]], graph.neighbors(path[0])
                removed_temp.append(data)
                graph.remove_node(path[0])
                continue

            edge_weight = graph.get_edge_data(path[0], path[1]).get('weight', 1)

            for node_name in path:
                if locked_nodes.get(node_name, 0) < edge_weight:
                    locked_nodes[node_name] = edge_weight

            time_delta = 0
            while edge_weight > 0:

                if len(threads) <= time_moment+time_delta:
                    thread = []
                    threads.append(thread)
                else:
                    thread = threads[time_moment+time_delta]

                if not len(thread) >= processes:
                    thread.append(path[1])
                    edge_weight -= 1

                time_delta += 1

            for node_name in nodes[path[1]]['edges']:
                graph.remove_node(node_name)

        for node, node_data, edges in removed_temp:
            graph.add_node(node, **node_data)
            for to_node in edges:
                graph.add_edge(node, to_node)

        time_moment += 1

    return threads


if __name__ == '__main__':

    expression = ' (x1+x2+x3+x4)* (x5+x6+x7+x8+x9)* (x10+x11+x12+x13)* (x14+x15+x16)'
    structed = struct_expression(expression)

    # === noweight ===
    digraph_nw = DiGraph(structed)
    nx.draw(digraph_nw, pos=digraph_nw.pos, with_labels=True, node_color='w', font_size=10, linewidths=2, node_size=450)
    ax = plt.gca()  # to get the current axis
    ax.collections[0].set_edgecolor("#000000")
    ax.collections[0].set_linewidth(1)
    plt.show()

    # === weight ===
    digraph = DiGraph(structed, edge_weight=weights)
    # nx.draw(digraph, pos=digraph.pos, with_labels=True, node_color='w', font_size=10, linewidths=2, node_size=450)
    # ax = plt.gca()  # to get the current axis
    # ax.collections[0].set_edgecolor("#000000")
    # ax.collections[0].set_linewidth(1)
    # labels = nx.get_edge_attributes(digraph, 'weight')
    # nx.draw_networkx_edge_labels(digraph, pos=digraph.pos, edge_labels=labels)
    # plt.show()

    threaded_tasks = []
    threaded_tasks_nw = []
    x, y = [], []
    for i in range(1, 10):

        threads = make_threads(digraph_nw, i)
        threaded_tasks_nw.append(threads)

        threads = make_threads(digraph, i)
        threaded_tasks.append(threads)
        print(f'\n\nThreads count [N={i}].')
        x.append(i)
        y.append(len(threads))

        print('%-10s' % 'process', end='')
        for process in range(i):
            print('%-10s' % f'P[{process}]', end='')
        print()

        for time_moment, thread in enumerate(threads):
            print('%-10s' % f'T[{time_moment}]', end='')
            for task in thread:
                print('%-10s' % task, end='')
            print()

    # === plot Tmin ===
    line, = plt.plot(x, y, 'k', label='$T_{threaded}$')
    line_min, = plt.plot([min(x), max(x)], [min(y), min(y)], 'k--', label='$T_{min}$')
    plt.xlabel('processes')
    plt.ylabel('T')
    plt.legend(handles=[line, line_min])
    plt.xlim([1, max(x)])
    plt.ylim([min(y) - 1, max(y) + 1])
    plt.grid()
    plt.show()

    P_t_min_1 = y.index(min(y))
    y_nw = [len(tasks) for tasks in threaded_tasks_nw]
    P_t_min_2 = y_nw.index(min(y_nw))

    # === plot Kp ===
    x = [i for i in range(1, len(threaded_tasks))]
    y1, y2 = [], []
    for threads_count in x:

        threads = threaded_tasks[threads_count-1]
        y1.append( sum([len(tasks) for tasks in threads]) / (len(threads) * threads_count) )

        threads = threaded_tasks_nw[threads_count - 1]
        y2.append( sum([len(tasks) for tasks in threads]) / (len(threads) * threads_count) )

    line_1, = plt.plot(x, y1, 'k', label='$K_{pu} (T[+] = 1; T[*] =3;)$')
    line_2, = plt.plot(x, y2, 'k--', label='$K_{pu} (T[+] = T[*] = 1)$')
    # line_min_1, = plt.plot(P_t_min_1 + 1, y1[P_t_min_1], 'k.', markersize=15, label='$K_{puT_{min}}$')
    # line_min_2, = plt.plot(P_t_min_2 + 1, y2[P_t_min_2], 'k.', markersize=15, label='$K_{puT_{min}}$')
    plt.xlabel('Processes')
    plt.ylabel('Usage')
    plt.legend(handles=[line_1, line_2])
    plt.xlim([1, max(x)])
    plt.ylim([0, 1.1])
    plt.grid()
    plt.show()