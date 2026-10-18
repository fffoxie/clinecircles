"""ANTICLINE CIRCLES - dense 90s-CGI construction.

The previous pass placed single large sprites and looked like a skeleton.
Real GD decoration is a MASS of small objects forming filled shapes, so this
module builds solid geometry:

  fill_rect   - a rectangle filled with a grid of bevelled blocks
  fill_disc   - a filled circle (polar fill, no gaps)
  fill_ring   - an annulus
  monster()   - a full clubstep face assembled from fills: skull, sockets,
                eyeballs, pupils, brow, teeth row, jaw, horns
  boss()      - a colossal version with animated groups

Everything is placed on the 30-unit grid and coloured per layer so the shape
reads at a glance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import gamedata as gd
from .level import Level
from .model import LevelObject

O_BLOCK = 1
O_BEVEL = 890
O_GRID_TOP = 2
O_GRID_OUTER = 3
O_GRID_INNER = 4
O_INDUSTRIAL = 817
O_INDUSTRIAL_DARK = 818
O_ROD_SHORT = 17
O_ROD_MED = 16
O_CIRCLE_FILLED = 50
O_CIRCLE_RING = 51
O_CIRCLE_HOLLOW = 236
O_CIRCLE_LARGE = 497
O_TINY = 1764
O_GEAR_L = 85
O_GEAR_M = 86
O_GEAR_S = 87
O_CHAIN = 498
O_SPIKE = 8
O_SPIKED_CIRCLE = 1702
O_SAW_L = 1705
O_PARTICLE_L = 1525

CH_CHROME = 20
CH_CHROME_DARK = 21
CH_GRID = 22
CH_EYE = 23
CH_TEETH = 24
CH_MONSTER = 25
CH_ACCENT = 26
CH_METAL = 27
CH_GLOW = 28
CH_BG = 29
CH_SKY = 30
CH_DEEP = 31

B = 30.0


def _o(level, oid, x, y, ch, z=-3, sx=1.0, sy=None, rot=None, groups=()):
    o = LevelObject(oid, x, y)
    o.color(ch)
    if sx != 1.0 or (sy is not None and sy != 1.0):
        o.set(128, sx)
        o.set(129, sx if sy is None else sy)
    o.z(z)
    if rot:
        o.rot(rot)
    for g in groups:
        o.add_group(g)
    level.add(o)
    return o


# --------------------------------------------------------------------------
# Filled primitives - the density comes from here
# --------------------------------------------------------------------------


def fill_rect(level, x0, x1, y0, y1, *, ch, step=B, z=-3, groups=(),
              oid=O_BEVEL):
    """Fill an axis-aligned rectangle with a grid of blocks."""
    n = 0
    x = x0
    while x <= x1 + 1e-6:
        y = y0
        while y <= y1 + 1e-6:
            _o(level, oid, x, y, ch, z=z, groups=groups)
            y += step
            n += 1
        x += step
    return n


def fill_disc(level, cx, cy, r, *, ch, step=B, z=-3, groups=(), oid=O_BEVEL):
    """Fill a circle on the grid (scanline fill)."""
    n = 0
    y = cy - r
    while y <= cy + r + 1e-6:
        dy = y - cy
        if abs(dy) <= r:
            half = math.sqrt(max(0.0, r * r - dy * dy))
            x = cx - half
            while x <= cx + half + 1e-6:
                _o(level, oid, x, y, ch, z=z, groups=groups)
                x += step
                n += 1
        y += step
    return n


def fill_ring(level, cx, cy, r0, r1, *, ch, step=B, z=-3, groups=(),
              oid=O_BEVEL):
    """Fill an annulus."""
    n = 0
    y = cy - r1
    while y <= cy + r1 + 1e-6:
        dy = y - cy
        x = cx - r1
        while x <= cx + r1 + 1e-6:
            d = math.hypot(x - cx, dy)
            if r0 <= d <= r1:
                _o(level, oid, x, y, ch, z=z, groups=groups)
                n += 1
            x += step
        y += step
    return n


def fill_tri(level, cx, cy, w, h, *, ch, step=B, z=-3, groups=(), down=False):
    """Fill an isoceles triangle (teeth, horns, shards)."""
    n = 0
    rows = max(1, int(h / step))
    for i in range(rows):
        yy = cy + (i * step if down else -i * step)
        frac = 1.0 - i / rows
        half = (w / 2) * frac
        x = cx - half
        while x <= cx + half + 1e-6:
            _o(level, O_SPIKED_CIRCLE, x, yy, ch, z=z, sx=0.9, rot=0 if down else 180,
               groups=groups)
            x += step
            n += 1
    return n


# --------------------------------------------------------------------------
# Monsters - assembled from fills so the face actually reads
# --------------------------------------------------------------------------


def monster(level, cx, cy, size, *, groups=(), z=-4, angry=True):
    """A clubstep monster face. `size` is head radius in blocks."""
    R = size * B
    g = list(groups)
    # skull mass, then a darker inner face plate
    fill_disc(level, cx, cy, R, ch=CH_MONSTER, step=B, z=z, groups=g)
    fill_disc(level, cx, cy, R * 0.86, ch=CH_DEEP, step=B, z=z + 1, groups=g)
    # eye sockets (dark), eyeballs, pupils
    for sgn in (-1, 1):
        ex = cx + sgn * R * 0.40
        ey = cy + R * 0.22
        fill_disc(level, ex, ey, R * 0.30, ch=CH_DEEP, step=B, z=z + 2, groups=g)
        fill_disc(level, ex, ey, R * 0.24, ch=CH_EYE, step=B, z=z + 3, groups=g)
        fill_disc(level, ex, ey - R * 0.02, R * 0.11, ch=CH_CHROME_DARK,
                  step=B, z=z + 4, groups=g)
    # angry brow
    for sgn in (-1, 1):
        for i in range(int(R * 0.34 / B)):
            xx = cx + sgn * (R * 0.18 + i * B)
            yy = cy + R * 0.52 + i * B * 0.42
            _o(level, O_BEVEL, xx, yy, CH_DEEP, z=z + 3, sx=1.1, groups=g)
    # teeth: a filled row of downward triangles
    n_teeth = max(4, int(R * 1.2 / B))
    for i in range(n_teeth):
        t = (i / max(1, n_teeth - 1) - 0.5) * 2
        tx = cx + t * R * 0.62
        fill_tri(level, tx, cy - R * 0.34, B * 1.7, B * 2.2, ch=CH_TEETH,
                 step=B, z=z + 3, groups=g, down=True)
    # jaw
    fill_rect(level, cx - R * 0.72, cx + R * 0.72, cy - R * 0.78, cy - R * 0.62,
              ch=CH_MONSTER, step=B, z=z + 2, groups=g)
    # horns / shard crown
    for sgn in (-1, 1):
        for k in range(3):
            fill_tri(level, cx + sgn * R * (0.45 + k * 0.18), cy + R * 0.86,
                     B * 2.2, B * (4.0 - k), ch=CH_ACCENT, step=B,
                     z=z - 1, groups=g)
    return g


def boss(level, cx, cy, size, *, groups=(), z=-6):
    """A colossal boss head: monster + rings + orbiting teeth."""
    g = monster(level, cx, cy, size, groups=groups, z=z, angry=True)
    R = size * B
    fill_ring(level, cx, cy, R * 1.10, R * 1.22, ch=CH_GLOW, step=B, z=z - 2,
              groups=g)
    fill_ring(level, cx, cy, R * 1.30, R * 1.36, ch=CH_ACCENT, step=B, z=z - 2,
              groups=g)
    # orbiting teeth
    for i in range(24):
        a = 2 * math.pi * i / 24
        tx = cx + math.cos(a) * R * 1.46
        ty = cy + math.sin(a) * R * 1.46
        _o(level, O_SPIKED_CIRCLE, tx, ty, CH_TEETH, z=z - 1, sx=1.5,
           rot=math.degrees(a) + 90, groups=g)
    return g


# --------------------------------------------------------------------------
# Architecture
# --------------------------------------------------------------------------


def chrome_pillar(level, x, y0, y1, *, width_blocks=3, ch=CH_CHROME,
                  z=-3, groups=()):
    """A solid metallic column, lit on one side."""
    n = 0
    for w in range(int(width_blocks)):
        ch2 = ch if w < width_blocks / 2 else CH_CHROME_DARK
        y = y0
        while y <= y1 + 1e-6:
            _o(level, O_BEVEL, x + w * B, y, ch2, z=z, groups=groups)
            y += B
            n += 1
    return n


def wire_box(level, cx, cy, w, h, d, *, ch=CH_GLOW, z=-6, groups=()):
    """Isometric wireframe box: 8 projected corners, 12 rods."""
    k, m = math.cos(math.radians(30)), math.sin(math.radians(30))

    def pr(X, Y, Z):
        return (cx + X + Z * k, cy + Y + Z * m)

    hw, hh = w / 2, h / 2
    f = [pr(-hw, -hh, 0), pr(hw, -hh, 0), pr(hw, hh, 0), pr(-hw, hh, 0)]
    b = [pr(-hw, -hh, d), pr(hw, -hh, d), pr(hw, hh, d), pr(-hw, hh, d)]
    for quad in (f, b):
        for i in range(4):
            a1, b1 = quad[i], quad[(i + 1) % 4]
            _rod_line(level, a1, b1, ch, z, groups)
    for a1, b1 in zip(f, b):
        _rod_line(level, a1, b1, ch, z, groups)


def _rod_line(level, p0, p1, ch, z, groups, step=B * 0.8):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy)
    if ln < 1:
        return
    n = max(1, int(ln / step))
    rot = math.degrees(math.atan2(dy, dx))
    for i in range(n + 1):
        t = i / n
        _o(level, O_ROD_MED, p0[0] + dx * t, p0[1] + dy * t, ch, z=z,
           sx=0.16, sy=1.0, rot=rot, groups=groups)


def grid_wall(level, x0, x1, y0, y1, *, ch=CH_GRID, step=B * 2, z=-8,
              groups=()):
    """A luminous grid wall filling the whole backdrop."""
    n = 0
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            _o(level, O_ROD_SHORT, x, y, ch, z=z, sx=0.08, sy=0.05,
               groups=groups)
            x += step
            n += 1
        y += step
    return n


PALETTE = {
    CH_CHROME: (236, 240, 250),
    CH_CHROME_DARK: (86, 94, 118),
    CH_GRID: (70, 210, 250),
    CH_EYE: (255, 246, 196),
    CH_TEETH: (252, 252, 255),
    CH_MONSTER: (132, 78, 205),
    CH_ACCENT: (255, 56, 170),
    CH_METAL: (150, 162, 186),
    CH_GLOW: (110, 255, 226),
    CH_BG: (10, 8, 26),
    CH_SKY: (26, 18, 62),
    CH_DEEP: (44, 22, 72),
}


def apply_palette(level):
    from .model import Color
    for ch, (r, g, b) in PALETTE.items():
        level.colors[ch] = Color(channel=ch, r=r, g=g, b=b)
    C = gd.ColorChannel
    if C.BG in level.colors:
        level.colors[C.BG].r, level.colors[C.BG].g, level.colors[C.BG].b = PALETTE[CH_BG]


def decorate(level, tl, sections):
    """Dense assembly across every section."""
    for name, (x0, x1) in sections.items():
        w = x1 - x0
        # 1. continuous luminous backdrop grid (fills the whole frame)
        grid_wall(level, x0, x1, -120, 960, ch=CH_GRID, step=90, z=-9)
        # 2. architectural ribs: shorter, spaced out, alternating heights
        x = x0 + 60
        i = 0
        while x < x1:
            top = 560 + (i % 3) * 90
            chrome_pillar(level, x, 300, top, width_blocks=2, z=-4)
            chrome_pillar(level, x, -180, -30, width_blocks=2, z=-4)
            x += 420
            i += 1
        # 3. wireframe boxes floating in the space
        x = x0 + 200
        i = 0
        while x < x1:
            wire_box(level, x, 470 + (i % 3) * 80, 170, 120, 110 + (i % 2) * 70,
                     ch=CH_GLOW, z=-6)
            x += 500
            i += 1
        # 4. monsters as architecture
        n_mon = max(2, int(w / 1600))
        for k in range(n_mon):
            mx = x0 + w * (k + 0.5) / n_mon
            monster(level, mx, 620 + (k % 2) * 70, 3.6, z=-3)
    if "boss_fight" in sections:
        bx0, bx1 = sections["boss_fight"]
        boss(level, (bx0 + bx1) / 2, 640, 6.0, z=-6)
    return


def assemble():
    from .layout import build_level
    res = build_level()
    level = res.level
    level.name = "Anticline Circles"
    level.description = ("ANTICLINE CIRCLES - 1990s CGI / clubstep monsters. "
                         "Unofficial fan level.")
    apply_palette(level)
    decorate(level, res.timeline, res.section_x)
    # trigger spine: one pulse per beat, straight row under the play area
    from .triggers import TriggerSet
    ts = TriggerSet(level)
    beat = res.track.beat_s
    t = res.track.time_at_bar(0)
    end = res.length_units
    while True:
        x = res.timeline.x_at_bar(res.track.bar_at_time(t))
        if x > end:
            break
        if x >= 0:
            ts.pulse(x, -120, target_type=gd.PulseTarget.CHANNEL,
                     target_id=CH_GRID, r=90, g=230, b=255,
                     fade_in=0.05, hold=0.02, fade_out=0.25)
        t += beat
    return res, level
