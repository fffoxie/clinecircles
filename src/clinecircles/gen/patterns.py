"""Gameplay for THE FLAMES OF FATE, one builder per music-map section.

Design rules that keep this a fair **Medium Demon** rather than a guessing game:

* every hazard is readable >= 0.4 s ahead. At 3x that is 187 units, so nothing
  is placed closer than 200 units after a portal, a screen-wide transition or a
  blind corner.
* cube jumps cover ~4.5 blocks at 1x, ~4.9 at 2x and ~5.1 at 3x (computed from
  the verified physics in :mod:`clinecircles.physics`). Spike clusters are at
  most 3 blocks wide, are spaced >= 5 blocks apart, and always leave >= 6 blocks
  of runway before the first one.
* flight corridors are never narrower than 4 blocks (120 units) and are usually
  5-7 blocks, so a 20% error in an estimated constant cannot make them
  impossible.
* hazards sit on the beat: spikes land on kicks, wave corridors pinch on the
  snare, and gamemode/speed portals land exactly on bar lines.
* no random-click gimmicks: every input is either a jump on a spike, a hold in a
  corridor, or an orb on a marked beat.

Sections are expressed in beats, converted to x through the :class:`Timeline`,
so a change in tempo or speed moves the gameplay with the music.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import ids
from ..gamedata import GameMode, Obj, Speed
from ..physics import (cube_jump_height_blocks, cube_jump_length_blocks)
from ..songmap import SectionDesign, SongMap
from ..timeline import Timeline
from .builder import BLOCK, FLOAT_FLOOR, GROUND, Builder

#: how far ahead a hazard must be visible, in seconds
READ_TIME = 0.4


@dataclass
class SecCtx:
    """Everything a section builder needs, plus musical helpers."""

    b: Builder
    song: SongMap
    tl: Timeline
    spec: SectionDesign
    x0: float
    x1: float
    t0: float
    t1: float

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def mode(self) -> GameMode:
        return self.spec.mode

    @property
    def speed(self) -> Speed:
        return self.spec.speed

    @property
    def length(self) -> float:
        return self.x1 - self.x0

    @property
    def units_per_beat(self) -> float:
        return self.tl.units_at(self.t0) * self.song.beat_s

    # -- musical positions ------------------------------------------------
    def beat_x(self, beats: float) -> float:
        """x of the beat ``beats`` beats after the section start."""
        return self.tl.x_at_time(self.t0 + beats * self.song.beat_s)

    def bar_x(self, bars: float) -> float:
        return self.tl.x_at_time(self.t0 + bars * self.song.bar_s)

    def frac_x(self, f: float) -> float:
        return self.x0 + self.length * f

    def read_ahead(self) -> float:
        """Units of x covered by ``READ_TIME`` seconds at this speed."""
        return self.tl.units_at(self.t0) * READ_TIME

    # -- convenience ------------------------------------------------------
    def colour(self) -> int:
        return int(ids.Obj.BLOCK_SQUARE) and 1004  # OBJ channel

    def spike(self, x: float, *, y: float = GROUND, count: int = 1,
              color: int | None = None, step: float = BLOCK, **kw) -> float:
        """A spike cluster centred on ``x``; returns its centre."""
        span = (count - 1) * step
        self.b.spikes_row(x - span / 2, x + span / 2, y=y, count=count,
                          color=color, **kw)
        return x

    def spike_ceiling(self, x: float, *, y: float, count: int = 1,
                      color: int | None = None) -> float:
        span = (count - 1) * BLOCK
        self.b.spikes_row(x - span / 2, x + span / 2, y=y, count=count,
                          color=color, flip_y=True)
        return x


# --------------------------------------------------------------------------
# Reusable patterns
# --------------------------------------------------------------------------


def runway(ctx: SecCtx) -> None:
    """Nothing at all for the first beat of a section (breathing room)."""
    return None


def flight_pinch(ctx: SecCtx, x: float, *, gap: float, centre: float,
                 width: float = BLOCK, color: int | None = None,
                 ceiling_y: float = 315.0, z: int | None = None) -> None:
    """A wall with a hole: solid below the gap and above it.

    The wall is filled from the ground surface up to the opening and from the
    opening up to ``ceiling_y``, so nothing is placed below the ground (where it
    would be invisible) or far above the screen.
    """
    b = ctx.b
    lo = centre - gap / 2
    hi = centre + gap / 2
    y = GROUND
    while y < lo - 1e-6:
        b.block(x, y, w=width, color=color, z=z)
        y += BLOCK
    y = hi
    while y <= ceiling_y + 1e-6:
        b.block(x, y, w=width, color=color, z=z)
        y += BLOCK


def flight_tunnel(ctx: SecCtx, x0: float, x1: float, *, gap: float,
                  centre: float, color: int | None = None,
                  ceiling_color: int | None = None, z: int | None = None,
                  ) -> None:
    """A long corridor: a floor row and a ceiling row with a ``gap`` slot."""
    ctx.b.corridor(x0, x1, gap=gap, centre=centre, color=color,
                   ceiling_color=ceiling_color, z=z)


def wave_tunnel(ctx: SecCtx, x0: float, x1: float, *, gap: float,
                centre_fn, channel: int, floor_y: float = FLOAT_FLOOR,
                ceiling_y: float = FLOAT_FLOOR + 360.0,
                z: int | None = None) -> int:
    """The classic wave corridor: a floor and a ceiling that weave.

    For every 30-unit step the corridor's centre moves along ``centre_fn``
    (which takes the 0..1 fraction through the tunnel), leaving a constant
    ``gap`` to fly through. Solid blocks fill from the tunnel floor up to the
    opening and from the opening up to the tunnel ceiling.

    Returns the number of blocks placed.
    """
    b = ctx.b
    n = max(2, int(round((x1 - x0) / BLOCK)))
    placed = 0
    for i in range(n + 1):
        x = x0 + i * BLOCK
        c = centre_fn(i / n)
        lo = round((c - gap / 2) / BLOCK) * BLOCK
        hi = round((c + gap / 2) / BLOCK) * BLOCK
        y = floor_y
        while y < lo:
            if b.block(x, y, color=channel, z=z) is not None:
                placed += 1
            y += BLOCK
        y = hi
        while y <= ceiling_y:
            if b.block(x, y, color=channel, z=z) is not None:
                placed += 1
            y += BLOCK
    return placed
