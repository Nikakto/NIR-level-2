class Level:

    id = 0
    coeff = 1
    nodes = None
    time = 0

    def __init__(self, nodes):

        if isinstance(nodes, dict):
            nodes = [dict(nodes)]

        self.id = nodes[0]['level'] if len(nodes) else None
        self.nodes = [dict(node) for node in nodes]  # we need create new instance of node dict for each level
        self.recalculate()

    def __repr__(self):
        level_id = self.id if self.id else 'Unknown'
        nodes_names = [node['name'] for node in self.nodes]
        contain_nodes = ', '.join(nodes_names)
        return f'(Level[{level_id}]: {contain_nodes})'

    def add_node(self, node):
        self.nodes += [dict(node)]  # we need create new instance of node dict for each level
        self.recalculate()

    def recalculate(self):
        self.time = sum(node['weight'] for node in self.nodes)

    def split(self):

        if len(self.nodes) == 1:

            levels = Level(self.nodes), Level(self.nodes)
            for level in levels:
                level.coeff *= 2

            return levels

        else:
            nodes = list(self.nodes)
            nodes.sort(key=lambda x: x['weight'])

            new_levels = [Level(nodes.pop()), Level(nodes.pop())]
            while len(nodes):
                new_levels.sort(key=lambda x: x.time)
                new_levels[0].add_node(nodes.pop())

            return new_levels
