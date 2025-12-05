import sys

import pygame

from src.states import MenuState
from src.utils import load_config


class Game:
  def __init__(self):
    self.config = load_config("config.yaml")
    if not self.config:
      sys.exit(1)

    pygame.init()
    pygame.font.init()
    self.width = self.config["window"]["width"]
    self.height = self.config["window"]["height"]
    self.screen = pygame.display.set_mode((self.width, self.height))
    pygame.display.set_caption(self.config["window"]["title"])
    self.clock = pygame.time.Clock()
    self.font = pygame.font.SysFont("Arial", 24)

    self.running = True
    self.state = MenuState(self)

  def change_state(self, new_state):
    self.state = new_state

  def run(self):
    while self.running:
      events = pygame.event.get()
      for event in events:
        if event.type == pygame.QUIT:
          self.running = False

      self.state.handle_input(events)
      self.state.update()
      self.state.draw()

      pygame.display.flip()
      self.clock.tick(self.config["game"]["speed"])

    pygame.quit()
    sys.exit()

    pygame.quit()
    sys.exit()
