# Python Snake Game

A classic Snake game implementation using Python and Pygame.

## Features

- Snake grows when eating apples
- Game over on wall or self collision
- Score tracking based on apples eaten
- Visual game with smooth rendering
- Arrow key controls
- Game over screen with restart option

## Requirements

- Python 3.8 or higher
- Pygame library

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python snake_game.py
```

2. Controls:
   - **Arrow Up**: Move up
   - **Arrow Down**: Move down
   - **Arrow Left**: Move left
   - **Arrow Right**: Move right
   - **Space**: Restart game (after game over)

3. Gameplay Rules:
   - Start with a snake of length 3
   - Eat red apples to grow and increase your score
   - Each apple eaten gives you 1 point
   - Avoid hitting the walls
   - Avoid hitting your own body
   - The game ends when you collide with a wall or yourself

## Game Details

- **Window Size**: 600x600 pixels
- **Grid Size**: 20x20 cells
- **Cell Size**: 30 pixels
- **Colors**:
  - Background: Black
  - Snake: Green
  - Apple: Red
  - Text: White

## Implementation Details

The game consists of three main components:

1. **Snake**: Handles movement, growth, collision detection, and rendering
2. **Apple**: Manages random spawning of food items
3. **GameManager**: Coordinates the game loop, input handling, and rendering

Enjoy playing!
