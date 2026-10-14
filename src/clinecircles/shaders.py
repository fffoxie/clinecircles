"""Geometry Dash 2.2 GPU shader triggers.

These are real post-processing effects applied by the engine (not faked with
2D objects), verified from ``data/object_table.csv`` (``ShaderGameObject``) and
``data/prop_table.csv`` (``trigger.shader.*``).

Shared property keys:
    10 FADE_TIME, 30 EASING, 85 EASE_RATE, 51 CENTER_ID, 71 TINT/REF CHANNEL,
    514 RELATIVE, 531 DISABLE_PREVIEW.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import gamedata as gd
from .level import Level
from .model import LevelObject

P = gd.Prop

# Verified shader object ids.
SHADER = {
    "options": 2904,
    "shockwave": 2905,
    "shockline": 2907,
    "glitch": 2909,
    "chromatic": 2910,
    "chromatic_glitch": 2911,
    "pixelate": 2912,
    "lens_circle": 2913,
    "radial_blur": 2914,
    "motion_blur": 2915,
    "bulge": 2916,
    "pinch": 2917,
    "grayscale": 2919,
    "sepia": 2920,
    "invert": 2921,
    "hue": 2922,
    "edit_color": 2923,
    "split_screen": 2924,
}


@dataclass
class ShaderSet:
    level: Level
    applied: list[tuple[str, LevelObject]] = field(default_factory=list)

    def _base(self, kind: str, x: float, y: float, fade: float,
              easing: gd.Easing, relative: bool) -> LevelObject:
        o = LevelObject(SHADER[kind], x, y)
        o.set(10, fade).set(30, int(easing)).set(85, 2.0)
        if relative:
            o.set(514, 1)
        return o

    def _emit(self, kind: str, o: LevelObject) -> LevelObject:
        self.level.add(o)
        self.applied.append((kind, o))
        return o

    # ------------------------------------------------------------------
    def glitch(self, x: float, y: float, strength: float = 1.0,
               speed: float = 1.0, slice_height: float = 10.0,
               fade: float = 0.4, easing: gd.Easing = gd.Easing.IN_OUT,
               relative: bool = False) -> LevelObject:
        o = self._base("glitch", x, y, fade, easing, relative)
        o.set(176, strength).set(175, speed).set(179, slice_height)
        return self._emit("glitch", o)

    def chromatic_glitch(self, x: float, y: float, strength: float = 1.0,
                         speed: float = 1.0, rgb_offset: float = 4.0,
                         line_thickness: float = 2.0, fade: float = 0.4,
                         easing: gd.Easing = gd.Easing.IN_OUT,
                         relative: bool = False) -> LevelObject:
        o = self._base("chromatic_glitch", x, y, fade, easing, relative)
        o.set(176, strength).set(175, speed)
        o.set(180, rgb_offset).set(179, line_thickness)
        return self._emit("chromatic_glitch", o)

    def chromatic(self, x: float, y: float, target_x: float = 6.0,
                  fade: float = 0.5,
                  easing: gd.Easing = gd.Easing.IN_OUT) -> LevelObject:
        o = self._base("chromatic", x, y, fade, easing, False)
        o.set(180, target_x)
        return self._emit("chromatic", o)

    def pixelate(self, x: float, y: float, target_x: float = 40.0,
                 fade: float = 0.4, relative: bool = False,
                 hard_edges: bool = True) -> LevelObject:
        o = self._base("pixelate", x, y, fade, gd.Easing.IN_OUT, relative)
        o.set(180, target_x)
        if hard_edges:
            o.set(515, 1)
        return self._emit("pixelate", o)

    def lens_circle(self, x: float, y: float, strength: float = 1.0,
                    size: float = 200.0, center_group: int | None = None,
                    tint_channel: int | None = None, fade: float = 0.6,
                    easing: gd.Easing = gd.Easing.IN_OUT) -> LevelObject:
        o = self._base("lens_circle", x, y, fade, easing, False)
        o.set(176, strength).set(179, size)
        if center_group is not None:
            o.set(51, center_group)
        if tint_channel is not None:
            o.set(71, tint_channel)
        return self._emit("lens_circle", o)

    def radial_blur(self, x: float, y: float, intensity: float = 1.0,
                    size: float = 120.0, center_group: int | None = None,
                    fade: float = 0.5) -> LevelObject:
        o = self._base("radial_blur", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(176, intensity).set(179, size)
        if center_group is not None:
            o.set(51, center_group)
        return self._emit("radial_blur", o)

    def bulge(self, x: float, y: float, amount: float = 1.0,
              radius: float = 100.0, center_group: int | None = None,
              fade: float = 0.6) -> LevelObject:
        o = self._base("bulge", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(176, amount).set(180, radius)
        if center_group is not None:
            o.set(51, center_group)
        return self._emit("bulge", o)

    def pinch(self, x: float, y: float, modifier: float = 1.0,
              radius: float = 100.0, center_group: int | None = None,
              fade: float = 0.6) -> LevelObject:
        o = self._base("pinch", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(179, modifier).set(512, radius)
        if center_group is not None:
            o.set(51, center_group)
        return self._emit("pinch", o)


    def hue(self, x: float, y: float, degrees: float = 90.0,
            fade: float = 0.5) -> LevelObject:
        o = self._base("hue", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(176, degrees)
        return self._emit("hue", o)

    def grayscale(self, x: float, y: float, target: float = 1.0,
                  fade: float = 0.5) -> LevelObject:
        o = self._base("grayscale", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(176, target)
        return self._emit("grayscale", o)

    def invert(self, x: float, y: float, target: float = 1.0,
               fade: float = 0.2) -> LevelObject:
        o = self._base("invert", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(176, target)
        return self._emit("invert", o)

    def shockwave(self, x: float, y: float, strength: float = 1.0,
                  speed: float = 1.0, size: float = 300.0,
                  fade: float = 0.6) -> LevelObject:
        o = self._base("shockwave", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(176, strength).set(175, speed).set(512, size)
        return self._emit("shockwave", o)

    def motion_blur(self, x: float, y: float, intensity: float = 1.0,
                    fade: float = 0.4) -> LevelObject:
        o = self._base("motion_blur", x, y, fade, gd.Easing.IN_OUT, False)
        o.set(176, intensity)
        return self._emit("motion_blur", o)

    def summary(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for kind, _ in self.applied:
            out[kind] = out.get(kind, 0) + 1
        return out
