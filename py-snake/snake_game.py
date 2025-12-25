import pygame
import random
import sys

# Constants based on spec
WINDOW_SIZE = 600
GRID_SIZE = 20
CELL_SIZE = 30
FPS = 10  # Game updates every 100ms

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)


class Snake:
    """Snake entity with movement, growth, collision detection, and rendering"""

    def __init__(self):
        """Initialize Snake class with body list, direction, and growth counter"""
        # Initial position at (10, 10) grid coordinates with length 3
        self.body = [(10, 10), (9, 10), (8, 10)]
        # Initial direction: (1, 0) moving right
        self.direction = (1, 0)
        # Pending growth counter
        self.pending_growth = 0
        # Color and size
        self.color = GREEN
        self.segment_size = CELL_SIZE

    def move(self):
        """Update snake position based on current direction and handle growth"""
        # Calculate new head position
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Add new head position
        self.body.insert(0, new_head)

        # Remove tail segment unless growing
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

    def change_direction(self, new_direction):
        """Set new direction if valid (not 180-degree turn)"""
        dx, dy = self.direction
        new_dx, new_dy = new_direction

        # Prevent 180-degree turns
        if (dx, dy) == (-new_dx, -new_dy):
            return

        self.direction = new_direction

    def check_self_collision(self):
        """Return true if head collides with body"""
        head = self.body[0]
        return head in self.body[1:]

    def check_wall_collision(self):
        """Return true if head is out of bounds (0-19)"""
        head_x, head_y = self.body[0]
        return head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE

    def check_apple_collision(self, apple_position):
        """Check if head position matches apple position"""
        return self.body[0] == apple_position

    def grow(self):
        """Increment pending_growth counter"""
        self.pending_growth += 1

    def render(self, surface):
        """Draw all segments as rectangles on pygame surface"""
        for segment in self.body:
            x, y = segment
            rect = pygame.Rect(
                x * CELL_SIZE, y * CELL_SIZE, self.segment_size, self.segment_size
            )
            pygame.draw.rect(surface, self.color, rect)


class Apple:
    """Apple/food entity with random spawning"""

    def __init__(self, snake_body):
        """Initialize apple with random position not on snake body"""
        self.color = RED
        self.size = CELL_SIZE
        self.position = self.spawn(snake_body)

    def spawn(self, snake_body):
        """Generate random position within grid bounds, ensure not on snake body"""
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            position = (x, y)
            if position not in snake_body:
                return position

    def respawn(self, snake_body):
        """Respawn apple at new random position"""
        self.position = self.spawn(snake_body)

    def render(self, surface):
        """Draw apple as rectangle on pygame surface"""
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)


class GameManager:
    """Main game loop, state management, and rendering coordination"""

    def __init__(self):
        """Initialize pygame and game window"""
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Initialize game state
        self.snake = Snake()
        self.apple = Apple(self.snake.body)
        self.score = 0
        self.game_over = False

    def handle_input(self):
        """Process keyboard input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    # Restart game on any key press after game over
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                else:
                    # Arrow key controls
                    if event.key == pygame.K_UP:
                        self.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction((1, 0))

        return True

    def update(self):
        """Coordinate snake and apple updates"""
        if self.game_over:
            return

        # Move snake
        self.snake.move()

        # Check collisions
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self.game_over = True
            return

        # Check apple collision
        if self.snake.check_apple_collision(self.apple.position):
            self.score += 1
            self.snake.grow()
            self.apple.respawn(self.snake.body)

    def render(self):
        """Render all game elements"""
        # Clear screen with black background
        self.window.fill(BLACK)

        # Render snake and apple
        self.snake.render(self.window)
        self.apple.render(self.window)

        # Render score display
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.window.blit(score_text, (10, 10))

        # Render game over screen if needed
        if self.game_over:
            self.render_game_over()

        # Update display
        pygame.display.flip()

    def render_game_over(self):
        """Display game over message with final score and restart option"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.window.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press SPACE to restart", True, WHITE)

        # Center text on screen
        game_over_rect = game_over_text.get_rect(
            center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 50)
        )
        score_rect = final_score_text.get_rect(
            center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2)
        )
        restart_rect = restart_text.get_rect(
            center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 50)
        )

        self.window.blit(game_over_text, game_over_rect)
        self.window.blit(final_score_text, score_rect)
        self.window.blit(restart_text, restart_rect)

    def restart_game(self):
        """Reset game state for new game"""
        self.snake = Snake()
        self.apple = Apple(self.snake.body)
        self.score = 0
        self.game_over = False

    def run(self):
        """Handle main game loop and timing"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game"""
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()
