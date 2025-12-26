# PY-SNAKE

A Python Snake game featuring 3D wireframe cube rendering in 2D using one-point perspective projection, dynamic color evolution, and a low-poly sphere apple.

## Features

- **3D Wireframe Cubes**: Snake segments rendered as 3D wireframe cubes with one-point perspective
- **Dynamic Colors**: Smooth color transitions through HSV color space over time
- **Low-Poly Sphere Apple**: Icosahedron-based wireframe sphere with gentle rotation
- **Performance Optimized**: Targets 60 FPS even with 100+ snake segments
- **Dashed Grid**: Visual grid with dashed lines to help plan moves
- **Progressive Difficulty**: Speed increases every 5 apples collected
- **High Score Persistence**: High scores saved to JSON file

## Screenshots

The game features a clean black background with vibrant, constantly evolving colors for maximum visibility. The one-point perspective creates depth as the snake moves around the grid.

## Installation

### Requirements

- Python 3.7+
- Pygame 2.5.0+

### Setup

1. Clone or download this directory

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

- **WASD** or **Arrow Keys**: Move snake
- **ESC** or **P**: Pause game
- **SPACE**: Start game / Restart after game over
- **Q**: Quit game

## Game Mechanics

- **Starting Length**: 3 segments
- **Starting Speed**: 8 moves per second
- **Speed Increase**: +1 move/sec every 5 apples (max 20)
- **Grid Size**: 20x15 cells
- **Collision**: Game over if snake hits walls or itself

## Technical Details

### Architecture

The game is built with a clean, modular architecture:

- `perspective.py` - One-point perspective camera system for 3D to 2D projection
- `wireframe_cube.py` - 3D wireframe cube rendering for snake segments
- `color_system.py` - HSV-based dynamic color evolution system
- `main.py` - Main game logic, state management, and rendering

### Rendering System

The rendering uses a one-point perspective projection where:
- Vanishing point: Center horizontally, 75% down vertically
- Perspective strength: 300 (moderate depth effect)
- All 3D objects share the same vanishing point for consistent depth

### Color Evolution

Colors evolve smoothly through the HSV spectrum:
- **Full cycle**: 60 seconds
- **Snake**: High saturation (0.8), high value (0.9)
- **Apple**: 120° offset from snake (complementary color)
- **Grid**: Low saturation (0.3), medium value (0.5)
- **UI**: Low saturation (0.2), high value (0.95)

### Performance

The game is optimized for smooth 60 FPS performance:
- Efficient 3D to 2D transformations
- Batch vertex projections
- Minimal redundant calculations
- Grid-based movement for predictable performance

## Design Decisions

See `DECISIONS.md` for detailed rationale behind all design choices including:
- Rendering specifications (vanishing point, perspective strength, cube size)
- Color system (transition method, algorithms, timing)
- Game mechanics (movement, speed, acceleration)
- Technical specifications (resolution, controls, persistence)
- UI/UX design (HUD layout, game states, grid visualization)

## High Score

High scores are automatically saved to `highscore.json` in the game directory. The file contains:
```json
{
  "high_score": 42,
  "date": "2025-12-25T18:30:00.000000"
}
```

## Development

### Project Structure

```
py-snake/
├── main.py              # Main game file
├── perspective.py       # 3D projection system
├── wireframe_cube.py    # Cube rendering
├── color_system.py      # Color evolution
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── DECISIONS.md        # Design decisions document
└── highscore.json      # High score storage (created on first run)
```

### Performance Metrics

Target: 60 FPS

Tested configurations:
- 3 segments: 60 FPS ✓
- 50 segments: 60 FPS ✓
- 100+ segments: 60 FPS ✓

## Credits

Created as part of the jkspec specification demonstration project.

## License

Free to use and modify.
