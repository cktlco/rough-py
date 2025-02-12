"""
Convenient factory functions and core imports for rough-py modules.

This file provides simple entry points to create and work with the core RoughCanvas
and RoughGenerator objects, as well as a convenience function for generating
a new random seed. It also imports commonly used classes and functions from
the internal modules.
"""

from .canvas import RoughCanvas
from .generator import RoughGenerator
from .math import random_seed
from .core import Config, Options


def canvas(width: int, height: int, config: Config | None = None) -> RoughCanvas:
    """
    Create a RoughCanvas object.

    RoughCanvas is the primary interface for drawing shapes with a 'rough',
    hand-sketched style on a logical canvas. The rendered result can be exported to
    SVG or otherwise manipulated.

    :param width: The width of the canvas in logical units (often pixels in many contexts).
    :param height: The height of the canvas in logical units.
    :param config: (Optional) A Config object containing global options for rough drawing.
    :return: A newly created RoughCanvas instance.
    """
    return RoughCanvas(width, height, config)


def generator(config: Config | None = None) -> RoughGenerator:
    """
    Create a RoughGenerator object.

    RoughGenerator provides shape-drawing methods that return Drawable objects,
    which hold the geometry and drawing instructions in a "rough" style.

    :param config: (Optional) A Config object containing global options for rough drawing.
    :return: A RoughGenerator instance.
    """
    return RoughGenerator(config)


def new_seed() -> int:
    """
    Generate a new random integer seed to used to initialize the rough drawing algorithms.

    :return: An integer seed, typically in the range [0, 2^31).
    """
    return random_seed()
