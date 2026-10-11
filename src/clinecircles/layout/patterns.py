"""Reusable, safety-margined gameplay patterns.

Difficulty comes from rhythm and speed, not from pixel-precise inputs: every
pattern here leaves at least ``SAFE_MARGIN`` blocks of clearance, so a 20%
error in the estimated physics constants cannot make a section impossible.

Helpers take/return *units* (1 block = 30); bar/beat maths is done by the
caller through :class:`~clinecircles.music.Timeline`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import gamedata as gd
from ..physics import cube_jump_height_blocks, cube_jump_length_blocks
from .primitives import BLOCK, Builder, b, snap_ground

# Minimum free vertical space we leave in flight corridors, in blocks.
SAFE_MARGIN = 4.0


@dataclass
class Ctx:
    """Context handed to a section builder."""

    build: Builder
    x0: float
    x1: float
    speed: gd.Speed
    mode: gd.GameMode
    floor_y: float = 0.0

    @property
    def length(self) -> float:
        return self.x1 - self.x0

    def at(self, frac: float) -> float:
        """A position ``frac`` (0..1) through the section."""
        return self.x0 + self.length * frac


def ground(ctx: Ctx, color: int | None = None, obj: int = gd.Obj.BLOCK_SQUARE,
           y: float | None = None) -> None:
    """Fill the floor for the whole section."""
    ctx.build.floor(ctx.x0, ctx.x1, ctx.floor_y if y is None else y, color, obj)


def corridor(ctx: Ctx, gap_blocks: float, color: int | None = None,
             ceiling_color: int | None = None) -> None:
    """Floor plus a ceiling leaving ``gap_blocks`` of flyable space."""
    ctx.build.floor(ctx.x0, ctx.x1, ctx.floor_y, color)
    ctx.build.ceiling(ctx.x0, ctx.x1, ctx.floor_y + gap_blocks,
                      ceiling_color if ceiling_color is not None else color)


# --------------------------------------------------------------------------
# Cube patterns
# --------------------------------------------------------------------------


def cube_jump_metrics(speed: gd.Speed) -> tuple[float, float]:
    """(jump height blocks, jump length blocks) at a given speed."""
    return (cube_jump_height_blocks(int(speed)),
            cube_jump_length_blocks(int(speed)))


def cube_spike_gap(ctx: Ctx, at: float, n_spikes: int = 1,
                   color: int | None = None) -> float:
    """A short spike cluster cleared with one jump. Returns its centre x."""
    x = ctx.at(at)
    span = (n_spikes - 1) * BLOCK
    ctx.build.spikes(x - span / 2, x + span / 2, ctx.floor_y, color,
                     count=n_spikes)
    return x


def cube_platform(ctx: Ctx, at: float, width_blocks: float,
                  height_blocks: float, color: int | None = None,
                  spikes_below: bool = False) -> float:
    """A floating platform the player lands on."""
    x = ctx.at(at)
    y = ctx.floor_y + height_blocks
    ctx.build.floor(x, x + b(width_blocks), y, color)
    if spikes_below:
        ctx.build.spikes(x + BLOCK / 2, x + b(width_blocks) - BLOCK / 2,
                         ctx.floor_y, color, count=max(1, int(width_blocks) - 1))
    return x


def cube_orb_chain(ctx: Ctx, at: float, kinds: tuple[str, ...],
                   spacing_blocks: float = 4.0,
                   height_blocks: float = 3.0) -> None:
    """A chain of orbs to be hit in sequence (rhythm jumps)."""
    x = ctx.at(at)
    for i, kind in enumerate(kinds):
        ctx.build.orb(x + i * b(spacing_blocks), ctx.floor_y + height_blocks,
                      kind)


def mode_switch(ctx: Ctx, at: float, mode: gd.GameMode,
                height_blocks: float = 3.0) -> None:
    ctx.build.mode(ctx.at(at), ctx.floor_y + height_blocks, mode)


def speed_switch(ctx: Ctx, at: float, speed: gd.Speed,
                 height_blocks: float = 3.0) -> None:
    ctx.build.speed(ctx.at(at), ctx.floor_y + height_blocks, speed)



# --------------------------------------------------------------------------
# Flight patterns (ship / ufo / wave / ball / spider / robot / swing)
# --------------------------------------------------------------------------


def flight_gap(ctx: Ctx, at: float, gap_blocks: float,
               gap_centre_blocks: float, width_blocks: float = 2.0,
               headroom_blocks: float = 12.0,
               color: int | None = None) -> None:
    """Pinch the corridor, leaving a gap the player flies through.

    Solid blocks are added from the floor up to the opening and from the
    opening up to the headroom, so the only way through is the gap.
    """
    x = ctx.at(at)
    w = b(width_blocks)
    lo = ctx.floor_y + gap_centre_blocks - gap_blocks / 2
    hi = ctx.floor_y + gap_centre_blocks + gap_blocks / 2
    y = ctx.floor_y
    while y + 1 <= lo:
        ctx.build.solid(x, snap_ground(y), w, BLOCK, color)
        y += 1
    y = hi
    while y <= ctx.floor_y + headroom_blocks:
        ctx.build.solid(x, snap_ground(y), w, BLOCK, color)
        y += 1


def saw(ctx: Ctx, at: float, height_blocks: float, size: str = "medium",
        color: int | None = None) -> None:
    """A rotating saw hazard (verified ids 1705/1706/1707)."""
    obj = {"large": gd.Obj.SAW_LARGE, "medium": gd.Obj.SAW_MEDIUM,
           "small": gd.Obj.SAW_SMALL}[size]
    x = ctx.at(at)
    ctx.build.hazard(x, ctx.floor_y + height_blocks, BLOCK * 2, BLOCK * 2,
                     obj, color)


def spike_wall(ctx: Ctx, at: float, from_blocks: float, to_blocks: float,
               color: int | None = None) -> None:
    """A vertical run of spikes rising from the floor."""
    x = ctx.at(at)
    y = from_blocks
    while y <= to_blocks:
        ctx.build.hazard(x, snap_ground(ctx.floor_y + y), BLOCK, BLOCK,
                         gd.Obj.SPIKE, color)
        y += 1


def ceiling_pinch(ctx: Ctx, at: float, gap_blocks: float, y_blocks: float,
                  color: int | None = None) -> None:
    """A ceiling stub that narrows a corridor (wave/ship-friendly)."""
    x = ctx.at(at)
    ctx.build.ceiling(x - BLOCK, x + BLOCK,
                      ctx.floor_y + y_blocks + gap_blocks, color)


def orb_flight(ctx: Ctx, at: float, kind: str, y_blocks: float) -> None:
    ctx.build.orb(ctx.at(at), ctx.floor_y + y_blocks, kind)
