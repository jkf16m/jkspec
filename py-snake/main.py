"""
PY-SNAKE: Snake game with 3D wireframe cube rendering in 2D using one-point perspective.
Features dynamic color evolution, low-poly sphere apple, and optimized rendering.

Main game file containing game logic, state management, and rendering.
"""

import pygame
import sys
import json
import os
import random
import math
import time
from datetime import datetime
from typing import Tuple, List, Optional
from enum import Enum

from perspective import PerspectiveCamera
from wireframe_cube import WireframeCube
from color_system import ColorEvolution


# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_WIDTH = 20
GRID_HEIGHT = 15
CELL_SIZE = 40
FPS_TARGET = 60

# Cube rendering
CUBE_SIZE = 20.0
CUBE_LINE_WIDTH = 2

# Game mechanics
STARTING_SPEED = 8  # moves per second
SPEED_INCREMENT = 1
SPEED_TRIGGER = 5  # apples to trigger speed increase
MAX_SPEED = 20
STARTING_LENGTH = 3
STARTING_POS = (10, 7)

# File for high score persistence
HIGHSCORE_FILE = "highscore.json"


class GameState(Enum):
    """Game state enumeration."""

    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4


class Direction(Enum):
    """Direction enumeration for snake movement."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self):
        """Return the opposite direction."""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]


class LowPolySphere:
    """
    Low-poly sphere for apple rendering.
    Uses icosahedron-based geometry with wireframe rendering.
    """

    def __init__(self, position_3d: Tuple[float, float, float], size: float = 20.0):
        """
        Initialize a low-poly sphere.

        Args:
            position_3d: (x, y, z) center position
            size: Radius of the sphere
        """
        self.position = position_3d
        self.size = size
        self.rotation_angle = 0.0  # Rotation around Y-axis
        self.rotation_speed = 10.0  # Degrees per second

        # Generate icosahedron vertices (12 vertices)
        self.base_vertices = self._generate_icosahedron()
        self.vertices_3d = self._calculate_world_vertices()
        self.edges = self._generate_edges()

    def _generate_icosahedron(self) -> List[Tuple[float, float, float]]:
        """Generate unit icosahedron vertices."""
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio

        # Normalize to unit sphere
        vertices = [
            (-1, phi, 0),
            (1, phi, 0),
            (-1, -phi, 0),
            (1, -phi, 0),
            (0, -1, phi),
            (0, 1, phi),
            (0, -1, -phi),
            (0, 1, -phi),
            (phi, 0, -1),
            (phi, 0, 1),
            (-phi, 0, -1),
            (-phi, 0, 1),
        ]

        # Normalize to unit sphere
        normalized = []
        for x, y, z in vertices:
            length = math.sqrt(x * x + y * y + z * z)
            normalized.append((x / length, y / length, z / length))

        return normalized

    def _generate_edges(self) -> List[Tuple[int, int]]:
        """Generate edges for icosahedron wireframe."""
        # Icosahedron has 30 edges connecting 12 vertices
        edges = [
            (0, 11),
            (0, 5),
            (0, 1),
            (0, 7),
            (0, 10),
            (1, 5),
            (5, 9),
            (11, 5),
            (11, 4),
            (11, 10),
            (2, 3),
            (2, 4),
            (2, 6),
            (2, 10),
            (2, 11),
            (1, 7),
            (1, 9),
            (3, 9),
            (3, 4),
            (3, 6),
            (4, 9),
            (6, 7),
            (6, 8),
            (6, 10),
            (7, 8),
            (7, 10),
            (8, 9),
            (8, 3),
            (9, 5),
            (4, 5),
        ]
        return edges

    def _rotate_y(
        self, point: Tuple[float, float, float], angle_deg: float
    ) -> Tuple[float, float, float]:
        """Rotate a point around Y-axis."""
        x, y, z = point
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        new_x = x * cos_a + z * sin_a
        new_z = -x * sin_a + z * cos_a

        return (new_x, y, new_z)

    def _calculate_world_vertices(self) -> List[Tuple[float, float, float]]:
        """Calculate world-space positions of all vertices with rotation."""
        px, py, pz = self.position

        vertices = []
        for vx, vy, vz in self.base_vertices:
            # Apply rotation
            rx, ry, rz = self._rotate_y((vx, vy, vz), self.rotation_angle)

            # Scale and translate
            vertices.append(
                (px + rx * self.size, py + ry * self.size, pz + rz * self.size)
            )

        return vertices

    def update(self, dt: float):
        """Update sphere rotation."""
        self.rotation_angle = (self.rotation_angle + self.rotation_speed * dt) % 360
        self.vertices_3d = self._calculate_world_vertices()

    def render(
        self,
        surface: pygame.Surface,
        camera: PerspectiveCamera,
        color: Tuple[int, int, int],
        line_width: int = 2,
    ):
        """Render the sphere wireframe."""
        vertices_2d = camera.project_points(self.vertices_3d)

        for v1_idx, v2_idx in self.edges:
            p1 = vertices_2d[v1_idx]
            p2 = vertices_2d[v2_idx]

            if line_width == 1:
                pygame.draw.aaline(surface, color, p1, p2)
            else:
                pygame.draw.line(surface, color, p1, p2, line_width)

    def update_position(self, new_position: Tuple[float, float, float]):
        """Update sphere position."""
        self.position = new_position
        self.vertices_3d = self._calculate_world_vertices()


class Snake:
    """Snake game logic and rendering."""

    def __init__(self, camera: PerspectiveCamera):
        """Initialize snake."""
        self.camera = camera
        self.reset()

    def reset(self):
        """Reset snake to starting state."""
        # Snake body as grid positions
        start_x, start_y = STARTING_POS
        self.body = [(start_x - i, start_y) for i in range(STARTING_LENGTH)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow_pending = 0

        # Create wireframe cubes for each segment
        self.cubes = [self._create_cube_for_cell(pos) for pos in self.body]

    def _create_cube_for_cell(self, grid_pos: Tuple[int, int]) -> WireframeCube:
        """Create a wireframe cube for a grid cell."""
        x, y = grid_pos
        # Convert grid position to world 3D position
        world_x = x * CELL_SIZE + CELL_SIZE / 2
        world_y = y * CELL_SIZE + CELL_SIZE / 2
        world_z = 0  # Snake stays on z=0 plane

        return WireframeCube((world_x, world_y, world_z), CUBE_SIZE)

    def set_direction(self, new_direction: Direction):
        """Set next direction (prevents immediate reversal)."""
        if new_direction != self.direction.opposite():
            self.next_direction = new_direction

    def move(self):
        """Move snake forward one cell."""
        self.direction = self.next_direction

        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        # Update cubes
        self.cubes = [self._create_cube_for_cell(pos) for pos in self.body]

    def grow(self):
        """Mark snake to grow on next move."""
        self.grow_pending += 1

    def check_collision(self) -> bool:
        """Check if snake collided with itself or walls."""
        head = self.body[0]

        # Wall collision
        if (
            head[0] < 0
            or head[0] >= GRID_WIDTH
            or head[1] < 0
            or head[1] >= GRID_HEIGHT
        ):
            return True

        # Self collision
        if head in self.body[1:]:
            return True

        return False

    def render(self, surface: pygame.Surface, color: Tuple[int, int, int]):
        """Render all snake segments."""
        for cube in self.cubes:
            cube.render(surface, self.camera, color, CUBE_LINE_WIDTH)


class Game:
    """Main game class."""

    def __init__(self):
        """Initialize game."""
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PY-SNAKE")

        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        # Initialize systems
        self.camera = PerspectiveCamera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.color_system = ColorEvolution()
        self.snake = Snake(self.camera)

        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self.load_high_score()
        self.speed = STARTING_SPEED
        self.move_timer = 0

        # Apple
        self.apple_pos = None
        self.apple_sphere = None
        self.spawn_apple()

    def load_high_score(self) -> int:
        """Load high score from file."""
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        """Save high score to file."""
        data = {"high_score": self.high_score, "date": datetime.now().isoformat()}
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def spawn_apple(self):
        """Spawn apple at random empty cell."""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)

            if (x, y) not in self.snake.body:
                self.apple_pos = (x, y)

                # Create 3D sphere
                world_x = x * CELL_SIZE + CELL_SIZE / 2
                world_y = y * CELL_SIZE + CELL_SIZE / 2
                world_z = 0

                self.apple_sphere = LowPolySphere(
                    (world_x, world_y, world_z), CUBE_SIZE * 0.8
                )
                break

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # Quit
                if event.key == pygame.K_q:
                    return False

                # State-specific controls
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_game()

                elif self.state == GameState.PLAYING:
                    # Movement
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.set_direction(Direction.UP)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.set_direction(Direction.DOWN)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.set_direction(Direction.LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.set_direction(Direction.RIGHT)

                    # Pause
                    elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.state = GameState.PAUSED

                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.start_game()

        return True

    def start_game(self):
        """Start new game."""
        self.state = GameState.PLAYING
        self.score = 0
        self.speed = STARTING_SPEED
        self.move_timer = 0
        self.snake.reset()
        self.spawn_apple()

    def update(self, dt: float):
        """Update game logic."""
        if self.state != GameState.PLAYING:
            return

        # Update apple rotation
        if self.apple_sphere:
            self.apple_sphere.update(dt)

        # Update snake movement
        self.move_timer += dt
        move_interval = 1.0 / self.speed

        if self.move_timer >= move_interval:
            self.move_timer = 0

            self.snake.move()

            # Check collision
            if self.snake.check_collision():
                self.game_over()
                return

            # Check apple collection
            if self.snake.body[0] == self.apple_pos:
                self.snake.grow()
                self.score += 1

                # Update high score
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

                # Speed up every SPEED_TRIGGER apples
                if self.score % SPEED_TRIGGER == 0 and self.speed < MAX_SPEED:
                    self.speed += SPEED_INCREMENT

                self.spawn_apple()

    def game_over(self):
        """Handle game over."""
        self.state = GameState.GAME_OVER

    def render_grid(self):
        """Render dashed grid lines with 3D perspective projection."""
        color = self.color_system.get_grid_color()

        # Grid should be positioned deeper in z to show more perspective
        # The farther back (larger z), the more visible the perspective effect
        grid_z = 100.0

        # Generate 3D grid lines on the ground plane
        grid_lines_3d = []

        # Vertical lines (along Y-axis)
        for x in range(GRID_WIDTH + 1):
            world_x = x * CELL_SIZE
            start_3d = (world_x, 0, grid_z)
            end_3d = (world_x, GRID_HEIGHT * CELL_SIZE, grid_z)
            grid_lines_3d.append((start_3d, end_3d))

        # Horizontal lines (along X-axis)
        for y in range(GRID_HEIGHT + 1):
            world_y = y * CELL_SIZE
            start_3d = (0, world_y, grid_z)
            end_3d = (GRID_WIDTH * CELL_SIZE, world_y, grid_z)
            grid_lines_3d.append((start_3d, end_3d))

        # Project 3D lines to 2D and render with dashed pattern
        for start_3d, end_3d in grid_lines_3d:
            # Project endpoints through perspective camera
            start_2d = self.camera.project_3d_to_2d(*start_3d)
            end_2d = self.camera.project_3d_to_2d(*end_3d)

            # Draw dashed line between projected endpoints
            self._draw_dashed_line(start_2d, end_2d, color, dash_length=5, gap_length=5)

    def _draw_dashed_line(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: Tuple[int, int, int],
        dash_length: int = 5,
        gap_length: int = 5,
    ):
        """
        Draw a dashed line between two 2D points.

        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
            color: Line color RGB tuple
            dash_length: Length of each dash in pixels
            gap_length: Length of each gap in pixels
        """
        x1, y1 = start
        x2, y2 = end

        # Calculate line length and direction
        dx = x2 - x1
        dy = y2 - y1
        line_length = math.sqrt(dx * dx + dy * dy)

        if line_length == 0:
            return

        # Normalize direction
        dx /= line_length
        dy /= line_length

        # Draw dashes along the line
        pattern_length = dash_length + gap_length
        current_pos = 0

        while current_pos < line_length:
            # Start of dash
            dash_start_x = x1 + dx * current_pos
            dash_start_y = y1 + dy * current_pos

            # End of dash
            dash_end_pos = min(current_pos + dash_length, line_length)
            dash_end_x = x1 + dx * dash_end_pos
            dash_end_y = y1 + dy * dash_end_pos

            # Draw the dash
            pygame.draw.line(
                self.screen,
                color,
                (int(dash_start_x), int(dash_start_y)),
                (int(dash_end_x), int(dash_end_y)),
            )

            # Move to next dash (skip gap)
            current_pos += pattern_length

    def render_hud(self):
        """Render HUD elements."""
        color = self.color_system.get_ui_color()

        # Score (top-left)
        score_text = self.font_small.render(f"Score: {self.score}", True, color)
        self.screen.blit(score_text, (10, 10))

        # High score (top-center)
        hs_text = self.font_small.render(f"High Score: {self.high_score}", True, color)
        hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(hs_text, hs_rect)

        # Speed (top-right)
        speed_text = self.font_small.render(f"Speed: {self.speed}", True, color)
        speed_rect = speed_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        self.screen.blit(speed_text, speed_rect)

        # FPS (bottom-right)
        fps = int(self.clock.get_fps())
        fps_text = self.font_small.render(f"FPS: {fps}", True, color)
        fps_rect = fps_text.get_rect(
            bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)
        )
        self.screen.blit(fps_text, fps_rect)

    def render_menu(self):
        """Render main menu."""
        color = self.color_system.get_ui_color()

        title = self.font_large.render("PY-SNAKE", True, color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        instructions = [
            "WASD or Arrow Keys to move",
            "ESC or P to pause",
            "Q to quit",
            "",
            "Press SPACE to start",
        ]

        y = SCREEN_HEIGHT // 2
        for line in instructions:
            text = self.font_small.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 40

    def render_paused(self):
        """Render paused overlay."""
        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        color = self.color_system.get_ui_color()

        text = self.font_large.render("PAUSED", True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        hint = self.font_small.render("Press ESC to resume", True, color)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(hint, hint_rect)

    def render_game_over(self):
        """Render game over screen."""
        color = self.color_system.get_ui_color()

        title = self.font_large.render("GAME OVER", True, color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        score_text = self.font_medium.render(f"Score: {self.score}", True, color)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        if self.score == self.high_score:
            new_hs = self.font_small.render("NEW HIGH SCORE!", True, color)
            new_hs_rect = new_hs.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(new_hs, new_hs_rect)

        hint = self.font_small.render("Press SPACE to restart", True, color)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
        self.screen.blit(hint, hint_rect)

    def render(self):
        """Render current frame."""
        # Clear screen
        self.screen.fill((0, 0, 0))

        if self.state == GameState.MENU:
            self.render_menu()

        else:
            # Render grid
            self.render_grid()

            # Render apple
            if self.apple_sphere:
                apple_color = self.color_system.get_apple_color()
                self.apple_sphere.render(
                    self.screen, self.camera, apple_color, CUBE_LINE_WIDTH
                )

            # Render snake
            snake_color = self.color_system.get_snake_color()
            self.snake.render(self.screen, snake_color)

            # Render HUD
            self.render_hud()

            # Render state overlays
            if self.state == GameState.PAUSED:
                self.render_paused()
            elif self.state == GameState.GAME_OVER:
                self.render_game_over()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS_TARGET) / 1000.0  # Delta time in seconds

            running = self.handle_input()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
