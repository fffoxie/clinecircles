"""CLINE CIRCLES - a verified Geometry Dash level generator.

Public API::

    from clinecircles import Level, LevelObject, gamedata, physics
    from clinecircles.serialization import write_gmd, build_level_string

Output is real GD data (``.gmd`` / level string), importable into the game
with the GDShare mod. See docs/VERIFICATION.md for what is verified.
"""

from .gamedata import Easing, GameMode, Obj, Prop, Speed
from .level import Level
from .model import Color, LevelObject, default_colors

__all__ = [
    "Level", "LevelObject", "Color", "default_colors",
    "Obj", "Prop", "Speed", "GameMode", "Easing",
]

__version__ = "0.1.0"
