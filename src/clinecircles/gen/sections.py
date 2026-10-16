"""Gameplay for THE FLAMES OF FATE: one builder per music-map section.

Design rules that keep this a fair Medium Demon rather than a guessing game:

* every hazard is readable >= 0.4 s ahead. At 3x that is 187 units, so nothing
  is placed closer than 200 units after a portal or a screen-wide transition.
* cube jumps cover ~4.5 blocks at 1x, ~4.9 at 2x, ~5.1 at 3x (from the verified
  physics in :mod:`clinecircles.physics`). Spike clusters are at most 3 blocks
  wide, sit >= 5 blocks apart and always leave >= 6 blocks of runway.
* flight corridors are never narrower than 4 blocks (120 units), usually 5-7.
* hazards land on beats; gamemode and speed portals land exactly on bar lines.
* the first bar of a flight section and the last bar of a cube section are left
  open, so the player can always be at the height the portal expects.

Sections are expressed in beats and converted to x through the Timeline, so a
change of tempo or speed moves the gameplay with the music.
"""

from __future__ import annotations

import math

from ..gamedata import GameMode, Obj, Speed
from . import palette as PAL
from . import patterns as P
from .builder import BLOCK, FLOAT_FLOOR, GROUND, Builder
from .patterns import SecCtx

C_HAZ = PAL.CH_HAZARD
C_SOL = PAL.CH_SOLID
C_EDGE = PAL.CH_SOLID_EDGE
C_ACC = PAL.CH_ACCENT
C_FAR = PAL.CH_DECO_FAR
C_MID = PAL.CH_DECO_MID
C_NEAR = PAL.CH_DECO_NEAR

#: centre of a flight corridor (7.5 blocks) - where portals go in flight modes
FLY = 225.0
#: slot heights used by the flight sections (units)
GAP_SHIP = 150.0
GAP_UFO = 180.0
GAP_WAVE = 120.0
GAP_BALL = 330.0
GAP_SWING = 180.0
#: the ceiling row used by ball / swing / wave sections
CEIL = FLOAT_FLOOR + 240.0   # 315: visible when the player flies at ~225


def _mode(ctx: SecCtx, x: float, mode: GameMode, y: float = GROUND) -> None:
    ctx.b.mode_portal(x, mode, y=y)


def _speed(ctx: SecCtx, x: float, speed: Speed, y: float = GROUND) -> None:
    ctx.b.speed_portal(x, speed, y=y)


def _ceil_row(ctx: SecCtx, x0: float, x1: float, *, y: float = CEIL,
              color: int | None = C_SOL) -> None:
    ctx.b.block_row(x0, x1, y, color=color)


def _hang_spikes(ctx: SecCtx, x0: float, x1: float, *, y: float,
                 count: int | None = None, color: int | None = C_HAZ) -> None:
    ctx.b.spikes_row(x0, x1, y=y, count=count, color=color, flip_y=True)


# ==========================================================================
# intro - bars 0-8, cube, 1x
# ==========================================================================


def build_intro(ctx: SecCtx) -> None:
    b = ctx.b
    b.mode_portal(ctx.x0, GameMode.CUBE, y=GROUND)
    # bar 1: first single spike, dead on the downbeat of bar 1
    ctx.spike(ctx.beat_x(4))
    # bar 2: two spikes (one jump)
    ctx.spike(ctx.beat_x(8), count=2)
    # bar 3: orb-assisted hop over a 3-wide cluster
    b.orb(ctx.beat_x(11), 60, "yellow")
    ctx.spike(ctx.beat_x(12), count=2)
    # bar 4-5: rhythm - spike on every beat, one jump each
    for k in range(4):
        ctx.spike(ctx.beat_x(16 + k * 2))
    # bar 6: two ground spikes plus one floating spike - the player must jump
    # early and land short, so it reads as the first real timing check
    ctx.spike(ctx.beat_x(23.5), count=2)
    ctx.spike(ctx.beat_x(25.5), count=2)
    # bar 7: pad launch over a long spike field (the intro's one hard hitter)
    b.pad(ctx.beat_x(27), GROUND, "yellow")
    ctx.spike(ctx.beat_x(28.5), count=3)
    # bar 8 is the ship portal in the next section; leave a clean runway
    b.mark("intro_end", ctx.x1)


# ==========================================================================
# build - bars 8-15, cube into ship, 2x
# ==========================================================================


def build_build(ctx: SecCtx) -> None:
    b = ctx.b
    _speed(ctx, ctx.x0, Speed.FAST, y=GROUND)
    _mode(ctx, ctx.x0, GameMode.SHIP, y=GROUND)
    # bar 8: open entry (no lower wall) so the ship can rise out of the ground
    _ceil_row(ctx, ctx.beat_x(0), ctx.beat_x(4), y=CEIL)
    # bars 9-14: six pinches, one per bar, alternating high and low
    for i in range(6):
        bar = 1 + i
        centre = 150.0 if i % 2 == 0 else 270.0
        P.flight_pinch(ctx, ctx.bar_x(bar), gap=GAP_SHIP, centre=centre,
                       color=C_SOL)
    # bar 15 is the next section's bar line; the lower wall stops early
    _ceil_row(ctx, ctx.bar_x(6.0), ctx.x1, y=CEIL)


# ==========================================================================
# drop1 - bars 15-24, ship, 2x
# ==========================================================================


def build_drop1(ctx: SecCtx) -> None:
    b = ctx.b
    _mode(ctx, ctx.x0, GameMode.SHIP, y=GROUND)
    # bars 15-17: open entry then a rising floor
    _ceil_row(ctx, ctx.x0, ctx.bar_x(2.0), y=CEIL)
    b.block_row(ctx.bar_x(2.0), ctx.x1, FLOAT_FLOOR, color=C_SOL)
    # a pinch on every bar, then every half bar in the last stretch
    centres = [210, 150, 270, 210, 150, 210, 270, 210]
    for i, c in enumerate(centres[:6]):
        P.flight_pinch(ctx, ctx.bar_x(2.5 + i), gap=GAP_SHIP, centre=c,
                       color=C_SOL)
    for i in range(4):
        c = 165.0 if i % 2 else 285.0
        P.flight_pinch(ctx, ctx.bar_x(8.5 + i * 0.5), gap=GAP_SHIP, centre=c,
                       color=C_SOL)
    # a saw in the slot as the readable "hard hitter"
    b.hazard(ctx.bar_x(7.6), 210.0, obj=Obj.SAW_MEDIUM, w=60, h=60,
             color=C_HAZ, groups=(b.group("hazard_moving"),))


# ==========================================================================
# drop1b - bars 24-30, UFO, 2x
# ==========================================================================


def build_drop1b(ctx: SecCtx) -> None:
    b = ctx.b
    _mode(ctx, ctx.x0, GameMode.UFO, y=GROUND)
    _ceil_row(ctx, ctx.x0, ctx.x1, y=CEIL)
    # open entry (1 bar), then the lower wall
    b.block_row(ctx.bar_x(1.0), ctx.x1, FLOAT_FLOOR, color=C_SOL)
    # UFO gaps are wider than the ship's; one per beat from bar 2
    for i in range(16):
        c = 150.0 + 120.0 * (1 + math.sin(i * 0.9))
        P.flight_pinch(ctx, ctx.bar_x(2.0 + i * 0.25), gap=GAP_UFO, centre=c,
                       color=C_SOL)
    # two ceiling saws to read as the section's spike
    for i in range(2):
        b.hazard(ctx.bar_x(4.0 + i * 2.0), CEIL - 45.0, obj=Obj.SAW_SMALL,
                 w=45, h=45, color=C_HAZ, flip_y=False)


# ==========================================================================
# fill - bars 30-32, wave, 2x
# ==========================================================================


def build_fill(ctx: SecCtx) -> None:
    b = ctx.b
    _mode(ctx, ctx.x0, GameMode.WAVE, y=GROUND)
    _ceil_row(ctx, ctx.x0, ctx.x1, y=CEIL)
    # two bars of tight but straight wave corridor: readable, no weaving yet
    b.block_row(ctx.x0, ctx.x1, FLOAT_FLOOR, color=C_SOL)
    P.wave_tunnel(ctx, ctx.x0, ctx.x1, gap=GAP_WAVE,
                  centre_fn=lambda t: 210.0, channel=C_SOL,
                  ceiling_y=CEIL)


# ==========================================================================
# drop2 - bars 32-40, wave, 2x
# ==========================================================================


def build_drop2(ctx: SecCtx) -> None:
    b = ctx.b
    _mode(ctx, ctx.x0, GameMode.WAVE, y=GROUND)
    _ceil_row(ctx, ctx.x0, ctx.x1, y=CEIL)
    b.block_row(ctx.x0, ctx.x1, FLOAT_FLOOR, color=C_SOL)
    # four two-bar weaving tunnels; the weave follows the melody
    for i in range(4):
        a = ctx.bar_x(i * 2.0)
        z = ctx.bar_x((i + 1) * 2.0)
        amp = 90.0 if i % 2 == 0 else 120.0
        phase = 0.0 if i % 2 == 0 else math.pi
        P.wave_tunnel(
            ctx, a, z, gap=GAP_WAVE,
            centre_fn=lambda t, amp=amp, phase=phase:
                225.0 + amp * math.sin(2 * math.pi * t + phase),
            channel=C_SOL, ceiling_y=CEIL)
    # the section's hard hitter: one 4-block pinch in the last bar
    P.flight_pinch(ctx, ctx.bar_x(7.5), gap=GAP_WAVE * 0.85, centre=225.0,
                   color=C_SOL)


# ==========================================================================
# drop2b - bars 40-48, robot, 2x
# ==========================================================================


def build_drop2b(ctx: SecCtx) -> None:
    b = ctx.b
    _mode(ctx, ctx.x0, GameMode.ROBOT, y=GROUND)
    # clean runway for the first bar (robot lands out of the wave)
    b.mark("robot_runway", ctx.bar_x(1.0))
    # bars 41-47: spike fields cleared with hold-jumps, one per beat
    for i in range(14):
        x = ctx.bar_x(1.5 + i * 0.5)
        n = 2 + (i % 2)
        ctx.spike(x, count=n)
    # two pads that launch the robot over the tallest fields
    b.pad(ctx.bar_x(3.0), GROUND, "yellow")
    b.pad(ctx.bar_x(6.0), GROUND, "pink")
    # two floating spikes over the middle of the section (a short-jump read)
    b.hazard(ctx.bar_x(5.0), 90.0, color=C_HAZ)
    b.hazard(ctx.bar_x(5.25), 90.0, color=C_HAZ)


# ==========================================================================
# groove - bars 48-61, ball then spider, 1x
# ==========================================================================


def build_groove(ctx: SecCtx) -> None:
    b = ctx.b
    _speed(ctx, ctx.x0, Speed.NORMAL, y=GROUND)
    _mode(ctx, ctx.x0, GameMode.BALL, y=GROUND)
    _ceil_row(ctx, ctx.x0, ctx.bar_x(6.5), y=CEIL)
    # ball: alternate ground and ceiling spikes, flip on the beat
    for i in range(12):
        x = ctx.bar_x(0.75 + i * 0.5)
        if i % 2 == 0:
            ctx.spike(x, count=1 + (i % 2))
        else:
            _hang_spikes(ctx, x - BLOCK / 2, x + BLOCK / 2, y=CEIL - 30.0,
                         count=2)
    # spider: platforms with spikes between (bars 55-60)
    _mode(ctx, ctx.bar_x(6.5), GameMode.SPIDER, y=GROUND)
    for i in range(6):
        a = ctx.bar_x(7.0 + i * 0.6)
        b.block_row(a, a + BLOCK * 1.5, 105, color=C_SOL)
        ctx.spike(a + BLOCK * 2.2, count=2)
    # a landing platform for the swing portal at the end
    b.block_row(ctx.bar_x(11.5), ctx.x1, FLOAT_FLOOR, color=C_SOL)


# ==========================================================================
# break - bars 61-63, mini + dual, 2x  (the track's only real dip)
# ==========================================================================


def build_break(ctx: SecCtx) -> None:
    b = ctx.b
    _speed(ctx, ctx.x0, Speed.FAST, y=GROUND)
    _mode(ctx, ctx.x0, GameMode.CUBE, y=GROUND)
    b.size_portal(ctx.x0, True, y=GROUND)
    b.dual_portal(ctx.bar_x(0.5), True, y=GROUND)
    # deliberately empty: a two-bar breather with a wide corridor and no
    # hazards, so the mascot scene behind the player can be read
    b.block_row(ctx.bar_x(1.0), ctx.x1, FLOAT_FLOOR, color=C_SOL)
    b.dual_portal(ctx.x1, False, y=GROUND)
    b.size_portal(ctx.x1, False, y=GROUND)


# ==========================================================================
# build2 - bars 63-66, swing, 2x
# ==========================================================================


def build_build2(ctx: SecCtx) -> None:
    b = ctx.b
    _mode(ctx, ctx.x0, GameMode.SWING, y=GROUND)
    _ceil_row(ctx, ctx.x0, ctx.x1, y=CEIL)
    b.block_row(ctx.bar_x(0.75), ctx.x1, FLOAT_FLOOR, color=C_SOL)
    # three climbing pinches, one per half bar
    for i in range(6):
        c = 150.0 + 120.0 * (1 + math.sin(i * 0.8))
        P.flight_pinch(ctx, ctx.bar_x(0.75 + i * 0.375), gap=GAP_SWING,
                       centre=c, color=C_SOL)


# ==========================================================================
# final - bars 66-79, cube 3x with ship and wave sub-sections
# ==========================================================================


def build_final(ctx: SecCtx) -> None:
    b = ctx.b
    _speed(ctx, ctx.x0, Speed.VERY_FAST, y=GROUND)
    _mode(ctx, ctx.x0, GameMode.CUBE, y=GROUND)
    # bars 66-69: cube at 3x. Clusters are at most 2 wide at this speed
    for i in range(8):
        ctx.spike(ctx.bar_x(0.75 + i * 0.5), count=1 + (i % 2))
    b.orb(ctx.bar_x(4.4), 75, "yellow")
    ctx.spike(ctx.bar_x(4.9), count=2)
    # brief 4x burst (bars 70-71): a straight corridor, nothing to dodge
    _speed(ctx, ctx.bar_x(4.0), Speed.SUPER_FAST, y=GROUND)
    b.block_row(ctx.bar_x(4.5), ctx.bar_x(5.9), 105, color=C_SOL)
    ctx.spike(ctx.bar_x(5.0), count=1)
    _speed(ctx, ctx.bar_x(6.0), Speed.VERY_FAST, y=GROUND)
    # bars 72-75: ship interlude on the beat
    _mode(ctx, ctx.bar_x(6.0), GameMode.SHIP, y=GROUND)
    _ceil_row(ctx, ctx.bar_x(6.0), ctx.bar_x(10.0), y=CEIL)
    b.block_row(ctx.bar_x(7.0), ctx.bar_x(10.0), FLOAT_FLOOR, color=C_SOL)
    for i in range(6):
        c = 165.0 if i % 2 else 285.0
        P.flight_pinch(ctx, ctx.bar_x(7.25 + i * 0.5), gap=GAP_SHIP,
                       centre=c, color=C_SOL)
    # bars 76-79: the closing wave run, then the cube portal home
    _mode(ctx, ctx.bar_x(10.0), GameMode.WAVE, y=GROUND)
    _ceil_row(ctx, ctx.bar_x(10.0), ctx.x1, y=CEIL)
    b.block_row(ctx.bar_x(10.5), ctx.x1, FLOAT_FLOOR, color=C_SOL)
    for i in range(3):
        a = ctx.bar_x(10.5 + i * 0.9)
        z = ctx.bar_x(11.4 + i * 0.9)
        P.wave_tunnel(ctx, a, z, gap=GAP_WAVE,
                      centre_fn=lambda t: 225.0 + 75.0 * math.sin(4 * math.pi * t),
                      channel=C_SOL, ceiling_y=CEIL)
    _mode(ctx, ctx.x1, GameMode.CUBE, y=GROUND)


# ==========================================================================
# outro - bars 79-94, cube, 1x
# ==========================================================================


def build_outro(ctx: SecCtx) -> None:
    b = ctx.b
    _speed(ctx, ctx.x0, Speed.NORMAL, y=GROUND)
    _mode(ctx, ctx.x0, GameMode.CUBE, y=GROUND)
    # one last clean jump on the downbeat, then open runway to the end wall
    ctx.spike(ctx.beat_x(4), count=2)
    ctx.spike(ctx.beat_x(12))
    b.mark("outro_open", ctx.beat_x(16))
    b.mark("level_end", ctx.x1)


# ==========================================================================
# registry
# ==========================================================================

SECTIONS = {
    "intro": build_intro,
    "build": build_build,
    "drop1": build_drop1,
    "drop1b": build_drop1b,
    "fill": build_fill,
    "drop2": build_drop2,
    "drop2b": build_drop2b,
    "groove": build_groove,
    "break": build_break,
    "build2": build_build2,
    "final": build_final,
    "outro": build_outro,
}
