"""Phase B: Geometry Dash trigger construction.

Every trigger property key used here was verified against
``data/prop_table.csv``; nothing is invented. Trigger objects are placed like
normal objects but carry a target group / channel instead of geometry.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import gamedata as gd
from .level import Level
from .model import LevelObject

P = gd.Prop


@dataclass
class Trigger:
    """A trigger object plus bookkeeping about what it targets."""

    obj: LevelObject
    kind: str


@dataclass
class TriggerSet:
    """Collects triggers so they can be emitted in a stable, readable order."""

    level: Level
    triggers: list[Trigger] = field(default_factory=list)

    def _add(self, kind: str, obj: LevelObject) -> LevelObject:
        self.level.add(obj)
        self.triggers.append(Trigger(obj, kind))
        return obj

    def move(self, x: float, y: float, target_group: int, dx: float, dy: float,
             duration: float = 1.0, easing: gd.Easing = gd.Easing.IN_OUT,
             ease_rate: float = 2.0) -> LevelObject:
        o = LevelObject(gd.Obj.TR_MOVE, x, y)
        o.set(P.DURATION, duration).set(P.MOVE_X, dx).set(P.MOVE_Y, dy)
        o.set(P.EASING, int(easing)).set(P.EASE_RATE, ease_rate)
        o.set(P.TARGET_ID, target_group)
        return self._add("move", o)

    def rotate(self, x: float, y: float, target_group: int, degrees: float,
               duration: float = 1.0, easing: gd.Easing = gd.Easing.IN_OUT,
               center_group: int | None = None, lock: bool = True,
               ease_rate: float = 2.0) -> LevelObject:
        o = LevelObject(gd.Obj.TR_ROTATE, x, y)
        o.set(P.DURATION, duration).set(P.DEGREES, degrees)
        o.set(P.EASING, int(easing)).set(P.EASE_RATE, ease_rate)
        o.set(P.TARGET_ID, target_group)
        if lock:
            o.set(P.LOCK_ROTATION, 1)
        if center_group is not None:
            o.set(P.CENTER_ID, center_group)
        return self._add("rotate", o)

    def alpha(self, x: float, y: float, target_group: int, opacity: float,
              duration: float = 0.5) -> LevelObject:
        o = LevelObject(gd.Obj.TR_ALPHA, x, y)
        o.set(P.DURATION, duration).set(P.OPACITY, opacity)
        o.set(P.TARGET_ID, target_group)
        return self._add("alpha", o)

    def pulse(self, x: float, y: float, *, target_type: gd.PulseTarget,
              target_id: int, r: int, g: int, b: int,
              fade_in: float = 0.0, hold: float = 0.0, fade_out: float = 0.0,
              exclusive: bool = False) -> LevelObject:
        o = LevelObject(gd.Obj.TR_PULSE, x, y)
        o.set(P.RED, r).set(P.GREEN, g).set(P.BLUE, b)
        o.set(P.FADE_IN, fade_in).set(P.HOLD, hold).set(P.FADE_OUT, fade_out)
        o.set(P.TARGET_TYPE, int(target_type)).set(P.TARGET_ID, target_id)
        if exclusive:
            o.set(P.EXCLUSIVE, 1)
        return self._add("pulse", o)

    def color(self, x: float, y: float, channel: int, r: int, g: int, b: int,
              duration: float = 0.5, blending: bool = False,
              opacity: float = 1.0) -> LevelObject:
        o = LevelObject(gd.Obj.TR_COLOR, x, y)
        o.set(P.RED, r).set(P.GREEN, g).set(P.BLUE, b)
        o.set(P.DURATION, duration).set(P.CHANNEL, channel)
        o.set(P.OPACITY, opacity)
        if blending:
            o.set(P.BLENDING, 1)
        return self._add("color", o)

    def toggle(self, x: float, y: float, group: int,
               activate: bool = True) -> LevelObject:
        o = LevelObject(gd.Obj.TR_TOGGLE, x, y)
        o.set(P.TARGET_ID, group).set(P.ACTIVATE_GROUP, 1 if activate else 0)
        return self._add("toggle", o)

    def spawn(self, x: float, y: float, group: int, delay: float = 0.0,
              ordered: bool = True) -> LevelObject:
        o = LevelObject(gd.Obj.TR_SPAWN, x, y)
        o.set(P.TARGET_ID, group).set(P.SPAWN_DELAY, delay)
        if ordered:
            o.set(441, 1)
        o.set(102, 1)  # disable preview
        return self._add("spawn", o)

    def shake(self, x: float, y: float, duration: float = 0.5,
              strength: float = 5.0, interval: float = 0.05) -> LevelObject:
        o = LevelObject(gd.Obj.TR_SHAKE, x, y)
        o.set(P.DURATION, duration).set(P.SHAKE_STRENGTH, strength)

    def zoom(self, x: float, y: float, zoom: float, duration: float = 1.0,
             easing: gd.Easing = gd.Easing.IN_OUT) -> LevelObject:
        o = LevelObject(gd.Obj.TR_ZOOM_CAMERA, x, y)
        o.set(P.DURATION, duration).set(P.ZOOM, zoom).set(P.EASING, int(easing))
        return self._add("zoom", o)

    def offset_camera(self, x: float, y: float, dx: float, dy: float,
                      duration: float = 1.0,
                      easing: gd.Easing = gd.Easing.IN_OUT) -> LevelObject:
        o = LevelObject(gd.Obj.TR_OFFSET_CAMERA, x, y)
        o.set(P.MOVE_X, dx).set(P.MOVE_Y, dy).set(P.DURATION, duration)
        o.set(P.EASING, int(easing))
        return self._add("offset_camera", o)

    def follow(self, x: float, y: float, target_group: int, mod_x: float = 1.0,
               mod_y: float = 1.0, duration: float = 1.0) -> LevelObject:
        o = LevelObject(gd.Obj.TR_FOLLOW, x, y)
        o.set(P.DURATION, duration).set(P.TARGET_ID, target_group)
        o.set(P.FOLLOW_TARGET, target_group).set(P.MOD_X, mod_x)
        o.set(P.MOD_Y, mod_y)
        return self._add("follow", o)

    def stop(self, x: float, y: float, target_group: int,
             mode: int = 0) -> LevelObject:
        o = LevelObject(gd.Obj.TR_STOP, x, y)
        o.set(P.TARGET_ID, target_group).set(P.STOP_MODE, mode)
        return self._add("stop", o)

    def touch(self, x: float, y: float, group: int, hold: bool = True,
              dual: bool = False) -> LevelObject:
        o = LevelObject(gd.Obj.TR_TOUCH, x, y)
        o.set(P.TARGET_ID, group)
        o.set(81, 1 if hold else 0)
        o.set(82, int(gd.TouchMode.HOLD if hold else gd.TouchMode.TOGGLE))
        if dual:
            o.set(89, 1)
        return self._add("touch", o)

    def animate(self, x: float, y: float, target_group: int,
                animation_id: int = 0) -> LevelObject:
        o = LevelObject(gd.Obj.TR_ANIMATE, x, y)
        o.set(P.TARGET_ID, target_group).set(P.ANIMATION_ID, animation_id)
        return self._add("animate", o)

    def bg_effect(self, x: float, y: float, enable: bool = True) -> LevelObject:
        obj = gd.Obj.TR_BG_EFFECT_ON if enable else gd.Obj.TR_BG_EFFECT_OFF
        return self._add("bg_effect", LevelObject(obj, x, y))

    def on_death(self, x: float, y: float, target_group: int) -> LevelObject:
        o = LevelObject(gd.Obj.TR_ON_DEATH, x, y)
        o.set(P.TARGET_ID, target_group)
        return self._add("on_death", o)

    def count(self, x: float, y: float, item_id: int, count: int,
              target_group: int, multi: bool = False) -> LevelObject:
        o = LevelObject(gd.Obj.TR_COUNT, x, y)
        o.set(P.ITEM_ID, item_id).set(P.COUNT, count)
        o.set(P.TARGET_ID, target_group).set(P.ACTIVATE_GROUP, 1)
        if multi:
            o.set(104, 1)
        return self._add("count", o)

    def summary(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for t in self.triggers:
            out[t.kind] = out.get(t.kind, 0) + 1
        return out

        o.set(P.SHAKE_INTERVAL, interval)
        return self._add("shake", o)
