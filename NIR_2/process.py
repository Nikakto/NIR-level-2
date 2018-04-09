from NIR_2.level import Level


class Process:

    id = 0
    buzy = 0
    levels = []
    task = None
    time = 0
    time_real = 0

    def __init__(self, levels):

        if isinstance(levels, Level):
            levels = [levels]

        self.id = Process.id
        Process.id += 1

        self.levels = levels
        self.recalculate()

    def __str__(self):
        print_levels = ', '.join(repr(l) for l in self.levels)
        return f'<Process> (buzy: {self.buzy}; task: {self.task}; time: {self.time}({self.time_real}); <levels: {print_levels})'

    def add_level(self, level):
        if isinstance(level, Level):
            level = [level]
        self.levels += level
        self.recalculate()

    def get_level(self, level_id):
        for lvl in self.levels:
            if lvl.id == level_id:
                return lvl

        return None

    def recalculate(self):
        self.time = sum(level.time / level.coeff for level in self.levels)
        self.time_real = sum(level.time for level in self.levels)

    def split(self):

        if len(self.levels) == 1:
            level = self.levels.pop()
            levels = level.split()
            [Process(l) for l in levels]
            return [Process(l) for l in levels]

        else:
            levels = list(self.levels)
            levels.sort(key=lambda x: (x.time, -x.id))

            new_processes = [Process(levels.pop()), Process(levels.pop())]
            while len(levels):
                new_processes.sort(key=lambda x: x.time)
                new_processes[0].add_level(levels.pop())

            return new_processes

    def tick(self):
        self.buzy -= 1
        if self.buzy <= 0:
            self.buzy = 0
            self.task = None
        return self.buzy