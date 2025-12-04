class Map:
    def __init__(self, filepath):
        self.walls = set()
        self.no_spawn = set()
        self.start_pos = (0, 0)
        self.width = 0
        self.height = 0
        self.load_map(filepath)

    def load_map(self, filepath):
        try:
            with open(filepath, 'r') as f:
                lines = [line.rstrip('\n') for line in f]
            
            self.height = len(lines)
            self.width = max(len(line) for line in lines) if lines else 0

            for y, line in enumerate(lines):
                for x, char in enumerate(line):
                    if char == '#':
                        self.walls.add((x, y))
                    elif char == 'x':
                        self.no_spawn.add((x, y))
                    elif char == 'S':
                        self.start_pos = (x, y)
        except FileNotFoundError:
            print(f"Error: Map file '{filepath}' not found.")

    def is_wall(self, x, y):
        return (x, y) in self.walls
    
    def is_no_spawn(self, x, y):
        return (x, y) in self.no_spawn
