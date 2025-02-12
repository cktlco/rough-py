"""
Provides seeded random generation and utility functions for the rough library.

This module contains:
  - random_seed(): A function to produce a random integer seed in the range [0, 2^31).
  - Random:       A simple linear congruential generator (LCG) for pseudo-random floats.
"""

from __future__ import annotations
import random


def random_seed() -> int:
    """
    Generates a random integer seed in the range [0, 2^31).

    :return: A random integer seed.
    """
    return int(random.random() * (2**31))


class Random:
    """
    Implements a simple linear congruential generator (LCG) for pseudo-random float values.
    The sequence is determined by an internal state initialized with the provided seed.
    """

    def __init__(self, seed: int) -> None:
        """
        Initializes the LCG with the specified seed.

        :param seed: An integer seed to use for the LCG.
        """
        self.seed = seed
        self._state = seed

    def next(self) -> float:
        """
        Generates the next pseudo-random float in [0, 1) based on the current state.

        If the internal state is zero, it falls back to Python's built-in random().

        :return: A pseudo-random float in the range [0, 1).
        """
        if self._state == 0:
            # Fall back to Python's built-in random if the state is zero.
            return random.random()
        self._state = (self._state * 48271) % 2147483647
        return self._state / 2147483647
