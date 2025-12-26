"""
Dynamic color evolution system using HSV color space.
Provides smooth color transitions over time while maintaining visibility on black background.
"""

import colorsys
import time
from typing import Tuple


class ColorEvolution:
    """
    Manages dynamic color evolution for game elements.
    All colors are tied to a master hue that rotates through the spectrum over time.
    """

    def __init__(self, cycle_duration: float = 60.0):
        """
        Initialize the color evolution system.

        Args:
            cycle_duration: Time in seconds for a full color cycle (default: 60s)
        """
        self.cycle_duration = cycle_duration
        self.start_time = time.time()

    def get_master_hue(self) -> float:
        """
        Calculate the current master hue based on elapsed time.
        Hue rotates through full spectrum (0.0 to 1.0) over cycle_duration.

        Returns:
            Hue value between 0.0 and 1.0
        """
        elapsed = time.time() - self.start_time
        # Normalize to 0.0-1.0 range, wrapping around
        return (elapsed / self.cycle_duration) % 1.0

    def get_snake_color(self) -> Tuple[int, int, int]:
        """
        Get the current color for snake segments.
        High saturation and value for maximum visibility.

        Returns:
            RGB color tuple (0-255 range)
        """
        hue = self.get_master_hue()
        saturation = 0.8  # High saturation for vibrant color
        value = 0.9  # High value for brightness

        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))

    def get_apple_color(self) -> Tuple[int, int, int]:
        """
        Get the current color for the apple.
        Offset 120 degrees (1/3) from snake for complementary color.

        Returns:
            RGB color tuple (0-255 range)
        """
        hue = (self.get_master_hue() + 0.333) % 1.0  # +120 degrees
        saturation = 0.9
        value = 0.95

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))

    def get_grid_color(self) -> Tuple[int, int, int]:
        """
        Get the current color for grid lines.
        Same hue as snake but low saturation and medium value for subtlety.

        Returns:
            RGB color tuple (0-255 range)
        """
        hue = self.get_master_hue()
        saturation = 0.3  # Low saturation for muted color
        value = 0.5  # Medium value

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))

    def get_ui_color(self) -> Tuple[int, int, int]:
        """
        Get the current color for UI text.
        High value, low saturation for readability.

        Returns:
            RGB color tuple (0-255 range)
        """
        hue = self.get_master_hue()
        saturation = 0.2
        value = 0.95

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))
