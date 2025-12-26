"""
3D wireframe cube rendering with one-point perspective.
This is the foundational component for rendering snake segments.
"""

import pygame
from typing import Tuple, List
from perspective import PerspectiveCamera


class WireframeCube:
    """
    Represents a 3D cube rendered as wireframe edges using one-point perspective.
    Used for snake segments in the py-snake game.
    """

    # Define cube vertices in local 3D space (relative to center)
    # Cube is centered at origin, extends from -1 to +1 in each dimension
    UNIT_CUBE_VERTICES = [
        (-1, -1, -1),  # 0: back-bottom-left
        (1, -1, -1),  # 1: back-bottom-right
        (1, 1, -1),  # 2: back-top-right
        (-1, 1, -1),  # 3: back-top-left
        (-1, -1, 1),  # 4: front-bottom-left
        (1, -1, 1),  # 5: front-bottom-right
        (1, 1, 1),  # 6: front-top-right
        (-1, 1, 1),  # 7: front-top-left
    ]

    # Define edges as pairs of vertex indices
    # 12 edges connect the 8 vertices
    EDGES = [
        # Back face
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        # Front face
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        # Connecting edges
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]

    def __init__(self, position_3d: Tuple[float, float, float], size: float = 20.0):
        """
        Initialize a wireframe cube.

        Args:
            position_3d: (x, y, z) position of cube center in world space
            size: Size of the cube in world units
        """
        self.position = position_3d
        self.size = size

        # Calculate actual vertex positions in world space
        self.vertices_3d = self._calculate_world_vertices()

    def _calculate_world_vertices(self) -> List[Tuple[float, float, float]]:
        """
        Calculate world-space positions of all cube vertices.

        Returns:
            List of (x, y, z) tuples for each vertex
        """
        px, py, pz = self.position
        half_size = self.size / 2

        return [
            (px + vx * half_size, py + vy * half_size, pz + vz * half_size)
            for vx, vy, vz in self.UNIT_CUBE_VERTICES
        ]

    def render(
        self,
        surface: pygame.Surface,
        camera: PerspectiveCamera,
        color: Tuple[int, int, int],
        line_width: int = 2,
    ):
        """
        Render the wireframe cube on the given surface.

        Args:
            surface: Pygame surface to draw on
            camera: PerspectiveCamera for 3D to 2D projection
            color: RGB color tuple for the cube edges
            line_width: Width of the edge lines in pixels
        """
        # Project all 3D vertices to 2D screen coordinates
        vertices_2d = camera.project_points(self.vertices_3d)

        # Draw all edges
        for v1_idx, v2_idx in self.EDGES:
            p1 = vertices_2d[v1_idx]
            p2 = vertices_2d[v2_idx]

            # Draw solid line (antialiased if line_width is 1)
            if line_width == 1:
                pygame.draw.aaline(surface, color, p1, p2)
            else:
                pygame.draw.line(surface, color, p1, p2, line_width)

    def update_position(self, new_position: Tuple[float, float, float]):
        """
        Update the cube's position in world space.

        Args:
            new_position: New (x, y, z) position for cube center
        """
        self.position = new_position
        self.vertices_3d = self._calculate_world_vertices()
