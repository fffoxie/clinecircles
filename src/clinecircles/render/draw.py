"""A Pillow renderer for the level: an editor-style approximation of GD.

This is not the game. It is a *verification tool*: it parses the decoded level
string, resolves the trigger state at a moment in time, and draws every object
with its position, rotation, scale, colour, Z-layer and opacity, so the level
can be looked at without a GD client.

Object shapes are vector approximations keyed on the verified object id
(:mod:`clinecircles.ids`). Each shape is drawn with the object's *real* grid
size where that is known (1 block = 30 units) so spacing and readability can be
judged honestly.

Deliberate limits (see docs/QA_checklist.md):

* no GD sprite art - blocks are squares, spikes are triangles, gears are
  circles with teeth, portals are capsules with a glyph.
* no glow, blending or particles beyond a translucent overlay.
* text objects are drawn with a Pillow font, not GD's bitmap font.
"""

from __future__ import annotations

import base64
import math
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from .. import ids
from ..gamedata import Prop
from ..level import Level
from ..model import LevelObject
from . import state as S

BLOCK = 30.0

#: object id -> drawing family
SPIKES = {8: 1.0, 39: 0.62, 103: 0.55, 144: 0.9, 18: 1.0, 19: 0.8, 20: 0.6,
          21: 0.4, 123: 1.0, 127: 0.7}
SAWS = {1705: 1.0, 1706: 0.72, 1707: 0.5, 1702: 0.8}
BLOCKS = {1, 2, 890, 1338, 1339, 1340}
CIRCLES = {50: "fill", 51: "ring", 236: "hollow", 497: "fill", 1764: "fill",
           997: "split", 998: "split", 999: "split", 1000: "split",
           1837: "quarter", 1838: "quarter", 1841: "expand", 1842: "expand"}
GEARS = {85: 1.0, 86: 0.66, 87: 0.44}
RODS = {15: 1.0, 16: 0.75, 17: 0.5, 498: 0.6}
PARTICLES = {1525: 1.0, 1526: 0.7, 1527: 0.45}
MODES = {12: "cube", 13: "ship", 47: "ball", 111: "UFO", 660: "wave",
         745: "robot", 1331: "spider", 1933: "swing"}
SPEEDS = {200: "0.5x", 201: "1x", 202: "2x", 203: "3x", 1334: "4x"}
GRAVITY = {10: "grav-down", 11: "grav-up"}
SIZES = {99: "big", 101: "mini"}
DUALS = {286: "dual-on", 287: "dual-off"}
MIRRORS = {45: "mirror-in", 46: "mirror-out"}
ORBS = {36: "yellow", 141: "pink", 1333: "red", 84: "blue", 1022: "green",
        1330: "black", 1594: "toggle", 1704: "dash-green",
        1751: "dash-pink"}
PADS = {35: "yellow", 140: "pink", 1332: "red", 67: "blue"}
TEXT_OBJ = 914


@dataclass
class Camera:
    """A GD-like camera: 640x360 units of world visible, centred on the player."""

    x: float
    y: float
    view_w: float = 640.0
    view_h: float = 360.0
    zoom: float = 1.0

    def project(self, wx: float, wy: float, w: int, h: int) -> tuple[float, float]:
        scale = (w / (self.view_w / self.zoom))
        cx = w * 0.5
        cy = h * 0.5
        return (cx + (wx - self.x) * scale, cy - (wy - self.y) * scale)

    def scale(self, w: int) -> float:
        return w / (self.view_w / self.zoom)


def _font(size: int):
    for path in ("/tmp/fontsroot/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/tmp/fontsroot/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _text_of(o: LevelObject) -> str:
    raw = o.get(Prop.TEXT) or o.get(31)
    if not raw:
        return ""
    try:
        return base64.b64decode(str(raw)).decode("utf-8", "replace")
    except Exception:
        return str(raw)


def _tri(dr: ImageDraw.ImageDraw, pts, fill, outline=None, width=1):
    dr.polygon(pts, fill=fill, outline=outline, width=width)


def _capsule(dr, box, fill, outline, width=2):
    dr.rounded_rectangle(box, radius=max(2.0, (box[3] - box[1]) * 0.35),
                         fill=fill, outline=outline, width=width)


def draw_scene(level: Level, objects: list[LevelObject], triggers: list[LevelObject],
               t: float, tl, *, width: int = 1280, height: int = 720,
               cam_y: float = 225.0, grid: bool = False, show_triggers: bool = False,
               player_x: float | None = None, player_y: float | None = None,
               player_mode: str = "cube") -> Image.Image:
    """Render one frame of the level at level time ``t``."""
    st = S.simulate(level, triggers, t, tl)
    px = tl.x_at_time(t) if player_x is None else player_x
    cam = Camera(x=px + st.cam_dx, y=cam_y + st.cam_dy, zoom=st.zoom)
    img = Image.new("RGB", (width, height), st.colour(PAL_SKY))
    dr = ImageDraw.Draw(img, "RGBA")

    _draw_background(dr, st, cam, width, height, tl, t)
    if grid:
        _draw_grid(dr, cam, width, height)

    sc = cam.scale(width)
    # painter's algorithm: z layer, then z order, then y (GD draws higher first)
    def key(o: LevelObject):
        return (int(o.get(Prop.Z_LAYER, 0)), int(o.get(Prop.Z_ORDER, 0)),
                -o.y)

    gs = _group_lookup(level, objects)
    for o in sorted(objects, key=key):
        if int(o.id) in S.TRIGGER_IDS and not show_triggers:
            continue
        g = _group_state(o, gs, st)
        if g.hidden or g.opacity <= 0.01:
            continue
        x = o.x + g.dx
        y = o.y + g.dy
        if not (cam.x - cam.view_w <= x <= cam.x + cam.view_w):
            continue
        _draw_object(dr, o, x, y, g, st, cam, width, height, sc)

    _draw_player(dr, cam, width, height, px, player_y, player_mode, sc)
    _draw_hud(dr, st, t, tl, width, height, level)
    return img


PAL_SKY = 1


def _group_lookup(level: Level, objects: list[LevelObject]) -> dict[int, list[int]]:
    """group id -> indices of objects in it (built once, cached by caller)."""
    return getattr(level, "_render_groups", {}) or {}


def _group_state(o: LevelObject, gs, st: S.SceneState) -> S.GroupState:
    """Combine every group the object belongs to into one transform."""
    out = S.GroupState()
    for g in o.groups():
        st_g = st.groups.get(g)
        if st_g is None:
            continue
        out.dx += st_g.dx
        out.dy += st_g.dy
        out.rot += st_g.rot
        out.opacity *= st_g.opacity
        out.hidden = out.hidden or st_g.hidden
    return out


def _draw_background(dr, st, cam: Camera, w: int, h: int, tl, t: float) -> None:
    """Sky gradient plus a parallax grid that reads as GD's background."""
    top = st.colour(PAL_SKY)
    bot = st.colour(2)
    for i in range(h):
        k = i / max(1, h - 1)
        dr.line([(0, i), (w, i)], fill=tuple(
            int(top[c] + (bot[c] - top[c]) * k) for c in range(3)))
    # parallax grid lines on the B5 layer
    grid_c = st.colour(5)
    step = 90.0
    sc = cam.scale(w)
    ox = (-cam.x * 0.25) % step
    for i in range(int(w / (step * sc)) + 3):
        px = (i * step + ox) * sc
        dr.line([(px, 0), (px, h)], fill=grid_c + (28,))
    oy = (-cam.y * 0.25) % step
    for i in range(int(h / (step * sc)) + 3):
        py = (i * step + oy) * sc
        dr.line([(0, py), (w, py)], fill=grid_c + (28,))
    # ground band
    gy = cam.project(0.0, 0.0, w, h)[1]
    if 0 <= gy <= h:
        dr.rectangle([(0, gy), (w, h)], fill=st.colour(3) + (255,))
        dr.line([(0, gy), (w, gy)], fill=st.colour(4) + (255,), width=2)


def _draw_grid(dr, cam: Camera, w: int, h: int) -> None:
    sc = cam.scale(w)
    step = BLOCK * sc
    ox = (-cam.x % BLOCK) * sc
    oy = (-cam.y % BLOCK) * sc
    for i in range(int(w / step) + 2):
        dr.line([(i * step + ox, 0), (i * step + ox, h)], fill=(255, 0, 255, 60))
    for i in range(int(h / step) + 2):
        dr.line([(0, i * step + oy), (w, i * step + oy)], fill=(255, 0, 255, 60))


def _draw_object(dr, o: LevelObject, x: float, y: float, g: S.GroupState,
                 st: S.SceneState, cam: Camera, w: int, h: int,
                 sc: float) -> None:
    oid = int(o.id)
    ch = int(o.get(Prop.COLOR_1, 0))
    rgb = st.colour(ch)
    a = int(255 * g.opacity * float(o.get(Prop.OPACITY, 1.0)))
    sx = float(o.get(Prop.SCALE_X, 1.0))
    sy = float(o.get(Prop.SCALE_Y, 1.0))
    rot = float(o.get(Prop.ROTATION, 0.0)) + g.rot
    flip_y = int(o.get(Prop.FLIP_Y, 0)) == 1
    cxp, cyp = cam.project(x, y, w, h)
    half = BLOCK * sc * 0.5

    if oid in BLOCKS:
        _rect(dr, cxp, cyp, half * sx, half * sy, rgb, a, rot,
              bevel=(oid == 890), flip_y=flip_y)
    elif oid in SPIKES:
        k = SPIKES[oid]
        _spike(dr, cxp, cyp, half * k * sx, half * sy, rgb, a, rot, flip_y)
    elif oid in SAWS:
        _saw(dr, cxp, cyp, half * SAWS[oid] * 1.6 * sx, rgb, a, rot)
    elif oid in CIRCLES:
        _circle(dr, cxp, cyp, half * sx, rgb, a, CIRCLES[oid], rot)
    elif oid in GEARS:
        _gear(dr, cxp, cyp, half * GEARS[oid] * 1.6 * sx, rgb, a, rot)
    elif oid in RODS:
        _rect(dr, cxp, cyp, half * 0.35 * sx, half * RODS[oid] * 1.4 * sy, rgb, a,
              rot, bevel=False, flip_y=flip_y)
    elif oid in PARTICLES:
        _circle(dr, cxp, cyp, half * PARTICLES[oid] * sx, rgb, a, "fill", rot)
    elif oid in MODES:
        _capsule(dr, [cxp - half * 0.8, cyp - half * 1.7, cxp + half * 0.8,
                      cyp + half * 1.7], rgb, (255, 255, 255, 200), 2)
        _glyph(dr, cxp, cyp, MODES[oid], sc)
    elif oid in SPEEDS:
        _capsule(dr, [cxp - half * 0.7, cyp - half * 1.2, cxp + half * 0.7,
                      cyp + half * 1.2], rgb, (255, 255, 255, 180), 2)
        dr.text((cxp - 14, cyp - 7), SPEEDS[oid], font=_font(max(10, int(13 * sc / 2))),
                fill=(255, 255, 255, 230))
    elif oid in GRAVITY:
        _capsule(dr, [cxp - half * 0.7, cyp - half * 1.2, cxp + half * 0.7,
                      cyp + half * 1.2], rgb, (255, 255, 255, 180), 2)
    elif oid in SIZES:
        _capsule(dr, [cxp - half * 0.7, cyp - half * 1.1, cxp + half * 0.7,
                      cyp + half * 1.1], rgb, (255, 255, 255, 180), 2)
    elif oid in DUALS or oid in MIRRORS:
        _capsule(dr, [cxp - half * 0.7, cyp - half * 1.1, cxp + half * 0.7,
                      cyp + half * 1.1], rgb, (255, 255, 255, 180), 2)
    elif oid in ORBS:
        _circle(dr, cxp, cyp, half * 1.1 * sx, rgb, a, "ring", rot)
        _circle(dr, cxp, cyp, half * 0.5 * sx, rgb, a, "fill", rot)
    elif oid in PADS:
        dr.polygon([(cxp - half * 1.3, cyp + half * 0.5),
                    (cxp + half * 1.3, cyp + half * 0.5),
                    (cxp + half * 0.9, cyp - half * 0.5),
                    (cxp - half * 0.9, cyp - half * 0.5)],
                   fill=rgb + (a,), outline=(255, 255, 255, 200))
    elif oid == TEXT_OBJ:
        txt = _text_of(o)
        size = max(10, int(28 * sx * sc / 1.5))
        dr.text((cxp, cyp), txt, font=_font(size), fill=rgb + (a,), anchor="mm")
    else:
        dr.rectangle([(cxp - half, cyp - half), (cxp + half, cyp + half)],
                     outline=rgb + (min(a, 140),), width=1)


def _rect(dr, cx, cy, hw, hh, rgb, a, rot, bevel=False, flip_y=False) -> None:
    if abs(rot) < 1e-6:
        box = [cx - hw, cy - hh, cx + hw, cy + hh]
        dr.rectangle(box, fill=rgb + (a,), outline=(0, 0, 0, min(a, 200)), width=1)
        if bevel:
            dr.rounded_rectangle(box, radius=max(1, hw * 0.35), fill=rgb + (a,),
                                 outline=(0, 0, 0, min(a, 200)), width=1)
        return
    rad = math.radians(rot)
    cs, sn = math.cos(rad), math.sin(rad)
    pts = []
    for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
        pts.append((cx + dx * cs - dy * sn, cy + dx * sn + dy * cs))
    dr.polygon(pts, fill=rgb + (a,), outline=(0, 0, 0, min(a, 200)))


def _spike(dr, cx, cy, hw, hh, rgb, a, rot, flip_y=False) -> None:
    sgn = 1.0 if flip_y else -1.0
    pts = [(cx - hw, cy - sgn * hh), (cx + hw, cy - sgn * hh), (cx, cy + sgn * hh)]
    if abs(rot) > 1e-6:
        rad = math.radians(rot)
        cs, sn = math.cos(rad), math.sin(rad)
        pts = [(cx + (px - cx) * cs - (py - cy) * sn,
                cy + (px - cx) * sn + (py - cy) * cs) for px, py in pts]
    dr.polygon(pts, fill=rgb + (a,), outline=(0, 0, 0, min(a, 220)))


def _saw(dr, cx, cy, r, rgb, a, rot) -> None:
    n = 12
    pts = []
    for i in range(n * 2):
        ang = math.radians(rot) + math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.68
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    dr.polygon(pts, fill=rgb + (a,), outline=(0, 0, 0, min(a, 220)))


def _circle(dr, cx, cy, r, rgb, a, style, rot=0.0) -> None:
    box = [cx - r, cy - r, cx + r, cy + r]
    if style in ("fill", "split"):
        dr.ellipse(box, fill=rgb + (a,), outline=(0, 0, 0, min(a, 200)))
        if style == "split":
            dr.line([(cx, cy - r), (cx, cy + r)], fill=(0, 0, 0, min(a, 200)), width=2)
    elif style == "ring":
        dr.ellipse(box, outline=rgb + (a,), width=max(2, int(r * 0.28)))
    elif style == "hollow":
        dr.ellipse(box, outline=rgb + (a,), width=max(2, int(r * 0.2)))
    elif style == "quarter":
        dr.pieslice(box, start=rot, end=rot + 90, fill=rgb + (a,),
                    outline=(0, 0, 0, min(a, 200)))
    elif style == "expand":
        dr.ellipse(box, outline=rgb + (min(a, 150),), width=2)


def _gear(dr, cx, cy, r, rgb, a, rot) -> None:
    n = 10
    pts = []
    for i in range(n * 2):
        ang = math.radians(rot) + math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.8
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    dr.polygon(pts, fill=rgb + (a,), outline=(0, 0, 0, min(a, 200)))
    dr.ellipse([cx - r * 0.32, cy - r * 0.32, cx + r * 0.32, cy + r * 0.32],
               fill=(0, 0, 0, 0))


def _glyph(dr, cx, cy, mode: str, sc: float) -> None:
    f = _font(max(9, int(11 * sc / 2)))
    dr.text((cx, cy), mode[0].upper(), font=f, fill=(20, 20, 30, 230), anchor="mm")


def _draw_player(dr, cam: Camera, w: int, h: int, px: float,
                 py: float | None, mode: str, sc: float) -> None:
    y = cam.y if py is None else py
    cxp, cyp = cam.project(px, y, w, h)
    r = 15.0 * sc
    col = (255, 255, 255, 235)
    if mode == "cube":
        dr.rectangle([cxp - r, cyp - r, cxp + r, cyp + r], fill=col,
                     outline=(20, 20, 30, 255), width=2)
    elif mode in ("ship", "ufo"):
        dr.ellipse([cxp - r, cyp - r * 0.8, cxp + r * 1.4, cyp + r * 0.8],
                   fill=col, outline=(20, 20, 30, 255), width=2)
    elif mode == "wave":
        dr.polygon([(cxp - r, cyp), (cxp, cyp - r), (cxp + r, cyp),
                    (cxp, cyp + r)], fill=col, outline=(20, 20, 30, 255))
    elif mode == "ball":
        dr.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=col,
                   outline=(20, 20, 30, 255), width=2)
        dr.line([(cxp - r, cyp), (cxp + r, cyp)], fill=(20, 20, 30, 255), width=2)
    elif mode == "robot":
        dr.rectangle([cxp - r * 0.8, cyp - r, cxp + r * 0.8, cyp + r], fill=col,
                     outline=(20, 20, 30, 255), width=2)
    elif mode == "spider":
        dr.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], outline=col, width=3)
        for a in range(0, 360, 45):
            ang = math.radians(a)
            dr.line([(cxp + r * 0.4 * math.cos(ang), cyp + r * 0.4 * math.sin(ang)),
                     (cxp + r * 1.3 * math.cos(ang), cyp + r * 1.3 * math.sin(ang))],
                    fill=col, width=2)
    elif mode == "swing":
        dr.polygon([(cxp, cyp - r), (cxp + r, cyp + r), (cxp - r, cyp + r)],
                   fill=col, outline=(20, 20, 30, 255))
    dr.ellipse([cxp - 2, cyp - 2, cxp + 2, cyp + 2], fill=(255, 0, 128, 255))


def _draw_hud(dr, st: S.SceneState, t: float, tl, w: int, h: int,
              level: Level) -> None:
    f = _font(16)
    bar = tl.bar_at_time(t)
    txt = (f"t={t:7.3f}s  bar={bar:6.2f}  x={tl.x_at_time(t):7.0f}  "
           f"zoom={st.zoom:.2f}")
    dr.rectangle([(0, 0), (w, 24)], fill=(0, 0, 0, 150))
    dr.text((8, 4), txt, font=f, fill=(255, 255, 255, 230))
    if st.shake > 0.5:
        dr.text((w - 130, 4), f"SHAKE {st.shake:.1f}", font=f,
                fill=(255, 120, 120, 230))
