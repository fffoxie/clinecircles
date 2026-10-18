"""ANTICLINE CIRCLES - 1990s CGI decoration system.

Visual language, from the reference images:
  * chrome / metallic primitive solids with strong light-dark faces
  * luminous wireframe grids receding in perspective
  * oversized cartoon eyes, jagged teeth, clubstep monsters as ARCHITECTURE
  * industrial machinery: gears, bolts, chains, beams
  * polar / rotational symmetry (the Aperture look)

All geometry uses verified GD object ids and is placed with real maths
(isometric + perspective projection), so the shapes are constructed rather
than eyeballed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import gamedata as gd
from .level import Level
from .model import LevelObject

# verified ids
O_BLOCK = 1
O_BEvel = 890            # Beveled Block (rounded / 3D shaded)
O_GRID_TOP = 2
O_GRID_OUTER = 3
O_GRID_INNER = 4
O_GRID_CENTER = 5
O_INDUSTRIAL = 817       # Light Industrial Block with Bolts
O_INDUSTRIAL_DARK = 818
O_ROD_SHORT = 17
O_ROD_MED = 16
O_ROD_TALL = 15
O_CIRCLE_FILLED = 50
O_CIRCLE_RING = 51
O_CIRCLE_HOLLOW = 236
O_CIRCLE_LARGE = 497
O_SPLIT_L = 997
O_TINY = 1764
O_GEAR_L = 85
O_GEAR_M = 86
O_GEAR_S = 87
O_CHAIN = 498
O_SPIKE = 8
O_SAW_L = 1705
O_ARROW = 1603
O_SPIKED_CIRCLE = 1702
O_PARTICLE_L = 1525
O_PARTICLE_S = 1527

# colour channels used by the CGI look
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

B = 30.0


def _add(level, oid, x, y, *, ch, z=-3, sx=1.0, sy=None, rot=None,
         groups=(), flipy=False):
    o = LevelObject(oid, x, y)
    o.color(ch)
    if sx != 1.0 or (sy is not None and sy != 1.0):
        o.set(128, sx)
        o.set(129, sx if sy is None else sy)
    o.z(z)
    if rot:
        o.rot(rot)
    if flipy:
        o.set(5, 1)
    for g in groups:
        o.add_group(g)
    level.add(o)
    return o


def _line(level, x0, y0, x1, y1, *, ch, thickness=0.18, z=-3, groups=(),
          spacing=30.0):
    """A straight edge built from rod sprites placed along the vector."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    if ln < 1:
        return
    n = max(1, int(ln / spacing))
    rot = math.degrees(math.atan2(dy, dx))
    for i in range(n + 1):
        t = i / n
        _add(level, O_ROD_MED, x0 + dx * t, y0 + dy * t, ch=ch, z=z,
             sx=thickness, sy=1.0, rot=rot, groups=groups)


def wire_box(level, cx, cy, w, h, d, *, ch, z=-4, groups=(), depth_ch=None):
    """An isometric wireframe box: 8 projected corners, 12 rods."""
    k = math.cos(math.radians(30))
    m = math.sin(math.radians(30))

    def proj(X, Y, Z):
        return (cx + X + Z * k, cy + Y + Z * m)

    hw, hh = w / 2, h / 2
    front = [proj(-hw, -hh, 0), proj(hw, -hh, 0),
             proj(hw, hh, 0), proj(-hw, hh, 0)]
    back = [proj(-hw, -hh, d), proj(hw, -hh, d),
            proj(hw, hh, d), proj(-hw, hh, d)]
    for quad in (front, back):
        for i in range(4):
            a, b = quad[i], quad[(i + 1) % 4]
            _line(level, a[0], a[1], b[0], b[1], ch=ch, z=z, groups=groups)
    for a, b in zip(front, back):
        _line(level, a[0], a[1], b[0], b[1], ch=depth_ch or ch, z=z, groups=groups)


def chrome_tower(level, x, y, height_blocks, *, width=1.0, z=-3, groups=(),
                 ch=CH_CHROME, dark=CH_CHROME_DARK):
    """A metallic tower: alternating lit and shadowed bevelled blocks."""
    for i in range(int(height_blocks)):
        yy = y + i * B
        o = LevelObject(O_BEvel, x, yy)
        o.color(ch if i % 2 == 0 else dark).scale(width).z(z)
        for g in groups:
            o.add_group(g)
        level.add(o)


def machinery(level, x, y, *, scale=1.0, z=-2, groups=()):
    """An industrial cluster: gear + bolts block + chain."""
    _add(level, O_GEAR_L, x, y, ch=CH_METAL, z=z, sx=scale, groups=groups)
    _add(level, O_INDUSTRIAL, x + 1.6 * B * scale, y - 0.6 * B, ch=CH_METAL,
         z=z, sx=0.9 * scale, groups=groups)
    _add(level, O_INDUSTRIAL_DARK, x - 1.6 * B * scale, y - 0.6 * B,
         ch=CH_CHROME_DARK, z=z, sx=0.9 * scale, groups=groups)
    for i in range(4):
        _add(level, O_CHAIN, x + (i - 1.5) * B * 0.8, y - 2.1 * B,
             ch=CH_METAL, z=z, sx=0.7 * scale, groups=groups)


def grid_hall(level, x0, x1, ybase, *, rows=6, spacing=210.0, z=-6,
              groups=(), ch=CH_GRID):
    """Receding luminous grid: horizontal rails + vertical risers."""
    x = x0
    while x <= x1:
        for r in range(rows):
            _add(level, O_ROD_MED, x, ybase + r * spacing * 0.42, ch=ch, z=z,
                 sx=0.12, sy=1.0, groups=groups)
        x += spacing
    for r in range(rows):
        yy = ybase + r * spacing * 0.42
        _line(level, x0, yy, x1, yy, ch=ch, thickness=0.10, z=z, groups=groups,
              spacing=140.0)


def monster(level, cx, cy, size, *, groups=(), z=-2, variant=0):
    """A clubstep monster: huge head, oversized eyes, jagged teeth, shards.

    `size` is roughly the head radius in blocks.
    """
    R = size * B
    # skull
    _add(level, O_CIRCLE_LARGE, cx, cy, ch=CH_MONSTER, z=z, sx=size * 0.92,
         groups=groups)
    _add(level, O_CIRCLE_FILLED, cx, cy, ch=CH_CHROME_DARK, z=z + 1,
         sx=size * 0.80, groups=groups)
    # eyes: two huge ovals with pupils
    for sgn in (-1, 1):
        ex = cx + sgn * R * 0.42
        ey = cy + R * 0.28
        _add(level, O_CIRCLE_RING, ex, ey, ch=CH_EYE, z=z + 2,
             sx=size * 0.34, groups=groups)
        _add(level, O_TINY, ex, ey - R * 0.02, ch=CH_CHROME_DARK, z=z + 3,
             sx=size * 0.14, groups=groups)
    # brow ridges
    for sgn in (-1, 1):
        _add(level, O_ROD_MED, cx + sgn * R * 0.42, cy + R * 0.58, ch=CH_TEETH,
             z=z + 2, sx=0.30, sy=0.9, rot=-sgn * 22, groups=groups)
    # jagged teeth
    n_teeth = 9
    for i in range(n_teeth):
        t = (i / (n_teeth - 1) - 0.5) * 2.0
        tx = cx + t * R * 0.62
        ty = cy - R * 0.52 + abs(t) * R * 0.12
        _add(level, O_SPIKED_CIRCLE, tx, ty, ch=CH_TEETH, z=z + 2,
             sx=size * 0.16, rot=180, groups=groups)
    # surrounding shards (silhouette spikes)
    for i in range(14):
        a = math.pi * (0.08 + 0.84 * i / 13)
        sx = cx + math.cos(a) * R * 1.12
        sy = cy + math.sin(a) * R * 1.12
        _add(level, O_TINY, sx, sy, ch=CH_ACCENT, z=z - 1, sx=size * 0.22,
             rot=math.degrees(a) + 45, groups=groups)


def teeth_maw(level, cx, cy, radius, *, count=16, groups=(), z=-1,
              ch=CH_TEETH, opening=0.0):
    """A ring of teeth; `opening` (0..1) gaps the top so the player can pass."""
    for i in range(count):
        a = 2 * math.pi * i / count
        # keep a gap at the top when opening > 0
        if opening > 0 and abs(math.sin(a - math.pi / 2)) > 1 - opening:
            continue
        x = cx + math.cos(a) * radius
        y = cy + math.sin(a) * radius
        _add(level, O_TINY, x, y, ch=ch, z=z, sx=0.55,
             rot=math.degrees(a) + 45, groups=groups)


def radial_fan(level, cx, cy, r0, r1, n, *, ch, z=-5, groups=(), width=0.10):
    """Radial line fan (the Aperture look)."""
    for i in range(n):
        a = 2 * math.pi * i / n
        x0 = cx + math.cos(a) * r0
        y0 = cy + math.sin(a) * r0
        x1 = cx + math.cos(a) * r1
        y1 = cy + math.sin(a) * r1
        _line(level, x0, y0, x1, y1, ch=ch, thickness=width, z=z,
              groups=groups, spacing=60.0)


def rotating_ring(level, cx, cy, radius, n, *, ch, z=-4, groups=(), scale=0.5):
    for i in range(n):
        a = 2 * math.pi * i / n
        _add(level, O_GEAR_S, cx + math.cos(a) * radius,
             cy + math.sin(a) * radius, ch=ch, z=z, sx=scale,
             rot=math.degrees(a), groups=groups)


# --------------------------------------------------------------------------
# Palette + full-level assembly
# --------------------------------------------------------------------------

PALETTE = {
    CH_CHROME: (232, 236, 245),
    CH_CHROME_DARK: (92, 100, 122),
    CH_GRID: (70, 200, 235),
    CH_EYE: (255, 246, 200),
    CH_TEETH: (250, 250, 255),
    CH_MONSTER: (58, 28, 92),
    CH_ACCENT: (255, 60, 170),
    CH_METAL: (150, 160, 180),
    CH_GLOW: (120, 255, 220),
    CH_BG: (14, 10, 30),
}


def apply_palette(level):
    from .model import Color
    for ch, (r, g, b) in PALETTE.items():
        level.colors[ch] = Color(channel=ch, r=r, g=g, b=b)
    C = gd.ColorChannel
    if C.BG in level.colors:
        level.colors[C.BG].r, level.colors[C.BG].g, level.colors[C.BG].b = PALETTE[CH_BG]


def _spine(level, tl, x0, x1, *, y=-95.0):
    """The trigger spine: one colour+pulse trigger per beat along the level.

    Beat length in units = speed * 60 / bpm (see docs/LEVEL_REFERENCES.md).
    Triggers go in a dead-straight row at a fixed y so the level stays
    editor-readable.
    """
    from .triggers import TriggerSet
    ts = TriggerSet(level)
    beat = tl.track.beat_s
    t = tl.track.time_at_bar(0)
    while True:
        x = tl.x_at_bar(tl.track.bar_at_time(t))
        if x > x1:
            break
        if x >= x0:
            ts.pulse(x, y, target_type=gd.PulseTarget.CHANNEL, target_id=CH_GRID,
                     r=80, g=220, b=255, fade_in=0.05, hold=0.02, fade_out=0.22)
        t += beat
    return ts


def decorate(level, tl, sections):
    """Lay the CGI/monster decoration across every section."""
    groups: list[int] = []

    for name, (x0, x1) in sections.items():
        mid = (x0 + x1) / 2
        width = x1 - x0
        # 1. luminous grid hall behind everything (dense)
        grid_hall(level, x0, x1, ybase=60, rows=8, spacing=130, z=-8,
                  ch=CH_GRID)
        # 2. wireframe boxes receding in perspective (the 90s CGI look)
        step = max(300.0, width / 3)
        x = x0 + step * 0.4
        i = 0
        while x < x1:
            wire_box(level, x, 210 + (i % 3) * 90, 180, 140,
                     120 + (i % 2) * 70, ch=CH_GLOW, z=-6,
                     depth_ch=CH_GRID)
            x += step * 0.5
            i += 1
        # 3. chrome towers
        x = x0 + 90
        while x < x1:
            chrome_tower(level, x, 60, 9, width=1.0, z=-3,
                         ch=CH_CHROME, dark=CH_CHROME_DARK)
            x += 240.0
        # 4. machinery clusters
        x = x0 + 160
        while x < x1:
            machinery(level, x, 150, scale=1.0, z=-2)
            x += 380.0
        # 5. clubstep monsters as architecture: several per section
        n_mon = max(2, int(width / 1500))
        for k in range(n_mon):
            mx = x0 + width * (k + 0.5) / n_mon
            monster(level, mx, 360 + (k % 2) * 80, 4.2, z=-2)
            teeth_maw(level, mx + 380, 300, 250, count=26, z=-1, opening=0.42)
            radial_fan(level, mx, 360, 120, 700, 32, ch=CH_GLOW, z=-6,
                       width=0.07)
            rotating_ring(level, mx, 360, 420, 18, ch=CH_METAL, z=-4,
                          scale=0.7)
    return groups


def build_anticline():
    """Assemble ANTICLINE CIRCLES: layout + CGI decoration + trigger spine."""
    from .layout import build_level
    res = build_level()
    level = res.level
    level.name = "Anticline Circles"
    level.description = ("ANTICLINE CIRCLES - 1990s CGI / clubstep monsters. "
                         "Unofficial fan level.")
    apply_palette(level)
    decorate(level, res.timeline, res.section_x)
    _spine(level, res.timeline, 0, res.length_units)
    return res, level
