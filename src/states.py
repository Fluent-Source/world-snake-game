import os

import pygame

from src.map import Map
from src.map_watcher import MapWatcher
from src.renderer import Renderer
from src.snake import Snake
from src.utils import Config


class GameState:
  def __init__(self, manager):
    self.manager = manager
    self.config = manager.config
    self.screen = manager.screen
    self.font = manager.font

  def handle_input(self, events):
    pass

  def update(self):
    pass

  def draw(self):
    pass


class MenuState(GameState):
  def __init__(self, manager, config: Config):
    super().__init__(manager)
    self.title_font = pygame.font.SysFont("Arial", 64)
    self.option_font = pygame.font.SysFont("Arial", 32)
    self.options = ["Start Game", "Quit"]
    self.selected_index = 0
    self.config = config

  def handle_input(self, events):
    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP or event.key == pygame.K_w:
          self.selected_index = (self.selected_index - 1) % len(self.options)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
          self.selected_index = (self.selected_index + 1) % len(self.options)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
          if self.selected_index == 0:
            self.manager.change_state(PlayState(self.manager, self.config))
          elif self.selected_index == 1:
            self.manager.running = False

  def draw(self):
    self.screen.fill(self.config.colors.background)

    title = self.title_font.render(self.config.window.title, True, self.config.colors.text)
    title_rect = title.get_rect(center=(self.manager.width / 2, self.manager.height / 4))
    self.screen.blit(title, title_rect)

    for i, option in enumerate(self.options):
      color = self.config.colors.select if i == self.selected_index else self.config.colors.text
      text = self.option_font.render(option, True, color)
      rect = text.get_rect(center=(self.manager.width / 2, self.manager.height / 2 + i * 50))
      self.screen.blit(text, rect)


class PlayState(GameState):
  def __init__(self, manager, config: Config):
    super().__init__(manager)
    self.config = config
    self.cell_width = self.config.grid.width
    self.cell_height = self.config.grid.height
    self.level_dir = os.path.join(self.config.path.dir, self.config.path.level)

    self.map = Map(self.level_dir)
    self.snake = Snake(self.map.start_pos, self.config.game.width)
    self.food = None
    self.score = 0
    self.renderer = Renderer(
      self.screen,
      self.config,
      self.cell_width,
      self.cell_height,
      self.map.width,
      self.map.height,
      self.map.get_skip_segments(),
    )
    self.spawn_food()
    self.direction_queue = []

    self.background_image = None
    self._reload_needed = False

    def _request_reload(_):
      """Callback from the background MapWatcher thread (any file changed)."""
      self._reload_needed = True

    self._watcher = MapWatcher(self.level_dir, _request_reload)

    background_path = os.path.join(self.level_dir, "background.png")

    if os.path.exists(background_path):
      try:
        image = pygame.image.load(background_path).convert()
        self.background_image = pygame.transform.scale(image, (self.manager.width, self.manager.height))
      except pygame.error as e:
        print(f"Error loading background image: {e}")

  def on_exit(self):
    """Called by Game when this state is replaced – stop background watcher."""
    if hasattr(self, "_watcher"):
      self._watcher.stop()

  def spawn_food(self):
    import random

    while True:
      x = random.randint(0, self.map.width - 1)
      y = random.randint(0, self.map.height - 1)
      if not self.map.is_wall(x, y) and not self.map.is_no_spawn(x, y) and (x, y) not in self.snake.body:
        self.food = (x, y)
        break

  def handle_input(self, events):
    for event in events:
      if event.type == pygame.KEYDOWN:
        new_direction = None

        if event.key == pygame.K_UP or event.key == pygame.K_w:
          new_direction = (0, -1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
          new_direction = (0, 1)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
          new_direction = (-1, 0)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
          new_direction = (1, 0)
        elif event.key == pygame.K_ESCAPE:
          self.manager.change_state(MenuState(self.manager, self.config))
          return

        if new_direction:
          check_direction = self.direction_queue[-1] if self.direction_queue else self.snake.direction

          is_horizontal_reverse = (new_direction[0] + check_direction[0] == 0) and (new_direction[0] != 0)
          is_vertical_reverse = (new_direction[1] + check_direction[1] == 0) and (new_direction[1] != 0)

          if not (is_horizontal_reverse or is_vertical_reverse) and len(self.direction_queue) < 2:
            self.direction_queue.append(new_direction)

  def _reload_level(self):
    """Reloads *map.txt* and (optionally) the background image."""
    self.map = Map(self.level_dir)
    if self.map.is_wall(*self.snake.get_head()) or self.map.is_no_spawn(*self.snake.get_head()):
      self.manager.change_state(PlayState(self.manager, self.config))
      return

    self.renderer = Renderer(
      self.screen,
      self.config,
      self.cell_width,
      self.cell_height,
      self.map.width,
      self.map.height,
      self.map.get_skip_segments(),
    )

    bg_path = os.path.join(self.level_dir, "background.png")
    if os.path.exists(bg_path):
      try:
        image = pygame.image.load(bg_path).convert()
        self.background_image = pygame.transform.scale(image, (self.manager.width, self.manager.height))
      except pygame.error as e:
        print(f"Error re-loading background image: {e}")

  def update(self):
    if self._reload_needed:
      self._reload_needed = False
      self._reload_level()

    if self.direction_queue:
      self.snake.direction = self.direction_queue.pop(0)

    head_x, head_y = self.snake.get_head()
    dx, dy = self.snake.direction
    new_x, new_y = head_x + dx, head_y + dy

    if new_x < 0:
      new_x = self.map.width - 1
    elif new_x >= self.map.width:
      new_x = 0
    if new_y < 0:
      new_y = self.map.height - 1
    elif new_y >= self.map.height:
      new_y = 0

    scan_count = 0
    max_scan = max(self.map.width, self.map.height)

    while (self.map.is_wall(new_x, new_y) or self.map.is_no_spawn(new_x, new_y)) and scan_count < max_scan:
      new_x += dx
      new_y += dy

      if new_x < 0:
        new_x = self.map.width - 1
      if new_x >= self.map.width:
        new_x = 0
      if new_y < 0:
        new_y = self.map.height - 1
      if new_y >= self.map.height:
        new_y = 0

      scan_count += 1

    if (
      self.map.is_wall(new_x, new_y)
      or self.map.is_no_spawn(new_x, new_y)
      or self.snake.check_self_collision((new_x, new_y))
    ):
      self.manager.change_state(
        FrozenGameOverState(self.manager, self.renderer, self.map, self.snake, self.food, self.score)
      )
      return

    self.snake.move((new_x, new_y))

    if (new_x, new_y) == self.food:
      self.snake.grow()
      self.score += 1
      self.spawn_food()

  def draw(self):
    # Draw background
    if self.background_image:
      self.screen.blit(self.background_image, (0, 0))
    else:
      # Fallback to single color if image is not found or failed to load
      self.screen.fill(self.config.colors.background)

    # Draw grid
    if self.config.grid.draw:
      self.renderer.draw_grid(self.map.width, self.map.height)

    # Draw walls
    self.renderer.draw_walls(self.map.walls)

    # Draw food
    if self.food:
      time_ms = pygame.time.get_ticks()
      self.renderer.draw_food(self.food, time_ms)

    # Draw snake
    self.renderer.draw_snake(self.snake)


class FrozenGameOverState(GameState):
  def __init__(self, manager, renderer, map_obj, snake, food, score):
    super().__init__(manager)
    self.renderer = renderer
    self.map = map_obj
    self.snake = snake
    self.food = food
    self.score = score
    self.title_font = pygame.font.SysFont("Arial", 48)
    self.sub_font = pygame.font.SysFont("Arial", 32)
    self.last_update_time = pygame.time.get_ticks()

  def handle_input(self, events):
    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          self.manager.change_state(PlayState(self.manager, self.config))
        elif event.key == pygame.K_q:
          self.manager.change_state(MenuState(self.manager, self.config))

  def update(self):
    # Do nothing, game is frozen.
    pass

  def draw(self):
    # Draw the captured game state
    self.screen.fill(self.config.colors.background)

    # Draw grid
    self.renderer.draw_grid(self.map.width, self.map.height)

    # Draw walls
    self.renderer.draw_walls(self.map.walls)

    # Draw food
    if self.food:
      # Keep the frame of the food at the moment of death
      # To prevent animated food from moving, we pass the stored death time
      self.renderer.draw_food(self.food, self.last_update_time)

    # Draw snake
    self.renderer.draw_snake(self.snake)
