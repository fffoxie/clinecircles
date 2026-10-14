"""Gameplay layout generation (Phase A)."""

from .build import BuildResult, build_level, make_timeline
from .patterns import Ctx
from .primitives import BLOCK, Builder, b, snap_ground

__all__ = ["BuildResult", "build_level", "make_timeline", "Builder", "Ctx",
           "BLOCK", "b", "snap_ground"]
