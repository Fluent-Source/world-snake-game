import pygame
from src.snake import Snake
from src.map import Map
from src.renderer import Renderer


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
    def __init__(self, manager):
        super().__init__(manager)
        self.title_font = pygame.font.SysFont("Arial", 64)
        self.option_font = pygame.font.SysFont("Arial", 32)
        self.options = ["Start Game", "Quit"]
        self.selected_index = 0

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected_index == 0:
                        self.manager.change_state(PlayState(self.manager))
                    elif self.selected_index == 1:
                        self.manager.running = False

    def draw(self):
        self.screen.fill(self.config["colors"]["background"])

        title = self.title_font.render(
            self.config["window"]["title"], True, self.config["colors"]["text"]
        )
        title_rect = title.get_rect(
            center=(self.manager.width / 2, self.manager.height / 4)
        )
        self.screen.blit(title, title_rect)

        for i, option in enumerate(self.options):
            color = (
                self.config["colors"]["snake"]
                if i == self.selected_index
                else self.config["colors"]["text"]
            )
            text = self.option_font.render(option, True, color)
            rect = text.get_rect(
                center=(self.manager.width / 2, self.manager.height / 2 + i * 50)
            )
            self.screen.blit(text, rect)


class PlayState(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.cell_width = self.config["grid"]["width"]
        self.cell_height = self.config["grid"]["height"]
        self.map = Map("levels/mexico.map")
        self.snake = Snake(self.map.start_pos)
        self.food = None
        self.score = 0
        self.renderer = Renderer(
            self.screen,
            self.config,
            self.cell_width,
            self.cell_height,
            self.map.width,
            self.map.height,
        )
        self.spawn_food()

    def spawn_food(self):
        import random

        while True:
            x = random.randint(0, self.map.width - 1)
            y = random.randint(0, self.map.height - 1)
            if (
                not self.map.is_wall(x, y)
                and not self.map.is_no_spawn(x, y)
                and (x, y) not in self.snake.body
            ):
                self.food = (x, y)
                break

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                    self.snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                    self.snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                    self.snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                    self.snake.direction = (1, 0)
                elif event.key == pygame.K_ESCAPE:
                    self.manager.change_state(MenuState(self.manager))

    def update(self):
        head_x, head_y = self.snake.get_head()
        dx, dy = self.snake.direction
        new_x, new_y = head_x + dx, head_y + dy

        # Wrap at map boundaries
        if new_x < 0:
            new_x = self.map.width - 1
        elif new_x >= self.map.width:
            new_x = 0
        if new_y < 0:
            new_y = self.map.height - 1
        elif new_y >= self.map.height:
            new_y = 0

        # Wall skipping logic
        scan_count = 0
        max_scan = max(self.map.width, self.map.height)

        while (
            self.map.is_wall(new_x, new_y) or self.map.is_no_spawn(new_x, new_y)
        ) and scan_count < max_scan:
            new_x += dx
            new_y += dy

            # Wrap
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
            self.manager.change_state(GameOverState(self.manager, self.score))
            return

        self.snake.move((new_x, new_y))

        if (new_x, new_y) == self.food:
            self.snake.grow()
            self.score += 1
            self.spawn_food()

    def draw(self):
        self.screen.fill(self.config["colors"]["background"])

        # Draw grid
        self.renderer.draw_grid(self.map.width, self.map.height)

        # Draw walls
        self.renderer.draw_walls(self.map.walls)

        # Draw food
        if self.food:
            time_ms = pygame.time.get_ticks()
            self.renderer.draw_food(self.food, time_ms)

        # Draw snake
        self.renderer.draw_snake(self.snake)

        # Draw score
        # score_text = self.font.render(
        #     f"Score: {self.score}", True, self.config["colors"]["text"]
        # )
        # self.screen.blit(score_text, (10, 10))


class GameOverState(GameState):
    def __init__(self, manager, score):
        super().__init__(manager)
        self.score = score
        self.title_font = pygame.font.SysFont("Arial", 48)

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.manager.change_state(PlayState(self.manager))
                elif event.key == pygame.K_q:
                    self.manager.change_state(MenuState(self.manager))

    def draw(self):
        self.screen.fill(self.config["colors"]["background"])

        over_text = self.title_font.render(
            "GAME OVER", True, self.config["colors"]["text"]
        )
        score_text = self.font.render(
            f"Final Score: {self.score}", True, self.config["colors"]["text"]
        )
        restart_text = self.font.render(
            "Press R to Restart or Q for Menu", True, self.config["colors"]["text"]
        )

        over_rect = over_text.get_rect(
            center=(self.manager.width / 2, self.manager.height / 2 - 50)
        )
        score_rect = score_text.get_rect(
            center=(self.manager.width / 2, self.manager.height / 2)
        )
        restart_rect = restart_text.get_rect(
            center=(self.manager.width / 2, self.manager.height / 2 + 50)
        )

        self.screen.blit(over_text, over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
