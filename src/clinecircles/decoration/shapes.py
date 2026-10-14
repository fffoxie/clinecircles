"""Surreal decorative motifs built from verified GD objects.

Motifs: oversized cartoon eyes, jagged geometric teeth, distorted circles and
spirals, impossible architecture, digital glitch artifacts.

All of them are grouped so triggers can animate them, and sit on negative
z-layers so they stay behind the gameplay.
"""

from __future__ import annotations

import math

from ..level import Level
from ..model import LevelObject

O_CIRCLE_FILLED = 50
O_CIRCLE_RING = 51
O_CIRCLE_HOLLOW_L = 236
O_CIRCLE_LARGE = 497
O_TINY_CIRCLE = 1764
O_SPLIT_L = 997
O_SPLIT_M = 998
O_SPLIT_S = 999
O_SPLIT_XS = 1000
O_EXPAND_L = 1841
O_EXPAND_S = 1842
O_QUARTER = 1837
O_QUARTER_S = 1838
O_ROD_SHORT = 17
O_ROD_MED = 16
O_ROD_TALL = 15
O_GEAR_L = 85
O_GEAR_M = 86
O_GEAR_S = 87
O_SPIKED_CIRCLE = 1702
O_CHAIN = 498
O_ARROW = 1603
O_PARTICLE_L = 1525
O_PARTICLE_M = 1526
O_PARTICLE_S = 1527


def _put(level: Level, obj_id: int, x: float, y: float, *, channel: int,
         groups: list[int] | None = None, scale: float = 1.0,
         rot: float | None = None, z: int = -3, flip_y: bool = False,
         opacity: float | None = None) -> LevelObject:
    o = LevelObject(obj_id, x, y)
    o.color(channel)
    if groups:
        for g in groups:
            o.add_group(g)
    if scale != 1.0:
        o.scale(scale)
    o.z(z)
    if rot is not None:
        o.rot(rot)
    if flip_y:
        o.set(5, 1)
    if opacity is not None:
        o.set(35, opacity)
    level.add(o)
    return o


# --------------------------------------------------------------------------
# Eyes
# --------------------------------------------------------------------------


def giant_eye(level: Level, x: float, y: float, size: float, *, ring: int,
              iris: int, pupil: int, groups: list[int],
              z: int = -3) -> LevelObject:
    """A huge uncanny eye: outer ring, iris and pupil.

    Returns the pupil object so it can be targeted for "look around" motion.
    """
    _put(level, O_CIRCLE_HOLLOW_L, x, y, channel=ring, groups=groups,
         scale=size, z=z)
    _put(level, O_CIRCLE_FILLED, x, y, channel=iris, groups=groups,
         scale=size * 0.86, z=z + 1)
    return _put(level, O_CIRCLE_RING, x, y, channel=pupil, groups=groups,
                scale=size * 0.34, z=z + 2)


def eye_row(level: Level, x0: float, x1: float, y: float, count: int, *,
            size: float, ring: int, iris: int, pupil: int,
            groups: list[int], z: int = -3) -> None:
    if count <= 1:
        giant_eye(level, x0, y, size, ring=ring, iris=iris, pupil=pupil,
                  groups=groups, z=z)
        return
    step = (x1 - x0) / (count - 1)
    for i in range(count):
        giant_eye(level, x0 + i * step, y, size, ring=ring, iris=iris,
                  pupil=pupil, groups=groups, z=z)


# --------------------------------------------------------------------------
# Teeth
# --------------------------------------------------------------------------


def tooth_wall(level: Level, x0: float, x1: float, y: float, *, count: int,
               channel: int, groups: list[int], size: float = 0.5,
               alternate: bool = True, z: int = -1) -> None:
    """A row of jagged teeth (rotated diamonds) forming a maw."""
    xs = ([x0] if count <= 1
          else [x0 + i * (x1 - x0) / (count - 1) for i in range(count)])
    for i, x in enumerate(xs):
        yy = y + (10.5 if (alternate and i % 2) else 0.0)
        _put(level, O_TINY_CIRCLE, x, yy, channel=channel, groups=groups,
             scale=size, rot=45, z=z)


def maw(level: Level, x: float, y: float, radius: float, *, count: int,
        channel: int, groups: list[int], z: int = -1) -> None:
    """A ring of teeth around a centre point."""
    for i in range(count):
        a = 2 * math.pi * i / count
        _put(level, O_TINY_CIRCLE, x + math.cos(a) * radius,
             y + math.sin(a) * radius, channel=channel, groups=groups,
             scale=0.55, rot=45 + math.degrees(a), z=z)


# --------------------------------------------------------------------------
# Spirals / distorted circles
# --------------------------------------------------------------------------


def spiral(level: Level, x: float, y: float, *, turns: float, radius: float,
           count: int, channel: int, groups: list[int], dot_scale: float = 0.35,
           z: int = -3) -> None:
    for i in range(count):
        t = i / max(1, count - 1)
        a = 2 * math.pi * turns * t
        r = radius * t
        _put(level, O_TINY_CIRCLE, x + math.cos(a) * r, y + math.sin(a) * r,
             channel=channel, groups=groups, scale=dot_scale, z=z)


def concentric_rings(level: Level, x: float, y: float, *, count: int,
                     base: float, channel: int, groups: list[int],
                     z: int = -3) -> None:
    for i in range(count):
        _put(level, O_CIRCLE_RING, x, y, channel=channel, groups=groups,
             scale=base * (1 + i * 0.42), z=z)



# --------------------------------------------------------------------------
# Impossible architecture
# --------------------------------------------------------------------------


def lattice(level: Level, x0: float, x1: float, y: float, *, rows: int,
            spacing: float, channel: int, groups: list[int], z: int = -4,
            skew: float = 0.0) -> None:
    """A skewed block lattice that reads as impossible perspective."""
    n = max(1, int((x1 - x0) / spacing))
    for i in range(n):
        x = x0 + i * spacing
        for r in range(rows):
            _put(level, O_ROD_MED, x + skew * r, y + r * spacing,
                 channel=channel, groups=groups, z=z)


def pillar_run(level: Level, x0: float, x1: float, y: float, *, spacing: float,
               channel: int, groups: list[int], height: int = 6,
               z: int = -4) -> None:
    n = max(1, int((x1 - x0) / spacing))
    for i in range(n):
        x = x0 + i * spacing
        for k in range(height):
            _put(level, O_ROD_TALL, x, y + k * 30, channel=channel,
                 groups=groups, z=z)


# --------------------------------------------------------------------------
# Glitch artifacts
# --------------------------------------------------------------------------


def glitch_strips(level: Level, x0: float, x1: float, y: float, *, count: int,
                  channel: int, groups: list[int], width: float = 90.0,
                  spread: float = 300.0, z: int = 3, seed: int = 1) -> None:
    """Thin offset bars that read as digital tearing (deterministic layout)."""
    state = seed * 2654435761 % 2 ** 32
    for _ in range(count):
        state = (1103515245 * state + 12345) % 2 ** 31
        t = (state % 1000) / 1000.0
        state = (1103515245 * state + 12345) % 2 ** 31
        u = (state % 1000) / 1000.0
        x = x0 + t * (x1 - x0)
        o = _put(level, O_SPLIT_XS, x, y + (u - 0.5) * spread, channel=channel,
                 groups=groups, scale=1.0, z=z)
        o.set(128, width / 30.0)
        o.set(129, 0.25)


def particle_field(level: Level, x0: float, x1: float, y: float, *, count: int,
                   channel: int, groups: list[int], spread: float = 240.0,
                   z: int = -4, seed: int = 7) -> None:
    state = seed * 40503 % 2 ** 32
    ids = [O_PARTICLE_L, O_PARTICLE_M, O_PARTICLE_S]
    for i in range(count):
        state = (1103515245 * state + 12345) % 2 ** 31
        t = (state % 1000) / 1000.0
        state = (1103515245 * state + 12345) % 2 ** 31
        u = (state % 1000) / 1000.0
        _put(level, ids[i % 3], x0 + t * (x1 - x0), y + (u - 0.5) * spread,
             channel=channel, groups=groups, scale=0.6, z=z)
