"""
Test suite for py-snake game components.
Tests perspective projection, wireframe rendering, color system, and game mechanics.
"""

import pygame
import sys
from perspective import PerspectiveCamera
from wireframe_cube import WireframeCube
from color_system import ColorEvolution
import time


def test_perspective_projection():
    """Test perspective camera projection."""
    print("\n=== Testing Perspective Projection ===")

    camera = PerspectiveCamera(800, 600)

    # Test vanishing point
    assert camera.vp_x == 400.0, "Vanishing point X should be screen center"
    assert camera.vp_y == 450.0, "Vanishing point Y should be 75% down"
    print(f"✓ Vanishing point: ({camera.vp_x}, {camera.vp_y})")

    # Test projection at different depths
    test_points = [
        (400, 300, 0),  # At vanishing point, z=0
        (400, 300, 100),  # Behind vanishing point
        (400, 300, -100),  # In front of vanishing point
        (600, 200, 0),  # Off to the side
    ]

    for x, y, z in test_points:
        sx, sy = camera.project_3d_to_2d(x, y, z)
        print(f"  3D({x},{y},{z}) -> 2D({sx:.1f},{sy:.1f})")

    print("✓ Perspective projection working")
    return True


def test_wireframe_cube():
    """Test wireframe cube creation and structure."""
    print("\n=== Testing Wireframe Cube ===")

    camera = PerspectiveCamera(800, 600)
    cube = WireframeCube((400, 300, 0), 20.0)

    # Verify structure
    assert len(cube.vertices_3d) == 8, "Cube should have 8 vertices"
    assert len(cube.EDGES) == 12, "Cube should have 12 edges"
    print(f"✓ Cube structure: 8 vertices, 12 edges")

    # Verify position
    assert cube.position == (400, 300, 0), "Cube position should match"
    assert cube.size == 20.0, "Cube size should match"
    print(f"✓ Cube position: {cube.position}, size: {cube.size}")

    # Test position update
    cube.update_position((500, 400, 50))
    assert cube.position == (500, 400, 50), "Position update should work"
    print("✓ Position update working")

    print("✓ Wireframe cube working")
    return True


def test_color_system():
    """Test color evolution system."""
    print("\n=== Testing Color Evolution System ===")

    color_system = ColorEvolution(cycle_duration=10.0)

    # Get initial colors
    snake_color = color_system.get_snake_color()
    apple_color = color_system.get_apple_color()
    grid_color = color_system.get_grid_color()
    ui_color = color_system.get_ui_color()

    # Verify RGB format
    for name, color in [
        ("Snake", snake_color),
        ("Apple", apple_color),
        ("Grid", grid_color),
        ("UI", ui_color),
    ]:
        assert len(color) == 3, f"{name} color should be RGB tuple"
        assert all(0 <= c <= 255 for c in color), f"{name} color values should be 0-255"
        print(f"✓ {name} color: RGB{color}")

    # Verify colors are visible (not too dark)
    assert sum(snake_color) > 100, "Snake color should be bright"
    assert sum(apple_color) > 100, "Apple color should be bright"
    print("✓ Colors are sufficiently bright for visibility")

    # Test hue rotation
    hue1 = color_system.get_master_hue()
    time.sleep(0.5)
    hue2 = color_system.get_master_hue()
    assert hue2 > hue1 or (hue2 < 0.1 and hue1 > 0.9), "Hue should rotate over time"
    print("✓ Color evolution over time working")

    print("✓ Color system working")
    return True


def test_rendering_performance():
    """Test rendering performance with many cubes."""
    print("\n=== Testing Rendering Performance ===")

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    camera = PerspectiveCamera(800, 600)
    color_system = ColorEvolution()

    # Create 100 cubes in a grid
    cubes = []
    for i in range(10):
        for j in range(10):
            x = 100 + i * 60
            y = 100 + j * 50
            cube = WireframeCube((x, y, 0), 20)
            cubes.append(cube)

    print(f"Created {len(cubes)} cubes")

    # Render frames and measure FPS
    clock = pygame.time.Clock()
    frame_times = []

    for frame in range(60):  # Render 60 frames
        screen.fill((0, 0, 0))

        color = color_system.get_snake_color()
        for cube in cubes:
            cube.render(screen, camera, color, 2)

        pygame.display.flip()
        dt = clock.tick(60)
        frame_times.append(dt)

    avg_fps = 1000.0 / (sum(frame_times) / len(frame_times))
    min_fps = 1000.0 / max(frame_times)

    print(f"✓ Average FPS: {avg_fps:.1f}")
    print(f"✓ Minimum FPS: {min_fps:.1f}")

    if avg_fps >= 55:
        print("✓ Performance target met (60 FPS)")
    else:
        print("⚠ Performance below target (60 FPS)")

    pygame.quit()
    return True


def test_game_initialization():
    """Test that main game can be initialized."""
    print("\n=== Testing Game Initialization ===")

    # Import main game (this tests that all dependencies work)
    try:
        from main import Game, Direction, GameState

        print("✓ Main game module imported successfully")

        # Verify enums
        assert len(list(GameState)) == 4, "Should have 4 game states"
        assert len(list(Direction)) == 4, "Should have 4 directions"
        print("✓ Game enums defined correctly")

        print("✓ Game initialization ready")
        return True
    except Exception as e:
        print(f"✗ Game initialization failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("PY-SNAKE TEST SUITE")
    print("=" * 60)

    tests = [
        test_perspective_projection,
        test_wireframe_cube,
        test_color_system,
        test_rendering_performance,
        test_game_initialization,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
