"""The CLINE robot mascot.

No reference image was supplied with the repository, and Geometry Dash does not
allow custom textures, so the mascot is an **original interpretation** built
from real GD objects and made recognisable through proportion and behaviour:

* a very large round head (object 50) with two oversized glowing eyes (51),
* tiny pupils (1764) that can look around,
* a single antenna (rod 16) with a floating ball (1764),
* a small rounded body and stubby arms/legs (rods 15/16/17),
* a small "smile" arc of dots that can invert into jagged teeth.

Every part is tagged with a group so triggers can animate it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..level import Level
from ..model import LevelObject

O_CIRCLE_FILLED = 50     # Pulsing Filled Circle
O_CIRCLE_RING = 51       # Pulsing Circle
O_CIRCLE_LARGE = 497     # Large Pulsing Circle
O_TINY_CIRCLE = 1764     # Tiny Circle
O_ROD_SHORT = 17
O_ROD_MED = 16
O_ROD_TALL = 15
O_BLOCK_BEVEL = 890      # Beveled Block


@dataclass
class RobotGroups:
    """Group ids for each animatable part of the robot."""

    root: int
    head: int
    eye_l: int
    eye_r: int
    pupil_l: int
    pupil_r: int
    antenna: int
    body: int
    arm_l: int
    arm_r: int
    mouth: int
    aura: int

    def all(self) -> list[int]:
        return [self.root, self.head, self.eye_l, self.eye_r, self.pupil_l,
                self.pupil_r, self.antenna, self.body, self.arm_l, self.arm_r,
                self.mouth, self.aura]


def allocate_groups(level: Level, base: int = 100) -> RobotGroups:
    g = [level.next_group_id(base + i * 7) for i in range(12)]
    return RobotGroups(*g)


@dataclass
class RobotStyle:
    """Colour channels and z-layer for the mascot."""

    body_channel: int
    eye_channel: int
    pupil_channel: int
    accent_channel: int
    z_layer: int = -2


def _obj(obj_id: int, x: float, y: float, *,
         groups: list[int], channel: int, scale: float = 1.0,
         z: int = -2, rot: float | None = None) -> LevelObject:
    o = LevelObject(obj_id, x, y)
    o.color(channel)
    for g in groups:
        o.add_group(g)
    if scale != 1.0:
        o.scale(scale)
    o.z(z)
    if rot is not None:
        o.rot(rot)
    return o


def build_robot(level: Level, x: float, y: float, style: RobotStyle,
                groups: RobotGroups, *, scale: float = 1.0,
                variant: str = "cute") -> list[LevelObject]:
    """Emit a CLINE robot at (x, y). Returns the objects created.

    ``variant``: ``cute`` (happy), ``angry`` (boss teeth), ``glitch``.
    """
    B = 30.0 * scale
    made: list[LevelObject] = []

    def add(o: LevelObject) -> None:
        made.append(o)
        level.add(o)

    root, head, el, er = (groups.root, groups.head, groups.eye_l, groups.eye_r)
    pl, pr = groups.pupil_l, groups.pupil_r
    ant, body = groups.antenna, groups.body
    al, ar, mouth, aura = (groups.arm_l, groups.arm_r, groups.mouth,
                           groups.aura)
    z = style.z_layer

    add(_obj(O_CIRCLE_LARGE, x, y + 0.6 * B, groups=[root, aura],
             channel=style.accent_channel, scale=1.15 * scale, z=z - 1))

    # antenna
    add(_obj(O_ROD_MED, x, y + 2.35 * B, groups=[root, head, ant],
             channel=style.accent_channel, scale=scale, z=z))
    add(_obj(O_TINY_CIRCLE, x, y + 2.85 * B, groups=[root, head, ant],
             channel=style.eye_channel, scale=0.9 * scale, z=z))

    # head
    add(_obj(O_CIRCLE_FILLED, x, y + 1.15 * B, groups=[root, head],
             channel=style.body_channel, scale=2.4 * scale, z=z))

    # eyes
    eye_dx = 0.42 * B
    add(_obj(O_CIRCLE_RING, x - eye_dx, y + 1.30 * B, groups=[root, head, el],
             channel=style.eye_channel, scale=0.95 * scale, z=z + 1))
    add(_obj(O_CIRCLE_RING, x + eye_dx, y + 1.30 * B, groups=[root, head, er],
             channel=style.eye_channel, scale=0.95 * scale, z=z + 1))
    add(_obj(O_TINY_CIRCLE, x - eye_dx, y + 1.28 * B,
             groups=[root, head, el, pl], channel=style.pupil_channel,
             scale=0.42 * scale, z=z + 2))
    add(_obj(O_TINY_CIRCLE, x + eye_dx, y + 1.28 * B,
             groups=[root, head, er, pr], channel=style.pupil_channel,
             scale=0.42 * scale, z=z + 2))

    # mouth
    if variant == "cute":
        for i in range(5):
            t = (i - 2) / 2.0
            add(_obj(O_TINY_CIRCLE, x + t * 0.28 * B,
                     y + 0.78 * B + (0.09 * B if abs(t) < 1 else 0.03 * B),
                     groups=[root, head, mouth], channel=style.pupil_channel,
                     scale=0.30 * scale, z=z + 1))
    else:
        for i in range(6):
            t = (i - 2.5) / 2.5
            add(_obj(O_TINY_CIRCLE, x + t * 0.30 * B, y + 0.80 * B,
                     groups=[root, head, mouth], channel=style.eye_channel,
                     scale=0.34 * scale, z=z + 1, rot=45))

    # body
    add(_obj(O_BLOCK_BEVEL, x, y - 0.35 * B, groups=[root, body],
             channel=style.body_channel, scale=1.5 * scale, z=z))

    # arms
    add(_obj(O_ROD_SHORT, x - 0.95 * B, y - 0.20 * B,
             groups=[root, body, al], channel=style.accent_channel,
             scale=scale, rot=25, z=z))
    add(_obj(O_ROD_SHORT, x + 0.95 * B, y - 0.20 * B,
             groups=[root, body, ar], channel=style.accent_channel,
             scale=scale, rot=-25, z=z))

    # legs
    add(_obj(O_ROD_SHORT, x - 0.42 * B, y - 1.05 * B, groups=[root, body],
             channel=style.accent_channel, scale=scale, z=z))
    add(_obj(O_ROD_SHORT, x + 0.42 * B, y - 1.05 * B, groups=[root, body],
             channel=style.accent_channel, scale=scale, z=z))

    return made
