import networkx as nx
import matplotlib.pyplot as plt
import shlex
import re
from copy import deepcopy


class DiGraph(nx.DiGraph):

    max_level = 0

    def __init__(self, structed_expression):

        super().__init__()
        self.pos = {}

        for operations in structed_expression:
            for name, edges, expression, level in operations:

                if level > self.max_level:
                    self.max_level = level

                if self.node_with_expression(expression) is None:
                    self.add_node(name, expression=expression, edges=edges, level=level)

        self.rebuild()

    def invert(self):
        edges = list(self.edges())
        for edge in edges:
            u, v = edge
            self.remove_edge(u, v)
            self.add_edge(v, u)

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

        _tree_struct(self.nodes_level(self.max_level)[0])
        return root_nodes

    def rebuild(self):

        nodes = self.nodes()
        for node_index in nodes:
            node_dict = nodes[node_index]

            for from_node in node_dict['edges']:
                if from_node in list(self.nodes):
                    self.add_edge(from_node, node_index)

        self.invert()
        self.rebuild_pos()
        self.invert()

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


def struct_expression(expression: str):

    args = []
    for val in shlex.shlex(expression):
        if re.findall(r'^\w+\d+$', val):
            arg = val, [], val, 0
            args.append(arg)

    structed = [args]

    expression = expression.replace(' ', '')
    multed_expression = expression.split('*')

    for index, expr in enumerate(multed_expression):
        expr = expr.replace('(', '')
        expr = expr.replace(')', '')
        multed_expression[index] = expr.split('+')

    y = 0
    multed_expression = sorted(multed_expression, key=len)
    while len(multed_expression) > 1:

        operations = []

        # processing inner sums
        sums = [(index, value) for index, value in enumerate(multed_expression) if isinstance(value, str)]
        for sumindex, sum_tuple in enumerate(sums):
            valindex, value = sum_tuple
            if valindex + 1 < len(sums):
                a, b = multed_expression[valindex], multed_expression.pop(valindex + 1)
                multed_expression[valindex] = f'y{y}'
                operations.append( (multed_expression[valindex], (a, b), f'y{y}', len(structed)) )
                y += 1
                sums.pop(valindex + 1), sums.pop(valindex)

        for index, expr in enumerate(multed_expression):

            # processing inner list
            if isinstance(expr, list):

                for valindex, value in enumerate(expr):
                    if valindex+1 < len(expr):
                        a, b = expr[valindex], expr.pop(valindex+1)
                        expr[valindex] = f'y{y}'
                        operations.append( (expr[valindex], (a, b), f'{a}+{b}', len(structed)) )
                        y += 1

                if len(expr) == 1:
                    multed_expression[index] = expr.pop(0)

        structed.append(operations)

    return structed


def make_threads(graph_origin: DiGraph, processes=1):

    graph = deepcopy(graph_origin)
    graph.invert()
    for root in graph.nodes_root():
        graph.remove_node(root)
    graph.invert()

    nodes = graph.nodes(data=True)

    threads = []
    while graph.nodes():

        graph.invert()
        if len(graph.nodes) > 1:
            allowed = graph.nodes_root()
        else:
            allowed = list(graph.nodes)
        graph.invert()

        removed_temp = []
        thread = []
        threads.append(thread)

        while len(thread) < processes:
            path = nx.algorithms.dag_longest_path(graph)

            if not path:
                break

            if path[0] not in allowed:
                data = path[0], nodes[path[0]], graph.neighbors(path[0])
                removed_temp.append(data)
                graph.remove_node(path[0])
                continue

            thread.append(path[0])
            graph.remove_node(path[0])

        for node, node_data, edges in removed_temp:
            graph.add_node(node, **node_data)
            for to_node in edges:
                graph.add_edge(node, to_node)

    return threads


if __name__ == '__main__':
    expression = '(x1+x2+x3+x4)* (x5+x6+x7+x8+x9)* (x10+x11+x12+x13)* (x14+x15+x16)'
    structed = struct_expression(expression)
    digraph = DiGraph(structed)
    nx.draw(digraph, pos=digraph.pos, with_labels=True, node_color='w', font_size=10, linewidths=2, node_size=450)
    ax = plt.gca()  # to get the current axis
    ax.collections[0].set_edgecolor("#000000")
    ax.collections[0].set_linewidth(1)
    plt.show()

    x, y = [], []
    for i in range(1, 10):
        threads = make_threads(digraph, i)
        print(f'threads count [N={i}]. Threaded: {threads}')
        x.append(i)
        y.append(len(threads))

    line, = plt.plot(x, y, 'k', label='$T_{threaded}$')
    line_min, = plt.plot([min(x), max(x)], [min(y), min(y)], 'k--', label='$T_{min}$')
    plt.xlabel('processes')
    plt.ylabel('T')
    plt.legend(handles=[line, line_min])
    plt.xlim([1, max(x)])
    plt.ylim([min(y) - 1, max(y) + 1])
    plt.grid()
    plt.show()