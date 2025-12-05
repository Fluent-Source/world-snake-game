import math

import pygame


class Renderer:
  """Modern renderer with visual enhancements."""

  def __init__(self, screen, config, cell_width, cell_height, map_width, map_height, skip_segments):
    self.screen = screen
    self.config = config
    self.cell_width = cell_width
    self.cell_height = cell_height
    self.map_width = map_width
    self.map_height = map_height
    self.skip_segments = skip_segments  # Store the skip segments

    # Helper to load and scale an asset
    def _load_asset(filename, scale_factor=1.0, is_apple=False):
      if is_apple:
        original_image = pygame.image.load(f"assets/{filename}").convert_alpha()
      else:
        original_image = pygame.image.load(f"assets/{config['colors']['snake']}/{filename}").convert_alpha()
      scale = min(self.cell_width, self.cell_height) / original_image.get_width()
      return pygame.transform.rotozoom(original_image, 0, scale * scale_factor)

    # Load Food Image
    self.apple_image = _load_asset("apple.png", 0.9, True)

    # Load Snake Head
    self.head_assets = {
      (-1, 0): _load_asset("head_left.png"),  # Left
      (1, 0): _load_asset("head_right.png"),  # Right
      (0, -1): _load_asset("head_up.png"),  # Up
      (0, 1): _load_asset("head_down.png"),  # Down
    }

    # Load Snake Tail
    self.tail_assets = {
      (1, 0): _load_asset("tail_left.png"),  # Tail goes left (snake body is to the right)
      (-1, 0): _load_asset("tail_right.png"),  # Tail goes right (snake body is to the left)
      (0, 1): _load_asset("tail_up.png"),  # Tail goes up (snake body is down)
      (0, -1): _load_asset("tail_down.png"),  # Tail goes down (snake body is up)
    }

    # Load Straight Body Parts
    self.body_straights = {
      (-1, 0): _load_asset("body_horizontal.png"),
      (1, 0): _load_asset("body_horizontal.png"),
      (0, -1): _load_asset("body_vertical.png"),
      (0, 1): _load_asset("body_vertical.png"),
    }

    # Load Turning Body Parts (Key is (v_in, v_out) where v_in is vector into cell, v_out is vector out of cell)
    self.body_turns = {
      # body_topleft.png (L-shape from top-left)
      ((0, 1), (-1, 0)): _load_asset("body_topleft.png"),  # In from Down, Out to Left
      ((1, 0), (0, -1)): _load_asset("body_topleft.png"),  # In from Right, Out to Up
      # body_topright.png (L-shape from top-right)
      ((0, 1), (1, 0)): _load_asset("body_topright.png"),  # In from Down, Out to Right
      ((-1, 0), (0, -1)): _load_asset("body_topright.png"),  # In from Left, Out to Up
      # body_bottomleft.png (L-shape from bottom-left)
      ((0, -1), (-1, 0)): _load_asset("body_bottomleft.png"),  # In from Up, Out to Left
      ((1, 0), (0, 1)): _load_asset("body_bottomleft.png"),  # In from Right, Out to Down
      # body_bottomright.png (L-shape from bottom-right)
      ((0, -1), (1, 0)): _load_asset("body_bottomright.png"),  # In from Up, Out to Right
      ((-1, 0), (0, 1)): _load_asset("body_bottomright.png"),  # In from Left, Out to Down
    }

  def draw_snake(self, snake):
    """Draw snake using asset images."""

    # We need at least the head to draw anything
    if not snake.body:
      return

    for i, (x, y) in enumerate(snake.body):
      image = None

      if i == 0:
        # Head
        image = self.head_assets.get(snake.direction)

      elif i == len(snake.body) - 1:
        # Tail
        # Re-compute the current tail orientation from the position of the
        # segment immediately in front of it so that the sprite changes
        # the very frame the tail goes around a corner.
        v_next = snake.directions[i - 1]
        image = self.tail_assets.get(v_next)

      else:
        # Body segment
        # Retrieve the entry & exit vectors that were stored while the
        # snake was moving. Because ``directions`` mirrors ``body`` we
        # have:
        #   directions[i]   – vector that this segment followed when it moved
        #   directions[i-1] – vector that the next segment (towards the head)
        #                      followed – i.e. the *out* vector.
        v_prev = snake.directions[i]  # vector into this segment
        v_next = snake.directions[i - 1]  # vector out of this segment

        if v_prev == v_next:
          # Straight segment
          image = self.body_straights.get(v_prev)
        else:
          # Corner segment (v_prev is the 'in' direction, v_next is the 'out' direction)
          image = self.body_turns.get((v_prev, v_next))

      if image:
        rect = image.get_rect(topleft=(x * self.cell_width, y * self.cell_height))
        self.screen.blit(image, rect)

  def draw_food(self, food_pos, time_ms):
    """Draw food as an image with a bobbing animation."""
    fx, fy = food_pos

    # Calculate center position
    center_x = fx * self.cell_width + self.cell_width // 2
    center_y = fy * self.cell_height + self.cell_height // 2

    # Bobbing animation calculation
    time_s = time_ms / 1000.0
    amplitude = self.cell_height / 6  # 1/6th of cell height bob
    frequency = 2.0 * math.pi * 0.5  # 0.5 cycles per second

    bob_offset = amplitude * math.sin(frequency * time_s)

    # Draw the apple image centered with the bobbing offset
    image_rect = self.apple_image.get_rect(center=(center_x, center_y + bob_offset))
    self.screen.blit(self.apple_image, image_rect)

  def draw_walls(self, walls):
    """Draw walls as thin segments connecting neighbouring wall cells (8-neighbourhood)."""
    if not walls:
      return

    wall_color = (
      self._hex_to_rgb(self.config["colors"]["wall"])
      if isinstance(self.config["colors"]["wall"], str)
      else self.config["colors"]["wall"]
    )

    # Helper to calculate the pixel centre of a given grid coordinate
    def centre(cx: int, cy: int):
      return (
        cx * self.cell_width + self.cell_width // 2,
        cy * self.cell_height + self.cell_height // 2,
      )

    # Thickness of the wall segment in pixels – tweak as desired (20% of a cell)
    thickness = max(1, int(min(self.cell_width, self.cell_height) * self.config["wall"]))

    walls_set = set(walls)
    drawn_segments = set()  # keep track of already drawn centre pairs to avoid duplicates

    # Directions that ensure each connection is considered exactly once (dx>0 or (dx==0 and dy>0))
    dirs = [
      (1, 0),  # right
      (0, 1),  # down
      (1, 1),  # down-right
      (1, -1),  # up-right
    ]

    for x, y in walls_set:
      cx, cy = centre(x, y)
      for dx, dy in dirs:
        # Check if this segment (from (x, y) in direction (dx, dy)) should be skipped.
        if (x, y) in self.skip_segments.get((dx, dy), set()):
          continue

        nx, ny = x + dx, y + dy
        if (nx, ny) in walls_set:
          c2x, c2y = centre(nx, ny)
          key = (min((x, y), (nx, ny)), max((x, y), (nx, ny)))
          if key in drawn_segments:
            continue
          pygame.draw.line(
            self.screen,
            wall_color,
            (cx, cy),
            (c2x, c2y),
            thickness,
          )
          drawn_segments.add(key)

  def draw_grid(self, map_width, map_height):
    """Draw a subtle background grid."""
    grid_color = tuple(min(255, c + 10) for c in self._hex_to_rgb(self.config["colors"]["grid"]))

    for x in range(map_width + 1):
      pygame.draw.line(
        self.screen,
        grid_color,
        (x * self.cell_width, 0),
        (x * self.cell_width, map_height * self.cell_height),
      )

    for y in range(map_height + 1):
      pygame.draw.line(
        self.screen,
        grid_color,
        (0, y * self.cell_height),
        (map_width * self.cell_width, y * self.cell_height),
      )

  def _hex_to_rgb(self, hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
