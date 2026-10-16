"""Trigger simulation: what the level looks like at level time ``t``.

This is a *model* of GD's trigger behaviour, not the engine. It implements the
parts that matter for looking at a render:

==============  ====================================================
trigger         modelled effect
==============  ====================================================
899  colour     channel RGB lerps to a new value over ``duration``
1007 alpha      group opacity lerps to a new value
901  move       group offset lerps from 0 to (dx, dy)
1346 rotate     group rotation lerps to ``degrees``
1006 pulse      channel/group RGB gets an additive pulse
1049 toggle     group becomes hidden / visible
1520 shake      camera shake amplitude over ``duration``
1913 zoom       camera zoom lerps to ``zoom``
1916 offset     camera offset lerps to (dx, dy)
==============  ====================================================

Deliberate simplifications, all documented:

* triggers are evaluated by a **linear scan of the triggers whose x is at or
  before the camera x**, in level-string order. GD evaluates them in the same
  order, so stacking matches.
* spawn-triggered groups (``62``) are not evaluated; anything meant to be
  spawned is drawn at its authored position.
* easing is approximated by a smoothstep for all easing ids except NONE, which
  is linear. This affects the *shape* of a lerp, never its endpoints.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .. import ids
from ..gamedata import Prop
from ..level import Level
from ..model import LevelObject

#: trigger object ids the simulator understands
COLOR = int(ids.Obj.TR_COLOR)
MOVE = int(ids.Obj.TR_MOVE)
PULSE = int(ids.Obj.TR_PULSE)
ALPHA = int(ids.Obj.TR_ALPHA)
TOGGLE = int(ids.Obj.TR_TOGGLE)
ROTATE = int(ids.Obj.TR_ROTATE)
SHAKE = int(ids.Obj.TR_SHAKE)
ZOOM = int(ids.Obj.TR_ZOOM_CAMERA)
OFFSET = int(ids.Obj.TR_OFFSET_CAMERA)
STOP = int(ids.Obj.TR_STOP)

TRIGGER_IDS = {COLOR, MOVE, PULSE, ALPHA, TOGGLE, ROTATE, SHAKE, ZOOM,
               OFFSET, STOP, int(ids.Obj.TR_SPAWN), int(ids.Obj.TR_ANIMATE),
               int(ids.Obj.TR_FOLLOW), int(ids.Obj.TR_TOUCH),
               int(ids.Obj.TR_COUNT), int(ids.Obj.TR_ON_DEATH),
               int(ids.Obj.TR_ENTER), int(ids.Obj.TR_START_POS),
               int(ids.Obj.TR_BG_EFFECT_ON), int(ids.Obj.TR_BG_EFFECT_OFF),
               int(ids.Obj.TR_RANDOM), int(ids.Obj.TR_STATIC_CAMERA),
               int(ids.Obj.TR_FOLLOW_PLAYER_Y), int(ids.Obj.TR_COLLISION),
               int(ids.Obj.TR_PICKUP), int(ids.Obj.TR_TRAIL_ON),
               int(ids.Obj.TR_TRAIL_OFF), int(ids.Obj.TR_ANIMATE_KEYFRAME),
               int(ids.Obj.TR_COLLISION_BLOCK)} | set(range(2900, 2930))


def _ease(t: float, easing: int) -> float:
    t = min(1.0, max(0.0, t))
    if easing == 0:                      # Easing.NONE
        return t
    return t * t * (3.0 - 2.0 * t)       # smoothstep approximation


@dataclass
class GroupState:
    dx: float = 0.0
    dy: float = 0.0
    rot: float = 0.0
    opacity: float = 1.0
    hidden: bool = False


@dataclass
class SceneState:
    """Resolved state of the level at one moment in time."""

    colors: dict[int, tuple[int, int, int]]
    color_opacity: dict[int, float]
    pulse: dict[int, tuple[float, float, float]] = field(default_factory=dict)
    groups: dict[int, GroupState] = field(default_factory=dict)
    shake: float = 0.0
    zoom: float = 1.0
    cam_dx: float = 0.0
    cam_dy: float = 0.0

    def colour(self, channel: int) -> tuple[int, int, int]:
        r, g, b = self.colors.get(channel, (255, 255, 255))
        pr, pg, pb = self.pulse.get(channel, (0.0, 0.0, 0.0))
        return (max(0, min(255, int(r + pr))), max(0, min(255, int(g + pg))),
                max(0, min(255, int(b + pb))))

    def group(self, g: int) -> GroupState:
        st = self.groups.get(g)
        if st is None:
            st = GroupState()
            self.groups[g] = st
        return st


def _g(obj: LevelObject, key: int, default=0.0) -> float:
    v = obj.get(key)
    if v is None or v == "":
        return float(default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return float(default)


def simulate(level: Level, triggers: list[LevelObject], t: float,
             tl) -> SceneState:
    """Resolve the level's appearance at level time ``t``.

    ``triggers`` must contain only trigger objects, in level-string order. A
    trigger fires when the player reaches its x, so its fire time is
    ``tl.time_at_x(trigger.x)``; effects then advance in *seconds*, which is
    what GD does.
    """
    st = SceneState(
        colors={ch: (c.r, c.g, c.b) for ch, c in level.colors.items()},
        color_opacity={ch: c.opacity for ch, c in level.colors.items()})
    for o in triggers:
        t0 = tl.time_at_x(o.x)
        if t0 > t:
            break
        oid = int(o.id)
        if oid == COLOR:
            ch = int(_g(o, Prop.CHANNEL, 0))
            dur = max(1e-6, _g(o, Prop.DURATION, 0.5))
            k = _ease((t - t0) / dur, int(_g(o, Prop.EASING, 0)))
            tgt = (int(_g(o, Prop.RED, 255)), int(_g(o, Prop.GREEN, 255)),
                   int(_g(o, Prop.BLUE, 255)))
            prev = st.colors.get(ch, tgt)
            st.colors[ch] = tuple(int(prev[i] + (tgt[i] - prev[i]) * k)
                                  for i in range(3))
            st.color_opacity[ch] = _g(o, Prop.OPACITY, 1.0)
        elif oid == ALPHA:
            g = int(_g(o, Prop.TARGET_ID, 0))
            dur = max(1e-6, _g(o, Prop.DURATION, 0.5))
            k = min(1.0, max(0.0, (t - t0) / dur))
            cur = st.group(g).opacity
            st.group(g).opacity = cur + (_g(o, Prop.OPACITY, 1.0) - cur) * k
        elif oid == TOGGLE:
            g = int(_g(o, Prop.TARGET_ID, 0))
            st.group(g).hidden = True
        elif oid == MOVE:
            g = int(_g(o, Prop.TARGET_ID, 0))
            dur = max(1e-6, _g(o, Prop.DURATION, 1.0))
            k = _ease((t - t0) / dur, int(_g(o, Prop.EASING, 0)))
            st.group(g).dx += _g(o, Prop.MOVE_X, 0.0) * k
            st.group(g).dy += _g(o, Prop.MOVE_Y, 0.0) * k
        elif oid == ROTATE:
            g = int(_g(o, Prop.TARGET_ID, 0))
            dur = max(1e-6, _g(o, Prop.DURATION, 1.0))
            k = _ease((t - t0) / dur, int(_g(o, Prop.EASING, 0)))
            st.group(g).rot += _g(o, Prop.DEGREES, 0.0) * k
        elif oid == PULSE:
            tgt_type = int(_g(o, Prop.TARGET_TYPE, 0))
            tgt = int(_g(o, Prop.TARGET_ID, 0))
            fi = _g(o, Prop.FADE_IN, 0.0)
            ho = _g(o, Prop.HOLD, 0.0)
            fo = _g(o, Prop.FADE_OUT, 0.0)
            dt = t - t0
            if dt < 0 or dt > fi + ho + fo:
                continue
            if dt < fi:
                k = dt / fi if fi > 0 else 1.0
            elif dt < fi + ho:
                k = 1.0
            else:
                k = 1.0 - ((dt - fi - ho) / fo if fo > 0 else 1.0)
            r, g, b = (_g(o, Prop.RED, 255), _g(o, Prop.GREEN, 255),
                       _g(o, Prop.BLUE, 255))
            key = tgt if tgt_type else -1
            if tgt_type == 0:
                st.pulse[key] = ((r - 255) * k, (g - 255) * k, (b - 255) * k)
            else:
                st.group(tgt).opacity = min(1.0, st.group(tgt).opacity + k)
        elif oid == SHAKE:
            dur = max(1e-6, _g(o, Prop.DURATION, 0.5))
            k = max(0.0, 1.0 - (t - t0) / dur)
            st.shake = max(st.shake, _g(o, Prop.SHAKE_STRENGTH, 0.0) * k)
        elif oid == ZOOM:
            dur = max(1e-6, _g(o, Prop.DURATION, 1.0))
            k = _ease((t - t0) / dur, int(_g(o, Prop.EASING, 0)))
            st.zoom += (_g(o, Prop.ZOOM, 1.0) - st.zoom) * k
        elif oid == OFFSET:
            dur = max(1e-6, _g(o, Prop.DURATION, 1.0))
            k = _ease((t - t0) / dur, int(_g(o, Prop.EASING, 0)))
            st.cam_dx += _g(o, Prop.MOVE_X, 0.0) * k
            st.cam_dy += _g(o, Prop.MOVE_Y, 0.0) * k
    return st
