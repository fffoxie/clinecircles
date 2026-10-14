"""Phase D: dramatic transitions, camera work, boss effects and endscreen.

Each transition combines several verified mechanisms so it reads as a real
transformation rather than a colour change:

* a giant eye whose pupil the camera dives through (lens-circle shader +
  radial blur + camera zoom/offset),
* the world rotating around the player (rotate triggers + bulge shader),
* the level collapsing to a point and expanding again (pinch shader + shake +
  shockwave),
* teeth closing around the corridor (moving tooth walls + shake),
* the mascot transforming into the boss (glitch/chromatic glitch + moves),
* an endscreen built from real Text objects (id 914).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field

from . import gamedata as gd
from . import shaders as SH
from .decoration import palette as PAL
from .decoration import shapes as SK
from .level import Level
from .model import LevelObject
from .triggers import TriggerSet

O_TEXT = 914
O_EXPAND_L = 1841


@dataclass
class EffectStats:
    objects: int = 0
    summary: dict[str, int] = field(default_factory=dict)
    transitions: list[str] = field(default_factory=list)

    def note(self, kind: str) -> None:
        self.summary[kind] = self.summary.get(kind, 0) + 1


def _text(level: Level, x: float, y: float, s: str, *, channel: int,
          scale: float, groups: list[int] | None = None,
          z: int = 4) -> LevelObject:
    o = LevelObject(O_TEXT, x, y)
    o.set(gd.Prop.TEXT_DATA, base64.b64encode(s.encode()).decode())
    o.color(channel)
    o.scale(scale)
    o.z(z)
    if groups:
        for g in groups:
            o.add_group(g)
    level.add(o)
    return o


# --------------------------------------------------------------------------
# Transitions
# --------------------------------------------------------------------------


def dive_through_pupil(level: Level, ts: TriggerSet, sh: SH.ShaderSet,
                       x: float, y: float, stats: EffectStats) -> None:
    """Camera dives into a giant eye's pupil and out into the next section."""
    g = level.next_group_id(900)
    SK.giant_eye(level, x, y, 9.0, ring=PAL.CH_DECO2, iris=PAL.CH_DECO,
                 pupil=PAL.CH_EYE, groups=[g], z=-5)
    SK.concentric_rings(level, x, y, count=5, base=10.0,
                        channel=PAL.CH_DECO, groups=[g], z=-6)
    stats.objects += 8

    sh.lens_circle(x - 120, y, strength=1.6, size=90.0, center_group=g,
                   fade=0.9, easing=gd.Easing.SINE_IN_OUT)
    sh.radial_blur(x + 60, y, intensity=1.4, size=160.0, center_group=g,
                   fade=0.7)
    ts.zoom(x - 120, y, 1.35, duration=1.2, easing=gd.Easing.IN_OUT)
    ts.zoom(x + 240, y, 1.0, duration=0.8, easing=gd.Easing.OUT)
    ts.shake(x + 60, y, duration=0.5, strength=6.0, interval=0.03)
    ts.alpha(x - 240, y, g, 0.0, duration=0.4)
    ts.alpha(x - 60, y, g, 1.0, duration=0.3)
    ts.alpha(x + 400, y, g, 0.0, duration=0.5)
    stats.note("transition_pupil")
    stats.transitions.append("dive_through_pupil")


def world_rotate(level: Level, ts: TriggerSet, x0: float, x1: float, y: float,
                 target_group: int, stats: EffectStats) -> None:
    """Rotate the environment around the player; gameplay stays readable."""
    ts.rotate(x0, y, target_group, 360, duration=(x1 - x0) / 320.0,
              easing=gd.Easing.NONE)
    sh = SH.ShaderSet(level)
    sh.bulge(x0, y, amount=0.5, radius=420.0, fade=1.2)
    stats.note("transition_rotate")
    stats.transitions.append("world_rotate")


def collapse_to_point(level: Level, ts: TriggerSet, x: float, y: float,
                      group: int, stats: EffectStats) -> None:
    """The world pinches into a point, shakes, then bursts back out."""
    sh = SH.ShaderSet(level)
    sh.pinch(x, y, modifier=1.2, radius=520.0, fade=1.1)
    sh.radial_blur(x + 30, y, intensity=1.8, size=260.0, fade=0.9)
    ts.move(x, y, group, 0, -140, duration=1.1, easing=gd.Easing.EXP_IN)
    ts.alpha(x + 80, y, group, 0.0, duration=0.35)
    ts.alpha(x + 140, y, group, 1.0, duration=0.35)
    ts.move(x + 140, y, group, 0, 140, duration=0.7,
            easing=gd.Easing.BACK_OUT)
    ts.shake(x, y, duration=0.9, strength=9.0, interval=0.025)
    sh.shockwave(x + 140, y, strength=1.4, speed=1.2, size=420.0, fade=0.8)
    stats.note("transition_collapse")
    stats.transitions.append("collapse_to_point")



def teeth_close(level: Level, ts: TriggerSet, x: float, y: float,
                stats: EffectStats) -> None:
    """Giant geometric teeth slam shut around the corridor."""
    top = level.next_group_id(900)
    bot = level.next_group_id(900)
    for i in range(14):
        xx = x - 210 + i * 30
        o = LevelObject(1764, xx, y + 260)
        o.color(PAL.CH_TEETH).scale(0.9).rot(45).z(-1).add_group(top)
        level.add(o)
        o2 = LevelObject(1764, xx, y - 200)
        o2.color(PAL.CH_TEETH).scale(0.9).rot(45).z(-1).add_group(bot)
        level.add(o2)
    stats.objects += 28
    ts.move(x, y, top, 0, -190, duration=0.55, easing=gd.Easing.BACK_IN)
    ts.move(x, y, bot, 0, 190, duration=0.55, easing=gd.Easing.BACK_IN)
    ts.move(x + 260, y, top, 0, 190, duration=0.45, easing=gd.Easing.BACK_OUT)
    ts.move(x + 260, y, bot, 0, -190, duration=0.45,
            easing=gd.Easing.BACK_OUT)
    ts.shake(x, y, duration=0.6, strength=7.0, interval=0.03)
    stats.note("transition_teeth")
    stats.transitions.append("teeth_close")


def boss_transform(level: Level, ts: TriggerSet, sh: SH.ShaderSet, x: float,
                   y: float, group: int, stats: EffectStats) -> None:
    """The cute mascot glitches and erupts into the giant boss."""
    sh.glitch(x, y, strength=1.6, speed=2.0, slice_height=14.0, fade=0.5)
    sh.chromatic_glitch(x + 30, y, strength=1.4, speed=2.4, rgb_offset=9.0,
                        fade=0.5)
    sh.invert(x + 60, y, target=1.0, fade=0.25)
    sh.shockwave(x + 90, y, strength=1.6, speed=1.4, size=520.0, fade=0.7)
    ts.move(x, y, group, 0, 26, duration=0.22, easing=gd.Easing.BACK_OUT)
    ts.rotate(x, y, group, 8, duration=0.22, easing=gd.Easing.SINE_IN_OUT)
    ts.move(x + 60, y, group, 0, -40, duration=0.5, easing=gd.Easing.EXP_IN)
    ts.shake(x, y, duration=1.0, strength=11.0, interval=0.02)
    stats.note("transition_boss")
    stats.transitions.append("boss_transform")


# --------------------------------------------------------------------------
# Endscreen
# --------------------------------------------------------------------------


def endscreen(level: Level, ts: TriggerSet, sh: SH.ShaderSet, x: float, y: float,
              stats: EffectStats) -> None:
    """A polished in-level endscreen (GD cannot author custom UI)."""
    g = level.next_group_id(950)
    _text(level, x, y + 150, "CLINE CIRCLES", channel=PAL.CH_TEXT,
          scale=0.9, groups=[g])
    _text(level, x, y + 60, "COMPLETE", channel=PAL.CH_ACCENT,
          scale=0.55, groups=[g])
    _text(level, x, y - 40, "an AI experiment - do not rate",
          channel=PAL.CH_DECO2, scale=0.30, groups=[g])
    stats.objects += 3

    for i in range(6):
        o = LevelObject(O_EXPAND_L, x - 120 + i * 60, y + 40)
        o.color(PAL.CH_DECO).scale(1.4 + i * 0.5).z(-4).add_group(g)
        level.add(o)
    SK.concentric_rings(level, x, y + 40, count=5, base=3.0,
                        channel=PAL.CH_DECO2, groups=[g], z=-5)
    stats.objects += 11

    ts.alpha(x - 260, y, g, 0.0, duration=0.01)
    ts.alpha(x - 60, y, g, 1.0, duration=0.9)
    ts.rotate(x, y, g, 6, duration=1.4, easing=gd.Easing.SINE_IN_OUT)
    sh.grayscale(x - 60, y, target=0.35, fade=1.2)
    sh.bulge(x, y + 40, amount=0.35, radius=500.0, fade=1.5)
    sh.chromatic(x + 40, y, target_x=3.0, fade=1.0)
    stats.note("endscreen")
    stats.transitions.append("endscreen")


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def apply_effects(build_result) -> EffectStats:
    """Run every Phase D effect over a decorated level."""
    res = build_result
    level = res.level
    ts = TriggerSet(level)
    sh = SH.ShaderSet(level)
    stats = EffectStats()
    sx = res.section_x
    before = len(level.objects)

    dive_through_pupil(level, ts, sh, sx["drop1_ship"][0] - 420, 320, stats)

    world_rotate(level, ts, sx["breakdown_wave"][0],
                 sx["breakdown_ball_spider"][1], 300,
                 level.next_group_id(900), stats)

    collapse_to_point(level, ts, sx["drop2_robot"][0] - 500, 300,
                      level.next_group_id(900), stats)
    boss_transform(level, ts, sh, sx["drop2_robot"][0] + 60, 340,
                   level.next_group_id(900), stats)

    teeth_close(level, ts, sx["boss_fight"][0] + 900, 260, stats)

    endscreen(level, ts, sh, sx["finale"][1] - 620, 300, stats)

    stats.objects = len(level.objects) - before
    return stats
