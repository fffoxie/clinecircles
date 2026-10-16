"""The verification stack: renderer, trigger simulator, player simulator, lint.

Nothing here is the game. Everything here exists so the level can be built,
looked at and *measured* without a Geometry Dash client.
"""

from .draw import Camera, draw_scene  # noqa: F401

__all__ = ["Camera", "draw_scene"]
