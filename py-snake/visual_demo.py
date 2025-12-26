"""
Visual demonstration of py-snake rendering components.
Generates a static scene showing cubes and sphere.
"""

import pygame
import sys
from perspective import PerspectiveCamera
from wireframe_cube import WireframeCube
from color_system import ColorEvolution

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("PY-SNAKE Visual Demo")

camera = PerspectiveCamera(800, 600)
color_system = ColorEvolution()

# Create a snake-like arrangement of cubes
cubes = []
for i in range(10):
    x = 200 + i * 45
    y = 300
    z = 0
    cubes.append(WireframeCube((x, y, z), 20))

# Create apple sphere
from main import LowPolySphere
apple = LowPolySphere((600, 200, 0), 18)

# Render scene
screen.fill((0, 0, 0))

# Draw grid
grid_color = color_system.get_grid_color()
for x in range(0, 800, 40):
    for y in range(0, 600, 10):
        if (y // 10) % 2 == 0:
            pygame.draw.line(screen, grid_color, (x, y), (x, min(y + 5, 600)))

for y in range(0, 600, 40):
    for x in range(0, 800, 10):
        if (x // 10) % 2 == 0:
            pygame.draw.line(screen, grid_color, (x, y), (min(x + 5, 800), y))

# Draw cubes
snake_color = color_system.get_snake_color()
for cube in cubes:
    cube.render(screen, camera, snake_color, 2)

# Draw apple
apple_color = color_system.get_apple_color()
apple.render(screen, camera, apple_color, 2)

# Draw title
font = pygame.font.Font(None, 48)
title = font.render("PY-SNAKE - Visual Demo", True, color_system.get_ui_color())
screen.blit(title, (200, 50))

# Save screenshot
pygame.image.save(screen, "demo_screenshot.png")
print("✓ Screenshot saved to demo_screenshot.png")

# Display for a moment
pygame.display.flip()
pygame.time.wait(2000)

pygame.quit()
print("✓ Visual demo complete")
