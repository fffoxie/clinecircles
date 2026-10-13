"""CLINE CIRCLES gameplay plan (rebuilt after real playtesting).

PLAYTEST FINDING (tools/wd_probe8.py, in Web Dashers):
  A) a continuous row of blocks at y=15 kills the player at x~21
  B) an empty level runs forever on the engine ground
  D) floating blocks well above the ground are safe to run under

Geometry Dash supplies the ground itself. A row of ground-level blocks is NOT
a floor: the player collides with their sides. So this level follows the
convention RobTop's own levels use (verified against assets/levels/1.txt):

  * the player runs on the ENGINE GROUND - no ground-level block rows
  * hazards (spikes) sit on the ground at y=15
  * solid geometry floats ABOVE the run line, bottom at y>=60 (2 blocks up),
    leaving the player's body clear and reachable by jumping
  * flight corridors are bounded by two floating platform rows
  * ground *decoration* is added separately with NON-SOLID objects

Coordinate convention: y=15 is a ground-level object; y=45+2k is a floating
row (k=0 -> centre 75, spans 60..90).
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import gamedata as gd
from ..music import Timeline
from .primitives import BLOCK, Builder

# Ground-level object centre (spikes, portals).
GROUND = 15.0
# Centre of the first safe floating platform row (spans 60..90).
FLOAT1 = 75.0


def row_centre(level: int) -> float:
    """Centre y of floating platform row `level` (0 -> FLOAT1)."""
    return FLOAT1 + level * BLOCK


@dataclass
class Ctx:
    """Section context: builder, x-range, speed and mode."""

    build: Builder
    x0: float
    x1: float
    speed: gd.Speed
    mode: gd.GameMode

    @property
    def length(self) -> float:
        return self.x1 - self.x0

    def at(self, frac: float) -> float:
        return self.x0 + self.length * frac


# --------------------------------------------------------------------------
# Ground-level primitives (safe)
# -------------------------------------------------------------------------- 


def spike(ctx: Ctx, at: float, count: int = 1, y: float = GROUND,
          color: int | None = None) -> float:
    """A spike cluster sitting on the ground at `at` (0..1 or absolute)."""
    x = at if at > 1.0 else ctx.at(at)
    span = (count - 1) * BLOCK
    ctx.build.spikes(x - span / 2, x + span / 2, 0.0, color, count=count)
    return x


def spikes_between(ctx: Ctx, x0: float, x1: float, count: int,
                   color: int | None = None) -> None:
    ctx.build.spikes(x0, x1, 0.0, color, count=count)


def saw(ctx: Ctx, x: float, y: float, size: str = "medium",
        color: int | None = None) -> None:
    obj = {"large": gd.Obj.SAW_LARGE, "medium": gd.Obj.SAW_MEDIUM,
           "small": gd.Obj.SAW_SMALL}[size]
    ctx.build.hazard(x, y, BLOCK * 2, BLOCK * 2, obj, color)


def orb(ctx: Ctx, x: float, y: float, kind: str = "yellow",
        groups: tuple[int, ...] = ()) -> None:
    ctx.build.orb(x, y, kind)


def portal(ctx: Ctx, x: float, y: float, obj: gd.Obj,
           groups: tuple[int, ...] = ()) -> None:
    ctx.build.portal(x, y, obj, groups)


def mode_portal(ctx: Ctx, x: float, mode: gd.GameMode,
                y: float = FLOAT1) -> None:
    ctx.build.mode(x, y, mode)


def speed_portal(ctx: Ctx, x: float, speed: gd.Speed,
                 y: float = FLOAT1) -> None:
    ctx.build.speed(x, y, speed)


# --------------------------------------------------------------------------
# Floating platforms
# -------------------------------------------------------------------------- 


def platform(ctx: Ctx, x0: float, x1: float, level: int = 0,
             color: int | None = None, obj: int = gd.Obj.BLOCK_SQUARE) -> None:
    """A floating platform row spanning x0..x1 at floating level `level`."""
    yc = row_centre(level)
    ctx.build.floor(x0, x1, (yc - 15.0) / BLOCK, color, obj)


def corridor(ctx: Ctx, span_blocks: float, level: int = 0,
             color: int | None = None) -> None:
    """Floor+ceiling floating rows leaving `span_blocks` of flyable space."""
    yc = row_centre(level)
    platform(ctx, ctx.x0, ctx.x1, level, color)
    top_yc = yc + span_blocks * BLOCK
    ctx.build.floor(ctx.x0, ctx.x1, (top_yc - 15.0) / BLOCK, color)


def gap(ctx: Ctx, x: float, opening: float, centre: float, level: int = 0,
        width: float = 45.0, color: int | None = None) -> None:
    """Pinch a corridor: solid above and below, leaving an opening."""
    yc = row_centre(level)
    lo = yc - 15.0 + centre * BLOCK - opening * BLOCK / 2
    hi = lo + opening * BLOCK
    y = yc - 15.0
    while y + BLOCK <= lo:
        ctx.build.solid(x, y + BLOCK / 2, width, BLOCK, color)
        y += BLOCK
    y = hi
    while y <= yc + 15.0 + 8 * BLOCK:
        ctx.build.solid(x, y + BLOCK / 2, width, BLOCK, color)
        y += BLOCK


# --------------------------------------------------------------------------
# Section builders
# -------------------------------------------------------------------------- 


def _x(tl: Timeline, bar: float) -> float:
    return tl.x_at_bar(bar)


def build_intro(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 0-12, cube, 1x - learnable jumps that grow in density."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    # bars 0-1: clean run-in, nothing to do but settle
    spike(ctx, X(1.0), 1, color=gd.ColorChannel.OBJ)
    spike(ctx, X(2.0), 2, color=gd.ColorChannel.OBJ)
    spike(ctx, X(3.0), 1, color=gd.ColorChannel.OBJ)   # bar 3 = first kick
    # a first floating platform to jump onto and off
    platform(ctx, X(3.8), X(4.6), 0, gd.ColorChannel.MG)
    spike(ctx, X(4.2), 1, color=gd.ColorChannel.OBJ)
    # rhythm: spike, spike-spike, gap
    for b in (5.0, 5.5, 6.0):
        spike(ctx, X(b), 1, color=gd.ColorChannel.OBJ)
    orb(ctx, X(6.6), row_centre(1), "yellow")
    platform(ctx, X(7.0), X(7.8), 0, gd.ColorChannel.MG)
    spike(ctx, X(7.4), 1, color=gd.ColorChannel.OBJ)
    # build to the drop
    spike(ctx, X(8.5), 2, color=gd.ColorChannel.OBJ)
    spike(ctx, X(9.5), 3, color=gd.ColorChannel.OBJ)
    spike(ctx, X(10.5), 1, color=gd.ColorChannel.OBJ)
    # approach: clean runway into the ship portal
    mode_portal(ctx, X(11.5), gd.GameMode.SHIP)


def build_ship(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 12-16, ship, 2x - 6-block openings, generous but rhythmic."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    corridor(ctx, 6.0, 0, gd.ColorChannel.MG)
    for b, opening, centre in ((0.6, 3.2, 1.8), (1.4, 2.6, 3.4),
                               (2.2, 3.0, 1.6), (3.0, 2.8, 3.6),
                               (3.6, 3.2, 2.0)):
        gap(ctx, X(b), opening, centre, 0, 45, gd.ColorChannel.OBJ)
    saw(ctx, X(2.6), row_centre(0) + 15 + 4.5 * BLOCK, "large",
        gd.ColorChannel.WHITE)


def build_ufo(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 16-20, UFO, 2x - hop through openings on the beat."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    mode_portal(ctx, X(0.0), gd.GameMode.UFO)
    corridor(ctx, 6.0, 0, gd.ColorChannel.MG2)
    for b, opening, centre in ((0.6, 3.4, 2.0), (1.0, 2.8, 3.6),
                               (1.6, 3.2, 1.8), (2.0, 2.6, 3.4),
                               (2.6, 3.4, 2.2), (3.0, 2.8, 1.6),
                               (3.6, 3.2, 3.4)):
        gap(ctx, X(b), opening, centre, 0, 30, gd.ColorChannel.OBJ)


def build_wave(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 20-23, wave, 1x - sparse, precise, uncanny."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    mode_portal(ctx, X(0.0), gd.GameMode.WAVE)
    corridor(ctx, 5.0, 1, gd.ColorChannel.MG)
    for b, opening, centre in ((0.5, 2.6, 1.6), (1.0, 2.4, 2.8),
                              (1.5, 2.6, 1.4), (2.0, 2.2, 2.6),
                              (2.5, 2.6, 1.8)):
        gap(ctx, X(b), opening, centre, 1, 30, gd.ColorChannel.OBJ)


def build_ball_spider(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 23-27, ball then spider, 1x - gravity flips and teleports."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    mode_portal(ctx, X(0.0), gd.GameMode.BALL)
    # ball: flip over a spike pit
    spikes_between(ctx, X(0.6), X(1.6), 5, gd.ColorChannel.OBJ)
    orb(ctx, X(1.1), row_centre(1), "blue")
    platform(ctx, X(2.0), X(2.8), 0, gd.ColorChannel.MG)
    mode_portal(ctx, X(3.0), gd.GameMode.SPIDER)
    # spider: hop platforms
    for i in range(3):
        platform(ctx, X(3.2 + i * 0.9), X(3.9 + i * 0.9), 0,
                 gd.ColorChannel.MG2)
        spike(ctx, X(4.05 + i * 0.9), 1, color=gd.ColorChannel.OBJ)
    platform(ctx, X(6.0), X(6.8), 0, gd.ColorChannel.MG)
    mode_portal(ctx, X(6.9), gd.GameMode.CUBE)


def build_robot(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 27-31, robot, 2x - variable-height jumps over rising spikes."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    mode_portal(ctx, X(0.0), gd.GameMode.ROBOT)
    for i, b in enumerate((0.6, 1.4, 2.2, 3.0)):
        spike(ctx, X(b), 1 + (i % 2), color=gd.ColorChannel.OBJ)
    platform(ctx, X(3.5), X(4.0), 0, gd.ColorChannel.MG)


def build_swing(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 31-35, swing, 2x - gravity-flipping flight through openings."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    mode_portal(ctx, X(0.0), gd.GameMode.SWING)
    corridor(ctx, 5.5, 0, gd.ColorChannel.MG2)
    for b, opening, centre in ((0.6, 2.8, 1.8), (1.4, 2.6, 3.2),
                               (2.2, 3.0, 1.6), (3.0, 2.6, 3.4),
                               (3.6, 2.8, 2.0)):
        gap(ctx, X(b), opening, centre, 0, 30, gd.ColorChannel.OBJ)
    saw(ctx, X(3.3), row_centre(0) + 15 + 4.0 * BLOCK, "medium",
        gd.ColorChannel.WHITE)


def build_boss(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 35-40, cube then ship, 2x - the boss fight."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    mode_portal(ctx, X(0.0), gd.GameMode.CUBE)
    for i, b in enumerate((0.4, 0.9, 1.4, 1.9, 2.4)):
        spike(ctx, X(b), 1 + (i % 2), color=gd.ColorChannel.OBJ)
    mode_portal(ctx, X(2.7), gd.GameMode.SHIP)
    corridor(ctx, 6.0, 0, gd.ColorChannel.MG2)
    for b, opening, centre in ((3.0, 3.0, 1.8), (3.6, 2.6, 3.4),
                               (4.2, 3.2, 1.6), (4.7, 2.8, 3.2)):
        gap(ctx, X(b), opening, centre, 0, 30, gd.ColorChannel.OBJ)


def build_finale(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    """bars 40-44, cube, 1x - two last clean jumps, then an open runway for
    the endscreen composition."""
    X = lambda b: _x(tl, bar0 + b)  # noqa: E731
    mode_portal(ctx, X(0.0), gd.GameMode.CUBE)
    spike(ctx, X(0.8), 1, color=gd.ColorChannel.OBJ)
    spike(ctx, X(1.6), 2, color=gd.ColorChannel.OBJ)
    # open space from bar 2.4 to the end for the endscreen


# --------------------------------------------------------------------------
# The plan
# -------------------------------------------------------------------------- 


@dataclass
class SectionSpec:
    name: str
    start_bar: float
    end_bar: float
    mode: gd.GameMode
    speed: gd.Speed
    build: object


SECTIONS: list[SectionSpec] = [
    SectionSpec("intro", 0, 12, gd.GameMode.CUBE, gd.Speed.NORMAL, build_intro),
    SectionSpec("drop1_ship", 12, 16, gd.GameMode.SHIP, gd.Speed.FAST, build_ship),
    SectionSpec("drop1_ufo", 16, 20, gd.GameMode.UFO, gd.Speed.FAST, build_ufo),
    SectionSpec("breakdown_wave", 20, 23, gd.GameMode.WAVE, gd.Speed.NORMAL, build_wave),
    SectionSpec("breakdown_ball_spider", 23, 27, gd.GameMode.BALL, gd.Speed.NORMAL, build_ball_spider),
    SectionSpec("drop2_robot", 27, 31, gd.GameMode.ROBOT, gd.Speed.FAST, build_robot),
    SectionSpec("drop2_swing", 31, 35, gd.GameMode.SWING, gd.Speed.FAST, build_swing),
    SectionSpec("boss_fight", 35, 40, gd.GameMode.CUBE, gd.Speed.FAST, build_boss),
    SectionSpec("finale", 40, 44, gd.GameMode.CUBE, gd.Speed.NORMAL, build_finale),
]
