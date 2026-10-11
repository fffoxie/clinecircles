"""Phase C: decoration orchestration.

Places the surreal environments, the CLINE mascot, and the colour/pulse
triggers that drive them. Everything is grouped so Phase D can animate it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import gamedata as gd
from ..level import Level
from ..music import Timeline
from ..triggers import TriggerSet
from . import palette as PAL
from . import robot as R
from . import shapes as SH

B = 30.0


@dataclass
class DecorContext:
    level: Level
    ts: TriggerSet
    tl: Timeline
    groups: R.RobotGroups
    z: dict[str, list[int]] = field(default_factory=dict)

    def group(self, name: str) -> int:
        g = self.level.next_group_id(400)
        self.z.setdefault(name, []).append(g)
        return g


@dataclass
class DecorStats:
    objects: int = 0
    per_section: dict[str, int] = field(default_factory=dict)


def _robot_style(pal: PAL.Palette, z: int = -2) -> R.RobotStyle:
    return R.RobotStyle(body_channel=PAL.CH_ROBOT,
                        eye_channel=PAL.CH_ROBOT_EYE,
                        pupil_channel=PAL.CH_ROBOT_PUPIL,
                        accent_channel=PAL.CH_ACCENT, z_layer=z)


def _beat_move(ts: TriggerSet, x: float, y: float, group: int, dx: float,
               dy: float, duration: float) -> None:
    ts.move(x, y, group, dx, dy, duration=duration,
            easing=gd.Easing.SINE_IN_OUT)


def animate_robot_bounce(ts: TriggerSet, x: float, y: float, group: int,
                         beats: int, beat_s: float, height: float = 22.0,
                         tilt: float = 8.0) -> None:
    """A little dance: alternating up/down moves plus head tilt on the beat."""
    for i in range(beats):
        bx = x + i * beat_s * 0.0  # triggers are placed at their own x
        up = height if i % 2 == 0 else -height * 0.6
        _beat_move(ts, x + i * 40, y, group, 0, up, beat_s * 0.9)
        ts.rotate(x + i * 40, y, group, tilt if i % 2 == 0 else -tilt,
                  duration=beat_s * 0.9, easing=gd.Easing.SINE_IN_OUT)


def decorate_intro(ctx: DecorContext, x0: float, x1: float) -> int:
    lv, ts, tl, g = ctx.level, ctx.ts, ctx.tl, ctx.groups
    n = 0
    # layered background rings that read as depth
    for i, x in enumerate(range(int(x0), int(x1), 900)):
        SH.concentric_rings(lv, x, 300 + (i % 3) * 120, count=3, base=1.2,
                            channel=PAL.CH_DECO, groups=[g.aura], z=-5)
        n += 3
    # a few watching eyes that blink via alpha triggers
    for i, x in enumerate(range(int(x0) + 400, int(x1), 1400)):
        eye_g = ctx.group(f"intro_eye_{i}")
        SH.giant_eye(lv, x, 420, 1.6, ring=PAL.CH_DECO2, iris=PAL.CH_DECO,
                     pupil=PAL.CH_EYE, groups=[eye_g], z=-4)
        ts.alpha(x, 90, eye_g, 0.0, duration=0.18)
        ts.alpha(x + 220, 90, eye_g, 1.0, duration=0.18)
        n += 3
    # the mascot dances through the buildup
    for i in range(4):
        rx = x0 + 900 + i * 1000
        R.build_robot(lv, rx, 210, _robot_style(PAL.P_INTRO), g, scale=1.15)
        n += 16
        animate_robot_bounce(ts, rx, 210, g.root, beats=4,
                             beat_s=tl.track.beat_s, height=24.0)
    # gentle parallax drift on the whole robot group
    ts.move(x0, 60, g.root, (x1 - x0) * 0.06, 40, duration=tl.track.bar_s * 12,
            easing=gd.Easing.SINE_IN_OUT)
    return n


def decorate_drop1(ctx: DecorContext, x0: float, x1: float) -> int:
    lv, ts, tl, g = ctx.level, ctx.ts, ctx.tl, ctx.groups
    n = 0
    # giant eyes sweeping past - the "watching" motif of the drop
    eye_g = ctx.group("drop1_eyes")
    SH.eye_row(lv, x0 + 300, x1 - 300, 300, count=7, size=1.8,
               ring=PAL.CH_DECO2, iris=PAL.CH_DECO, pupil=PAL.CH_EYE,
               groups=[eye_g], z=-4)
    n += 21
    ts.move(x0, 60, eye_g, 240, -60, duration=tl.track.bar_s * 8,
            easing=gd.Easing.SINE_IN_OUT)
    # jagged teeth along the ceiling
    tooth_g = ctx.group("drop1_teeth")
    SH.tooth_wall(lv, x0, x1, 520, count=26, channel=PAL.CH_TEETH,
                  groups=[tooth_g], size=0.6, z=-1)
    n += 26
    # spirals + glitch tearing
    for i, x in enumerate(range(int(x0) + 500, int(x1), 1100)):
        SH.spiral(lv, x, 240, turns=2.2, radius=170, count=18,
                  channel=PAL.CH_DECO2, groups=[g.aura], z=-4)
        n += 18
    SH.glitch_strips(lv, x0, x1, 260, count=18, channel=PAL.CH_GLITCH,
                     groups=[g.aura], z=3, seed=11)
    n += 18
    return n


def decorate_breakdown(ctx: DecorContext, x0: float, x1: float) -> int:
    lv, ts, g = ctx.level, ctx.ts, ctx.groups
    n = 0
    # one enormous uncanny eye dominating the quiet section
    big = ctx.group("break_eye")
    SH.giant_eye(lv, (x0 + x1) / 2, 360, 7.5, ring=PAL.CH_DECO2,
                 iris=PAL.CH_DECO, pupil=PAL.CH_EYE, groups=[big], z=-5)
    n += 3
    ts.rotate((x0 + x1) / 2, 60, big, 360, duration=9.0,
              easing=gd.Easing.SINE_IN_OUT)
    # bone-white spiked rings, deliberately unsettling
    for i, x in enumerate(range(int(x0) + 300, int(x1), 700)):
        SH.concentric_rings(lv, x, 200, count=4, base=0.9,
                            channel=PAL.CH_DECO, groups=[g.aura], z=-4)
        n += 4
    return n



def decorate_drop2(ctx: DecorContext, x0: float, x1: float) -> int:
    lv, ts, tl, g = ctx.level, ctx.ts, ctx.tl, ctx.groups
    n = 0
    # the mascot's angry form appears, bigger, watching from behind
    R.build_robot(lv, x0 + 700, 340, _robot_style(PAL.P_DROP2, z=-2), g,
                  scale=2.6, variant="angry")
    n += 16
    ts.move(x0, 60, g.root, 300, -80, duration=tl.track.bar_s * 8,
            easing=gd.Easing.SINE_IN_OUT)
    # closing maw
    maw_g = ctx.group("drop2_maw")
    for x in range(int(x0) + 600, int(x1), 1500):
        SH.maw(lv, x, 300, 210, count=14, channel=PAL.CH_TEETH,
               groups=[maw_g], z=-1)
        n += 14
        ts.rotate(x, 60, maw_g, 180, duration=tl.track.bar_s * 4,
                  easing=gd.Easing.SINE_IN_OUT)
    # impossible lattice architecture
    SH.lattice(lv, x0, x1, 60, rows=5, spacing=260, channel=PAL.CH_DECO,
               groups=[g.aura], z=-5, skew=18)
    n += int((x1 - x0) / 260) * 5
    SH.particle_field(lv, x0, x1, 300, count=40, channel=PAL.CH_DECO2,
                      groups=[g.aura], z=-4, seed=23)
    n += 40
    return n


def decorate_boss(ctx: DecorContext, x0: float, x1: float) -> int:
    lv, ts, tl, g = ctx.level, ctx.ts, ctx.tl, ctx.groups
    n = 0
    # THE CLINE BOSS: the mascot grown enormous, teeth bared
    R.build_robot(lv, x0 + 1200, 420, _robot_style(PAL.P_BOSS, z=-2), g,
                  scale=5.5, variant="angry")
    n += 16
    ts.move(x0, 60, g.root, (x1 - x0) * 0.5, -120,
            duration=tl.track.time_at_bar(40) - tl.track.time_at_bar(35),
            easing=gd.Easing.SINE_IN_OUT)
    ts.rotate(x0, 60, g.head, 12, duration=tl.track.bar_s * 2,
              easing=gd.Easing.SINE_IN_OUT)
    # teeth closing around the player corridor
    for x in range(int(x0) + 400, int(x1), 800):
        tg = ctx.group("boss_teeth")
        SH.tooth_wall(lv, x, x + 500, 560, count=10, channel=PAL.CH_TEETH,
                      groups=[tg], size=0.85, z=-1)
        n += 10
        ts.move(x, 60, tg, 0, -60, duration=tl.track.bar_s * 2,
                easing=gd.Easing.IN_OUT)
    for i in range(5):
        SH.concentric_rings(lv, x0 + 1200, 420, count=3, base=4.0 + i * 0.6,
                            channel=PAL.CH_DECO2, groups=[g.aura], z=-5)
        n += 3
    return n


def decorate_finale(ctx: DecorContext, x0: float, x1: float) -> int:
    lv, ts, tl, g = ctx.level, ctx.ts, ctx.tl, ctx.groups
    n = 0
    # the boss shrinks back to its cute form and waves
    R.build_robot(lv, (x0 + x1) / 2, 300, _robot_style(PAL.P_FINALE), g,
                  scale=2.0, variant="cute")
    n += 16
    ts.rotate((x0 + x1) / 2, 60, g.arm_r, -40, duration=tl.track.bar_s,
              easing=gd.Easing.SINE_IN_OUT)
    ts.rotate((x0 + x1) / 2 + 60, 60, g.arm_r, 40, duration=tl.track.bar_s,
              easing=gd.Easing.SINE_IN_OUT)
    for x in range(int(x0) + 200, int(x1), 500):
        SH._put(lv, SH.O_EXPAND_L, x, 300, channel=PAL.CH_DECO2,
                groups=[g.aura], scale=2.0, z=-4)
        n += 1
    SH.concentric_rings(lv, (x0 + x1) / 2, 300, count=6, base=2.5,
                        channel=PAL.CH_DECO, groups=[g.aura], z=-5)
    n += 6
    return n



# --------------------------------------------------------------------------
# Colour script
# --------------------------------------------------------------------------


def _colour_script(ctx: DecorContext,
                   section_x: dict[str, tuple[float, float]]) -> None:
    """Change the whole palette on each section's downbeat."""
    ts, tl = ctx.ts, ctx.tl
    for name, pal in PAL.SECTION_PALETTES.items():
        if name not in section_x:
            continue
        x, y = section_x[name][0], 60
        dur = tl.track.bar_s * 2
        for ch, fieldname in PAL._FIELDS.items():
            r, g, b = getattr(pal, fieldname)
            ts.color(x, y, ch, r, g, b, duration=dur)
        ts.color(x, y, int(gd.ColorChannel.BG), *pal.sky, duration=dur)
        ts.color(x, y, int(gd.ColorChannel.G1), *pal.ground, duration=dur)


def _span(build_result, name: str) -> tuple[float, float] | None:
    mapping = {
        "intro": ["intro"],
        "drop1": ["drop1_ship", "drop1_ufo"],
        "breakdown": ["breakdown_wave", "breakdown_ball_spider"],
        "drop2": ["drop2_robot", "drop2_swing"],
        "boss": ["boss_fight"],
        "finale": ["finale"],
    }
    xs = [build_result.section_x[n] for n in mapping.get(name, [])
          if n in build_result.section_x]
    if not xs:
        return None
    return (min(a for a, _ in xs), max(b for _, b in xs))


def decorate(build_result, *, palette_script: bool = True) -> DecorStats:
    """Run all Phase C decoration over a built level."""
    level = build_result.level
    tl: Timeline = build_result.timeline
    ts = TriggerSet(level)
    groups = R.allocate_groups(level)
    ctx = DecorContext(level=level, ts=ts, tl=tl, groups=groups)

    before = len(level.objects)
    stats = DecorStats()
    for name, fn in (
        ("intro", decorate_intro),
        ("drop1", decorate_drop1),
        ("breakdown", decorate_breakdown),
        ("drop2", decorate_drop2),
        ("boss", decorate_boss),
        ("finale", decorate_finale),
    ):
        span = _span(build_result, name)
        if span is None:
            continue
        stats.per_section[name] = fn(ctx, *span)

    if palette_script:
        PAL.apply_initial(level)
        _colour_script(ctx, build_result.section_x)

    stats.objects = len(level.objects) - before
    return stats
