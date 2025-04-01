import math
from . import settings as s # Use 's' alias for brevity

def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t

def grid_to_screen(pos):
    """Convert grid coordinates to screen coordinates (center of cell)"""
    return (pos[0] * s.GRID_SIZE + s.GRID_SIZE // 2, pos[1] * s.GRID_SIZE + s.GRID_SIZE // 2)

def screen_to_grid(pos):
     """Convert screen coordinates to grid coordinates"""
     return (pos[0] // s.GRID_SIZE, pos[1] // s.GRID_SIZE)

def get_perspective_scale(y_coord):
    """ Calculates a scale factor based on Y position """
    t = max(0, min(1, y_coord / s.HEIGHT)) # Normalize y-coordinate
    return lerp(s.MIN_SCALE, s.MAX_SCALE, t)