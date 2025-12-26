"""
One-point perspective transformation system for converting 3D coordinates to 2D screen space.
This is the foundational rendering component for the py-snake game.
"""

import math
from typing import Tuple, Optional


class PerspectiveCamera:
    """
    Implements one-point perspective projection for 3D to 2D transformation.
    All 3D objects in the game share the same vanishing point for consistent depth perception.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        vanishing_point_x: Optional[float] = None,
        vanishing_point_y: Optional[float] = None,
        perspective_strength: float = 300.0,
    ):
        """
        Initialize the perspective camera.

        Args:
            screen_width: Width of the screen in pixels
            screen_height: Height of the screen in pixels
            vanishing_point_x: X coordinate of vanishing point (default: center)
            vanishing_point_y: Y coordinate of vanishing point (default: 75% down)
            perspective_strength: Controls how strong the perspective effect is (lower = stronger)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Default vanishing point: center horizontally, 75% down vertically
        self.vp_x = (
            vanishing_point_x if vanishing_point_x is not None else screen_width / 2
        )
        self.vp_y = (
            vanishing_point_y if vanishing_point_y is not None else screen_height * 0.75
        )

        self.perspective_strength = perspective_strength

    def project_3d_to_2d(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """
        Transform 3D coordinates to 2D screen coordinates using one-point perspective.

        The perspective formula:
        - Points farther away (larger z) appear closer to the vanishing point
        - The perspective_strength controls how quickly this convergence happens

        Args:
            x: 3D X coordinate
            y: 3D Y coordinate
            z: 3D Z coordinate (depth, larger = farther away)

        Returns:
            Tuple of (screen_x, screen_y) coordinates
        """
        # Calculate perspective factor (objects farther away get smaller/closer to VP)
        # Add 1 to avoid division by zero and ensure reasonable scaling
        perspective_factor = self.perspective_strength / (self.perspective_strength + z)

        # Apply perspective transformation
        # The formula pulls points toward the vanishing point based on depth
        screen_x = self.vp_x + (x - self.vp_x) * perspective_factor
        screen_y = self.vp_y + (y - self.vp_y) * perspective_factor

        return (screen_x, screen_y)

    def project_points(self, points_3d: list) -> list:
        """
        Transform multiple 3D points to 2D screen coordinates.

        Args:
            points_3d: List of (x, y, z) tuples

        Returns:
            List of (screen_x, screen_y) tuples
        """
        return [self.project_3d_to_2d(x, y, z) for x, y, z in points_3d]
