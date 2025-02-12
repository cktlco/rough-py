"""
Provides basic geometry primitives such as points and lines.

This module defines:
  - Point: A 2D coordinate tuple (float, float).
  - Line: A tuple consisting of two Points.
  - line_length(): A function to compute the Euclidean distance between the two Points in a Line.
"""

from __future__ import annotations
import math
from typing import Tuple

# A Point is defined as a tuple of two floats: (x, y)
Point = Tuple[float, float]
# A Line is defined as a tuple containing two Points
Line = Tuple[Point, Point]


def line_length(line: Line) -> float:
    """
    Computes and returns the Euclidean distance between the two endpoints of the given line.

    :param line: A Line, represented as a tuple of two Point values.
                 Each Point is a tuple of (x, y) coordinates.
    :return: The distance as a float.
    """
    p1, p2 = line
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
