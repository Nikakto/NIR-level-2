from NIR_1 import DiGraph


class Task:

    id = 0
    graph = None
    live_time = -1
    levels = None
    nodes = None
    process = None
    process_level = 0
    ready = False

    def __init__(self, graph: DiGraph):

        self.id = Task.id
        Task.id += 1

        self.graph = graph
        self.live_time = 0
        self.process = {}

        self.levels = {}
        for lid in range(1, graph.max_level + 1):

            nodes = {node: None for node in graph.nodes_level(lid)}
            self.levels[lid] = nodes

        self.nodes = []
        for i in range(1, graph.max_level + 1):
            self.nodes.extend(graph.nodes_level(i))

    def __repr__(self):

        return f'<Task[{self.id}] (' \
               f'processes: {len(self.process)}' \
               f')>'

    def do(self, processes):

        self.live_time += 1

        # remove finished calculations
        ps_to_remove = []
        for ps, nodes_to_delete in self.process.items():
            if ps.task != self:
                magic = [self.nodes.remove(node) for node in nodes_to_delete]
                ps_to_remove.append(ps)

        for ps in ps_to_remove:
            del self.process[ps]

        # check to need calculations
        if not (len(self.process) or len(self.nodes)):
            self.ready = True
            return

        for lid in self.levels.keys():

            nodes = self.levels[lid] if lid in self.levels.keys() else []
            for ps in processes:
                if not ps.buzy and ps.get_level(lid):

                    level = ps.get_level(lid)
                    level_nodes_names = [node['name'] for node in level.nodes]

                    # check can calculate any
                    if not any(node in level_nodes_names for node in nodes):
                        continue

                    # check all nodes is not calculationg now
                    if not all(self.levels[lid][node] is None for node in level_nodes_names):
                        continue

                    # check all nodes before that has been calculated
                    if not all(edge not in self.nodes for node in level.nodes for edge in node['edges']):
                        continue

                    ps.buzy = sum(node['weight'] for node in level.nodes)
                    ps.task = self
                    self.process[ps] = level_nodes_names
                    self.process_level = lid if self.process_level > lid else self.process_level

                    # set for node process
                    for node in level_nodes_names:
                        self.levels[lid][node] = ps