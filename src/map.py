import csv
import os


class Map:
  def __init__(self, filepath):
    self.walls = set()
    self.no_spawn = set()
    self.start_pos = (0, 0)
    self.width = 0
    self.height = 0

    # New attributes for wall segment exceptions
    # The key is the direction vector (dx, dy), and the value is a set of
    # (x, y) coordinates marking the start of a segment to skip.
    self.skip_segments = {
      (1, 0): set(),  # right
      (0, 1): set(),  # down
      (1, 1): set(),  # down-right
      (1, -1): set(),  # up-right
    }

    self.load_map(filepath)

  def _load_exceptions(self, map_dir):
    """Loads wall segment exceptions from CSVs in the map directory."""
    # Maps filename to (dx, dy)
    csv_files = {
      "right.csv": (1, 0),
      "down.csv": (0, 1),
      "down-right.csv": (1, 1),
      "up-right.csv": (1, -1),
    }

    for filename, direction in csv_files.items():
      csv_path = os.path.join(map_dir, filename)
      try:
        with open(csv_path, "r", newline="") as csvfile:
          reader = csv.reader(csvfile)
          for row in reader:
            # Expecting x, y in the CSV row
            if len(row) == 2:
              try:
                x = int(row[0].strip())
                y = int(row[1].strip())
                self.skip_segments[direction].add((x, y))
              except ValueError:
                # Silently ignore rows with non-integer coordinates
                pass
      except FileNotFoundError:
        # Silently ignore missing CSV files
        pass

  def load_map(self, level):
    try:
      with open(os.path.join(level, "map.txt"), "r") as f:
        lines = [line.rstrip("\n") for line in f]

      self.height = len(lines)
      self.width = max(len(line) for line in lines) if lines else 0

      for y, line in enumerate(lines):
        for x, char in enumerate(line):
          if char == "#":
            self.walls.add((x, y))
          elif char == "x":
            self.no_spawn.add((x, y))
          elif char == "S":
            self.start_pos = (x, y)
    except FileNotFoundError:
      print(f"Error: Map level '{level}' not found.")
      return

    # Load wall segment exceptions if the map file was successfully loaded
    self._load_exceptions(level)

  def is_wall(self, x, y):
    return (x, y) in self.walls

  def is_no_spawn(self, x, y):
    return (x, y) in self.no_spawn

  def get_skip_segments(self):
    """Returns the dictionary of wall segments to skip."""
    return self.skip_segments
