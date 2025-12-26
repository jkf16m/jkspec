# PY-SNAKE DESIGN DECISIONS

## 1. RENDERING DECISIONS

### Vanishing Point
- **Location**: Center of screen horizontally, 75% down vertically (creates slight upward viewing angle)
- **Rationale**: Creates depth without being too extreme, comfortable viewing angle

### Perspective Strength
- **Factor**: 300 (moderate perspective)
- **Rationale**: Strong enough to show depth, not so strong that distant objects disappear

### Cube Specifications
- **Size**: 20 units in 3D space
- **Origin**: Centered at (0, 0, 0) for each cube
- **Line Width**: 2 pixels
- **Antialiasing**: Enabled
- **Rationale**: Clear visibility while maintaining performance

### Apple (Low-Poly Sphere)
- **Polygon Count**: 12 faces (icosahedron-based)
- **Style**: Wireframe
- **Animation**: Gentle rotation on Y-axis (10 degrees per second)
- **Rationale**: Distinct from cubes, visually interesting without being distracting

## 2. COLOR SYSTEM DECISIONS

### Transition Method
- **Method**: HSV color space smooth transitions
- **Timing**: Time-based, independent of score
- **Duration**: Full color cycle every 60 seconds
- **Rationale**: Smooth, predictable evolution that enhances atmosphere

### Color Algorithm
- **Snake**: Hue rotates through spectrum, high saturation (0.8), high value (0.9)
- **Apple**: Offset 120 degrees from snake hue (complementary color)
- **Grid**: Same hue as snake but low saturation (0.3), medium value (0.5)
- **Rationale**: Unified color harmony while maintaining clear visual hierarchy

### Element Independence
- **Approach**: Unified color scheme (all elements tied to master hue)
- **Rationale**: Cohesive visual experience, easier to maintain visibility

## 3. GAME MECHANICS DECISIONS

### Movement System
- **Type**: Grid-based movement
- **Grid Size**: 20x15 cells
- **Cell Size**: 40 pixels
- **Screen Size**: 800x600 pixels
- **Rationale**: Classic snake feel, predictable collision detection

### Speed & Acceleration
- **Starting Speed**: 8 moves per second
- **Acceleration Trigger**: Every 5 apples collected
- **Acceleration Amount**: +1 move per second
- **Max Speed**: 20 moves per second
- **Rationale**: Gentle ramp-up that becomes challenging but not impossible

### Starting Conditions
- **Initial Length**: 3 segments
- **Starting Position**: Center of grid (10, 7)
- **Starting Direction**: Right
- **Rationale**: Standard setup, gives room to maneuver

### Apple Mechanics
- **Spawn Count**: 1 apple at a time
- **Spawn Rules**: Random empty cell
- **Respawn Timing**: Immediate upon collection
- **Rationale**: Classic snake rules, keeps gameplay focused

## 4. TECHNICAL DECISIONS

### Display
- **Resolution**: 800x600 pixels
- **Window Mode**: Windowed (not fullscreen)
- **Resizable**: No
- **Rationale**: Standard resolution, easy to debug and test

### Controls
- **Movement**: WASD and Arrow keys
- **Pause**: ESC or P
- **Restart**: SPACE (on game over)
- **Quit**: Q (at any time)
- **Rationale**: Standard gaming controls, multiple options for accessibility

### Persistence
- **File**: highscore.json in game directory
- **Structure**: {"high_score": <int>, "date": "<ISO date>"}
- **Rationale**: Simple, human-readable format

## 5. UI DECISIONS

### HUD Elements
- **Score**: Top-left (current score)
- **High Score**: Top-center
- **Speed**: Top-right (moves per second)
- **FPS**: Bottom-right (debug info)
- **Rationale**: Standard placement, non-intrusive

### Game States
- **MENU**: Title, instructions, press SPACE to start
- **PLAYING**: Active gameplay
- **PAUSED**: Dimmed background, "PAUSED" text, ESC to resume
- **GAME_OVER**: Score display, high score, press SPACE to restart
- **Rationale**: Clear state transitions, intuitive flow

### Grid Visualization
- **Coverage**: Full playable area
- **Visibility**: Always visible at low opacity
- **Cell Size**: Matches game grid (40 pixels)
- **Rationale**: Helps player judge distances and plan moves

## IMPLEMENTATION PRIORITY
1. Wireframe cube rendering (foundational)
2. Perspective transformation system
3. Basic snake mechanics
4. Color evolution system
5. Low-poly sphere apple
6. Grid rendering
7. UI and game states
8. Performance optimization
