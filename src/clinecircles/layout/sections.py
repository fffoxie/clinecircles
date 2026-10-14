"""The CLINE CIRCLES gameplay layout (Phase A).

Section plan, derived from the verified arrangement in
``data/music/nine_circles.json`` (174 BPM, drop1 @ bar 12, breakdown @ bar 20,
drop2 @ bar 27, end @ bar 44)::

    bars  0-12  intro / buildup   1x  CUBE   -> robot dances innocently
    bars 12-16  drop 1            2x  SHIP   -> giant eye transition
    bars 16-20  drop 1            2x  UFO    -> eye geometry
    bars 20-23  breakdown         1x  WAVE   -> uncanny, sparse
    bars 20-27  breakdown         1x  BALL+SPIDER -> boss introduction
    bars 27-31  drop 2            2x  ROBOT  -> boss awakens
    bars 31-35  drop 2            2x  SWING  -> escalation
    bars 35-40  drop 2            2x  CUBE+SHIP -> boss fight
    bars 40-44  finale            1x  CUBE   -> resolution + endscreen

Every mode the task asks for is present: cube, ship, UFO, wave, spider, swing,
robot (plus ball).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import gamedata as gd
from ..music import Timeline
from . import patterns as P
from .primitives import BLOCK, Builder, b

Ctx = P.Ctx


@dataclass
class SectionSpec:
    name: str
    start_bar: float
    end_bar: float
    mode: gd.GameMode
    speed: gd.Speed
    build: Callable[[Ctx, Timeline, float], None]


# --------------------------------------------------------------------------
# A - intro / buildup (bars 0-12, 1x, cube)
# --------------------------------------------------------------------------


def build_intro(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    P.ground(ctx)
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731

    # bars 0-1: empty run-in so the player can settle
    # bar 1: first single spike, generous
    ctx.build.spikes(at(bar0 + 1.5), at(bar0 + 1.5), ctx.floor_y,
                     color=gd.ColorChannel.OBJ, count=1)
    # bar 2: two spikes (one jump)
    x = at(bar0 + 2.5)
    ctx.build.spikes(x - BLOCK / 2, x + BLOCK / 2, ctx.floor_y,
                     color=gd.ColorChannel.OBJ, count=2)
    # bar 3 = first kick: a clean jump right on the accent
    P.cube_spike_gap(ctx, _frac(ctx, at(bar0 + 3.0)), 1,
                     color=gd.ColorChannel.OBJ)
    # bars 4-6: platform hops
    P.cube_platform(ctx, _frac(ctx, at(bar0 + 4.2)), 4, 3,
                    color=gd.ColorChannel.MG)
    P.cube_platform(ctx, _frac(ctx, at(bar0 + 5.4)), 4, 5,
                    color=gd.ColorChannel.MG)
    # bars 6-8: orb rhythm
    P.cube_orb_chain(ctx, _frac(ctx, at(bar0 + 6.8)), ("yellow", "pink"),
                     spacing_blocks=5.0, height_blocks=3.0)
    # bars 8-10: triple spike, the first real timing check
    x = at(bar0 + 9.0)
    ctx.build.spikes(x - BLOCK, x + BLOCK, ctx.floor_y,
                     color=gd.ColorChannel.OBJ, count=3)
    # bars 10-12: approach to the ship portal, clean runway
    ctx.build.mode(at(bar0 + 11.4), ctx.floor_y + 3, gd.GameMode.SHIP)


def _frac(ctx: Ctx, x: float) -> float:
    """Convert an absolute x into the section-relative fraction Ctx.at wants."""
    if ctx.length <= 0:
        return 0.0
    return max(0.0, min(1.0, (x - ctx.x0) / ctx.length))


# --------------------------------------------------------------------------
# B1 - drop 1, ship (bars 12-16, 2x)
# --------------------------------------------------------------------------


def build_drop1_ship(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    # open corridor: 11 blocks of flyable space (very forgiving)
    P.corridor(ctx, 11, color=gd.ColorChannel.MG, ceiling_color=gd.ColorChannel.MG)
    # pinches at bar accents, all leaving >= 6 blocks
    for k, (bar, gap, centre) in enumerate([
        (12.5, 7.0, 5.0),
        (13.5, 6.0, 7.0),
        (14.5, 6.5, 4.5),
    ]):
        P.flight_gap(ctx, _frac(ctx, at(bar0 + (bar - 12))), gap, centre,
                     width_blocks=2.0, color=gd.ColorChannel.OBJ)
    # saws as readable hazards in the open corridor
    P.saw(ctx, _frac(ctx, at(bar0 + 15.2)), 8.5, "large",
          color=gd.ColorChannel.WHITE)


# --------------------------------------------------------------------------
# B2 - drop 1, UFO (bars 16-20, 2x)
# --------------------------------------------------------------------------


def build_drop1_ufo(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    P.corridor(ctx, 10, color=gd.ColorChannel.MG2, ceiling_color=gd.ColorChannel.MG2)
    ctx.build.mode(at(bar0), ctx.floor_y + 3, gd.GameMode.UFO)
    for bar, gap, centre in [
        (16.6, 7.0, 5.0),
        (17.4, 6.5, 6.5),
        (18.2, 7.5, 4.0),
        (19.0, 6.0, 6.0),
        (19.6, 7.0, 5.0),
    ]:
        P.flight_gap(ctx, _frac(ctx, at(bar0 + (bar - 16))), gap, centre,
                     width_blocks=1.5, color=gd.ColorChannel.OBJ)



# --------------------------------------------------------------------------
# C1 - breakdown, wave (bars 20-23, 1x)
# --------------------------------------------------------------------------


def build_breakdown_wave(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    P.corridor(ctx, 9, color=gd.ColorChannel.MG, ceiling_color=gd.ColorChannel.MG)
    ctx.build.mode(at(bar0), ctx.floor_y + 3, gd.GameMode.WAVE)
    for i, bar in enumerate((20.5, 21.2, 21.9, 22.5)):
        centre = 4.5 if i % 2 == 0 else 6.0
        P.flight_gap(ctx, _frac(ctx, at(bar0 + (bar - 20))), 6.0, centre,
                     width_blocks=1.5, color=gd.ColorChannel.OBJ)


# --------------------------------------------------------------------------
# C2 - breakdown, ball + spider (bars 23-27, 1x)
# --------------------------------------------------------------------------


def build_breakdown_ball_spider(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    P.ground(ctx, color=gd.ColorChannel.MG)
    ctx.build.mode(at(bar0), ctx.floor_y + 3, gd.GameMode.BALL)
    pit_x0, pit_x1 = at(bar0 + 0.8), at(bar0 + 1.8)
    ctx.build.spikes(pit_x0, pit_x1, ctx.floor_y, color=gd.ColorChannel.OBJ,
                     count=max(2, int((pit_x1 - pit_x0) / BLOCK)))
    ctx.build.orb(at(bar0 + 1.3), ctx.floor_y + 4, "blue")
    ctx.build.mode(at(bar0 + 2.4), ctx.floor_y + 3, gd.GameMode.SPIDER)
    for i in range(3):
        x0 = at(bar0 + 2.8 + i * 1.0)
        ctx.build.floor(x0, x0 + b(2), ctx.floor_y, gd.ColorChannel.MG)
        ctx.build.spikes(x0 + b(2.6), x0 + b(3.0), ctx.floor_y,
                         color=gd.ColorChannel.OBJ, count=1)
    ctx.build.mode(at(bar0 + 6.6), ctx.floor_y + 3, gd.GameMode.CUBE)


# --------------------------------------------------------------------------
# D1 - drop 2, robot (bars 27-31, 2x)
# --------------------------------------------------------------------------


def build_drop2_robot(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    P.ground(ctx, color=gd.ColorChannel.MG2)
    ctx.build.mode(at(bar0), ctx.floor_y + 3, gd.GameMode.ROBOT)
    for bar in (27.6, 28.4, 29.2, 30.0):
        x = at(bar0 + (bar - 27))
        ctx.build.spikes(x - BLOCK / 2, x + BLOCK / 2, ctx.floor_y,
                         color=gd.ColorChannel.OBJ, count=2)
    P.cube_platform(ctx, _frac(ctx, at(bar0 + 30.6)), 3, 4,
                    color=gd.ColorChannel.MG)


# --------------------------------------------------------------------------
# D2 - drop 2, swing (bars 31-35, 2x)
# --------------------------------------------------------------------------


def build_drop2_swing(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    P.corridor(ctx, 10, color=gd.ColorChannel.MG2,
               ceiling_color=gd.ColorChannel.MG2)
    ctx.build.mode(at(bar0), ctx.floor_y + 3, gd.GameMode.SWING)
    for i, bar in enumerate((31.6, 32.4, 33.2, 34.0, 34.6)):
        centre = 5.0 if i % 2 == 0 else 7.0
        P.flight_gap(ctx, _frac(ctx, at(bar0 + (bar - 31))), 6.5, centre,
                     width_blocks=1.5, color=gd.ColorChannel.OBJ)
    P.saw(ctx, _frac(ctx, at(bar0 + 34.4)), 8.0, "medium",
          color=gd.ColorChannel.WHITE)


# --------------------------------------------------------------------------
# D3 - boss fight, cube + ship (bars 35-40, 2x)
# --------------------------------------------------------------------------


def build_boss_fight(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    P.ground(ctx, color=gd.ColorChannel.MG)
    ctx.build.mode(at(bar0), ctx.floor_y + 3, gd.GameMode.CUBE)
    for i, bar in enumerate((35.5, 36.0, 36.5, 37.0)):
        x = at(bar0 + (bar - 35))
        ctx.build.spikes(x - BLOCK / 2, x + BLOCK / 2, ctx.floor_y,
                         color=gd.ColorChannel.OBJ, count=1 + (i % 2))
    ctx.build.mode(at(bar0 + 37.6), ctx.floor_y + 3, gd.GameMode.SHIP)
    P.corridor(ctx, 11, color=gd.ColorChannel.MG2,
               ceiling_color=gd.ColorChannel.MG2)
    for bar, gap, centre in [(38.0, 6.5, 5.0), (38.6, 6.0, 7.0),
                             (39.2, 6.5, 4.5)]:
        P.flight_gap(ctx, _frac(ctx, at(bar0 + (bar - 35))), gap, centre,
                     width_blocks=1.5, color=gd.ColorChannel.OBJ)


# --------------------------------------------------------------------------
# E - finale (bars 40-44, 1x, cube)
# --------------------------------------------------------------------------


def build_finale(ctx: Ctx, tl: Timeline, bar0: float) -> None:
    at = lambda bar: tl.x_at_bar(bar)  # noqa: E731
    P.ground(ctx, color=gd.ColorChannel.MG)
    ctx.build.mode(at(bar0), ctx.floor_y + 3, gd.GameMode.CUBE)
    P.cube_spike_gap(ctx, _frac(ctx, at(bar0 + 1.0)), 1,
                     color=gd.ColorChannel.OBJ)
    P.cube_spike_gap(ctx, _frac(ctx, at(bar0 + 2.0)), 2,
                     color=gd.ColorChannel.OBJ)


# --------------------------------------------------------------------------
# The plan
# --------------------------------------------------------------------------


SECTIONS: list[SectionSpec] = [
    SectionSpec("intro", 0, 12, gd.GameMode.CUBE, gd.Speed.NORMAL, build_intro),
    SectionSpec("drop1_ship", 12, 16, gd.GameMode.SHIP, gd.Speed.FAST,
                build_drop1_ship),
    SectionSpec("drop1_ufo", 16, 20, gd.GameMode.UFO, gd.Speed.FAST,
                build_drop1_ufo),
    SectionSpec("breakdown_wave", 20, 23, gd.GameMode.WAVE, gd.Speed.NORMAL,
                build_breakdown_wave),
    SectionSpec("breakdown_ball_spider", 23, 27, gd.GameMode.BALL,
                gd.Speed.NORMAL, build_breakdown_ball_spider),
    SectionSpec("drop2_robot", 27, 31, gd.GameMode.ROBOT, gd.Speed.FAST,
                build_drop2_robot),
    SectionSpec("drop2_swing", 31, 35, gd.GameMode.SWING, gd.Speed.FAST,
                build_drop2_swing),
    SectionSpec("boss_fight", 35, 40, gd.GameMode.CUBE, gd.Speed.FAST,
                build_boss_fight),
    SectionSpec("finale", 40, 44, gd.GameMode.CUBE, gd.Speed.NORMAL,
                build_finale),
]
