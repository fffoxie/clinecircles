"""The generator for THE FLAMES OF FATE.

Public entry point::

    from clinecircles.gen import build_level
    result = build_level()          # level + builder + song map + timeline

Modules
-------
builder     geometry primitives, with a record of what was placed
patterns    reusable, safety-margined gameplay patterns
sections    one builder per music-map section
palette     the colour script
mascots     Cline and Antigravity, built from GD objects
deco        decoration modules and the per-section decoration pass
effects     transitions, camera work, beat-synced triggers, endscreen
build       the orchestrator
"""

from .build import BuildResult, build_level  # noqa: F401

__all__ = ["BuildResult", "build_level"]
