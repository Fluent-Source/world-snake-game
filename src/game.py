import pygame
import random
import sys
from src.map import Map
from src.snake import Snake
from src.utils import load_config

class Game:
    def __init__(self):
        self.config = load_config("config.yaml")
        if not self.config:
            sys.exit(1)
        
        pygame.init()
        pygame.font.init()
        self.width = self.config['window']['width']
        self.height = self.config['window']['height']
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.config['window']['title'])
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.game_over_font = pygame.font.SysFont("Arial", 48)
        
        self.cell_width = self.config['grid']['width']
        self.cell_height = self.config['grid']['height']
        
        self.map = Map("levels/default.map")
        self.reset_game()

    def reset_game(self):
        self.snake = Snake(self.map.start_pos)
        self.food = None
        self.spawn_food()
        self.score = 0
        self.running = True
        self.game_over = False

    def spawn_food(self):
        while True:
            x = random.randint(0, self.map.width - 1)
            y = random.randint(0, self.map.height - 1)
            if (not self.map.is_wall(x, y) and 
                not self.map.is_no_spawn(x, y) and 
                (x, y) not in self.snake.body):
                self.food = (x, y)
                break

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.running = False
                else:
                    if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                        self.snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                        self.snake.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                        self.snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                        self.snake.direction = (1, 0)

    def update(self):
        if self.game_over:
            return

        head_x, head_y = self.snake.get_head()
        dx, dy = self.snake.direction
        new_x, new_y = head_x + dx, head_y + dy
        
        # Wrapping logic
        if new_x < 0:
            new_x = self.map.width - 1
        if new_x >= self.map.width:
            new_x = 0
        if new_y < 0:
            new_y = self.map.height - 1
        if new_y >= self.map.height:
            new_y = 0
            
        # Wall skipping logic
        scan_count = 0
        max_scan = max(self.map.width, self.map.height)
        
        while (self.map.is_wall(new_x, new_y) or self.map.is_no_spawn(new_x, new_y)) and scan_count < max_scan:
            new_x += dx
            new_y += dy
            
            # Wrap again during skip
            if new_x < 0:
                new_x = self.map.width - 1
            if new_x >= self.map.width:
                new_x = 0
            if new_y < 0:
                new_y = self.map.height - 1
            if new_y >= self.map.height:
                new_y = 0
            
            scan_count += 1
            
        if self.map.is_wall(new_x, new_y) or self.map.is_no_spawn(new_x, new_y):
            # Trapped in walls
            self.game_over = True
            return
        
        new_head = (new_x, new_y)
        
        if self.snake.check_self_collision(new_head):
            self.game_over = True
            return

        self.snake.move(new_head)
        
        if new_head == self.food:
            self.snake.grow()
            self.score += 1
            self.spawn_food()

    def draw(self):
        self.screen.fill(self.config['colors']['background'])
        
        # Draw Walls
        for x, y in self.map.walls:
            rect = (x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height)
            pygame.draw.rect(self.screen, self.config['colors']['wall'], rect)
            
        # Draw Food
        if self.food:
            fx, fy = self.food
            rect = (fx * self.cell_width, fy * self.cell_height, self.cell_width, self.cell_height)
            pygame.draw.rect(self.screen, self.config['colors']['food'], rect)
        
        # Draw Snake
        for x, y in self.snake.body:
            rect = (x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height)
            pygame.draw.rect(self.screen, self.config['colors']['snake'], rect)
            
        # Draw Score
        score_text = self.font.render(f"Score: {self.score}", True, self.config['colors']['text'])
        self.screen.blit(score_text, (10, 10))
        
        # Draw Game Over
        if self.game_over:
            over_text = self.game_over_font.render("GAME OVER", True, self.config['colors']['text'])
            restart_text = self.font.render("Press R to Restart or Q to Quit", True, self.config['colors']['text'])
            
            over_rect = over_text.get_rect(center=(self.width/2, self.height/2 - 20))
            restart_rect = restart_text.get_rect(center=(self.width/2, self.height/2 + 30))
            
            self.screen.blit(over_text, over_rect)
            self.screen.blit(restart_text, restart_rect)
            
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.config['game']['speed'])
        
        pygame.quit()
        sys.exit()
