"""The CLINE robot mascot, built to match the supplied model sheet.

Reference (rfimage/Gemini_Generated_Image_j83qx5j83qx5j83q.jpg) shows:
  * a rounded-SQUARE head, white/lavender, glowing
  * TWO TALL VERTICAL OVAL eyes (dark), the character's signature
  * a small round knob/antenna on top
  * angular 'ear' notches on both sides of the head
  * a rounded chest with a dark purple chest plate
  * dark purple ball joints at shoulders/elbows/knees
  * white limb segments and crescent claw hands
  * palette: white, lavender, mid purple, deep purple, near-black

Geometry Dash has no custom textures, so the mascot is composed from real GD
objects. Every part carries a group id so triggers can animate it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..level import Level
from ..model import LevelObject

# Verified object ids used by the mascot.
O_BLOCK_BEVEL = 890       # Beveled Block  (rounded square -> head/chest)
O_BLOCK_SQUARE = 1        # plain square   (eye slots, ear notches)
O_ROD_SHORT = 17          # limb segments
O_ROD_MED = 16
O_TINY_CIRCLE = 1764      # joints / knob / pupils
O_CIRCLE_RING = 51        # eye rims
O_QUARTER = 1838          # small quarter circle -> claw hands
O_SPLIT_XS = 1000         # small accents

# Palette from the model sheet.
C_WHITE = 0xF2EFFA
C_LAVENDER = 0xC9C2E8
C_PURPLE = 0x6B5B95
C_DEEP = 0x2E2745
C_ACCENT = 0x8F7FD4


@dataclass
class RobotGroups:
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
    """Colour channels for the mascot (resolved against the level palette)."""

    body_channel: int
    eye_channel: int
    pupil_channel: int
    accent_channel: int
    z_layer: int = -2


def _o(obj_id: int, x: float, y: float, *, groups, channel, sx: float = 1.0,
       sy: float | None = None, z: int = -2, rot: float | None = None):
    o = LevelObject(obj_id, x, y)
    o.color(channel)
    for g in groups:
        o.add_group(g)
    if sx != 1.0 or (sy is not None and sy != 1.0):
        o.set(128, sx)
        o.set(129, sx if sy is None else sy)
    o.z(z)
    if rot is not None:
        o.rot(rot)
    return o


def build_robot(level: Level, x: float, y: float, style: RobotStyle,
                groups: RobotGroups, *, scale: float = 1.0,
                variant: str = "cute") -> list[LevelObject]:
    """Emit a CLINE robot centred on (x, y). `y` is the head centre."""
    B = 30.0 * scale
    made: list[LevelObject] = []

    def add(o):
        made.append(o)
        level.add(o)

    root, head = groups.root, groups.head
    el, er, pl, pr = groups.eye_l, groups.eye_r, groups.pupil_l, groups.pupil_r
    ant, body = groups.antenna, groups.body
    al, ar, aura = groups.arm_l, groups.arm_r, groups.aura
    z = style.z_layer

    # ---- aura glow behind the whole character --------------------------
    add(_o(O_CIRCLE_RING, x, y - 0.15 * B, groups=[root, aura],
           channel=style.accent_channel, sx=3.4 * scale, z=z - 2))

    # ---- head: rounded square -----------------------------------------
    add(_o(O_BLOCK_BEVEL, x, y, groups=[root, head],
           channel=style.body_channel, sx=2.5 * scale, z=z))
    # ear notches (angular bumps either side)
    for sgn in (-1, 1):
        add(_o(O_BLOCK_SQUARE, x + sgn * 1.45 * B, y, groups=[root, head],
               channel=style.accent_channel, sx=0.55 * scale,
               sy=0.55 * scale, z=z - 1, rot=45))

    # ---- eyes: two TALL vertical ovals (signature feature) -------------
    eye_dx = 0.42 * B
    for sgn, eg, pg in ((-1, el, pl), (1, er, pr)):
        # dark rounded slot
        add(_o(O_BLOCK_BEVEL, x + sgn * eye_dx, y + 0.02 * B,
               groups=[root, head, eg], channel=style.pupil_channel,
               sx=0.62 * scale, sy=1.45 * scale, z=z + 1))
        # small highlight inside
        add(_o(O_TINY_CIRCLE, x + sgn * eye_dx - 0.06 * B, y + 0.28 * B,
               groups=[root, head, eg, pg], channel=style.eye_channel,
               sx=0.24 * scale, z=z + 2))

    # ---- antenna knob --------------------------------------------------
    add(_o(O_TINY_CIRCLE, x, y + 1.55 * B, groups=[root, head, ant],
           channel=style.body_channel, sx=0.85 * scale, z=z))

    # ---- mouth (expression) --------------------------------------------
    if variant == "cute":
        for i in range(3):
            add(_o(O_TINY_CIRCLE, x + (i - 1) * 0.20 * B, y - 0.62 * B,
                   groups=[root, head, groups.mouth],
                   channel=style.pupil_channel, sx=0.20 * scale, z=z + 1))
    else:
        for i in range(5):
            add(_o(O_BLOCK_SQUARE, x + (i - 2) * 0.24 * B, y - 0.66 * B,
                   groups=[root, head, groups.mouth], channel=style.eye_channel,
                   sx=0.30 * scale, sy=0.30 * scale, z=z + 1, rot=45))

    # ---- chest ---------------------------------------------------------
    add(_o(O_BLOCK_BEVEL, x, y - 1.85 * B, groups=[root, body],
           channel=style.body_channel, sx=1.7 * scale, z=z))
    add(_o(O_BLOCK_BEVEL, x, y - 1.95 * B, groups=[root, body],
           channel=style.accent_channel, sx=1.15 * scale, sy=0.9 * scale,
           z=z + 1))

    # ---- arms: shoulder joint, upper, elbow, forearm, claw -------------
    for sgn, ag in ((-1, al), (1, ar)):
        sh = (x + sgn * 1.15 * B, y - 1.55 * B)
        add(_o(O_TINY_CIRCLE, sh[0], sh[1], groups=[root, body, ag],
               channel=style.accent_channel, sx=0.42 * scale, z=z + 2))
        add(_o(O_ROD_SHORT, sh[0] + sgn * 0.10 * B, sh[1] - 0.55 * B,
               groups=[root, body, ag], channel=style.body_channel,
               sx=0.9 * scale, z=z + 1, rot=sgn * 12))
        el2 = (sh[0] + sgn * 0.22 * B, sh[1] - 1.05 * B)
        add(_o(O_TINY_CIRCLE, el2[0], el2[1], groups=[root, body, ag],
               channel=style.accent_channel, sx=0.38 * scale, z=z + 2))
        add(_o(O_ROD_SHORT, el2[0] + sgn * 0.10 * B, el2[1] - 0.55 * B,
               groups=[root, body, ag], channel=style.body_channel,
               sx=0.9 * scale, z=z + 1, rot=sgn * 6))
        add(_o(O_QUARTER, el2[0] + sgn * 0.16 * B, el2[1] - 1.05 * B,
               groups=[root, body, ag], channel=style.body_channel,
               sx=0.85 * scale, z=z + 2, rot=sgn * 150))

    # ---- legs ----------------------------------------------------------
    for sgn in (-1, 1):
        hip = (x + sgn * 0.48 * B, y - 2.55 * B)
        add(_o(O_TINY_CIRCLE, hip[0], hip[1], groups=[root, body],
               channel=style.accent_channel, sx=0.40 * scale, z=z + 2))
        add(_o(O_ROD_SHORT, hip[0], hip[1] - 0.55 * B, groups=[root, body],
               channel=style.body_channel, sx=0.95 * scale, z=z + 1))
        add(_o(O_TINY_CIRCLE, hip[0], hip[1] - 1.10 * B, groups=[root, body],
               channel=style.accent_channel, sx=0.36 * scale, z=z + 2))
        add(_o(O_ROD_SHORT, hip[0], hip[1] - 1.62 * B, groups=[root, body],
               channel=style.body_channel, sx=0.95 * scale, z=z + 1))
        add(_o(O_BLOCK_BEVEL, hip[0], hip[1] - 2.15 * B, groups=[root, body],
               channel=style.body_channel, sx=0.95 * scale, sy=0.55 * scale,
               z=z + 2))
    return made
