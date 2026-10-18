"""Render a Geometry Dash .gmd level to PNG images.

Why this exists: the browser test engine does not implement every GD object,
so reference levels cannot be *played* there. This renders them from the real
sprite sheets instead, so layouts, spacing, density and colour use can be
studied directly.

Sprites come from the game's own TexturePacker atlases (GJ_GameSheet*.png +
.json). Per-object sprite names and grid sizes come from the engine object
definitions (tools/../engine_defs.json, dumped from a GD-compatible engine).

Usage:
  python3 tools/gd_visualize.py "rflevels/Layout.gmd" --out out/refs/Layout.png
  python3 tools/gd_visualize.py "rflevels/Nine Circles.gmd" --strip --outdir out/refs
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clinecircles.serialization import read_gmd  # noqa: E402

SHEETS = "/tmp/sheets"
ENGINE_DEFS = "/tmp/wd/engine_defs.json"
BLOCK = 30.0

_atlas_cache: dict[str, tuple[Image.Image, dict]] = {}


def load_atlas(name: str):
    if name in _atlas_cache:
        return _atlas_cache[name]
    png = os.path.join(SHEETS, name + ".png")
    js = os.path.join(SHEETS, name + ".json")
    if not (os.path.exists(png) and os.path.exists(js)):
        _atlas_cache[name] = (None, {})
        return _atlas_cache[name]
    img = Image.open(png).convert("RGBA")
    with open(js) as fh:
        meta = json.load(fh)
    frames = meta.get("frames", meta)
    _atlas_cache[name] = (img, frames)
    return _atlas_cache[name]


def load_engine():
    if not os.path.exists(ENGINE_DEFS):
        return {}
    with open(ENGINE_DEFS) as fh:
        return json.load(fh)


_frame_index: dict | None = None


def _all_sheets() -> list[str]:
    out = []
    for f in sorted(os.listdir(SHEETS)):
        if f.endswith(".png"):
            out.append(f[:-4])
    return out


def _build_frame_index() -> dict:
    """frame name -> (sheet, frame dict). Built once across every atlas."""
    global _frame_index
    if _frame_index is not None:
        return _frame_index
    idx: dict = {}
    for sheet in _all_sheets():
        img, frames = load_atlas(sheet)
        if img is None:
            continue
        for name, f in frames.items():
            if name not in idx:
                idx[name] = (sheet, f)
            if name.endswith(".png"):
                idx.setdefault(name[:-4], (sheet, f))
    _frame_index = idx
    return idx


def _norm_sheet(name: str) -> str:
    for suffix in ("-uhd", "-hd", "_uhd", "_hd"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def sprite_for(oid: int, engine: dict):
    """Return (PIL image, natural_px_width) for an object id, or (None, 0)."""
    d = engine.get(str(oid))
    if not d:
        return None, 0
    frame_name = d.get("frame")
    if not frame_name:
        return None, 0
    sheet_hint = d.get("spritesheet")

    idx = _build_frame_index()
    cand = None
    if sheet_hint:
        want = _norm_sheet(sheet_hint)
        img, frames = load_atlas(want)
        if img is not None:
            cand = frames.get(frame_name) or frames.get(frame_name[:-4])
            if cand is not None:
                cand = (want, cand)
    if cand is None:
        cand = idx.get(frame_name) or idx.get(frame_name[:-4])
    if cand is None:
        return None, 0
    sheet, f = cand
    img, _frames = load_atlas(sheet)
    if img is None:
        return None, 0
    fr = f.get("frame") or f
    x, y, w, h = int(fr["x"]), int(fr["y"]), int(fr["w"]), int(fr["h"])
    crop = img.crop((x, y, x + w, y + h))
    if f.get("rotated"):
        crop = crop.transpose(Image.ROTATE_90)
    ss = f.get("sourceSize") or {"w": w, "h": h}
    sss = f.get("spriteSourceSize") or {"x": 0, "y": 0, "w": w, "h": h}
    full = Image.new("RGBA", (int(ss["w"]), int(ss["h"])), (0, 0, 0, 0))
    full.paste(crop, (int(sss.get("x", 0)), int(sss.get("y", 0))))
    return full, full.width


def tint(img: Image.Image, rgb) -> Image.Image:
    if rgb is None:
        return img
    r, g, b = rgb
    out = img.copy()
    px = out.load()
    for yy in range(out.height):
        for xx in range(out.width):
            pr, pg, pb, pa = px[xx, yy]
            if pa:
                px[xx, yy] = (pr * r // 255, pg * g // 255, pb * b // 255, pa)
    return out


def color_map(level):
    out = {}
    for ch, c in level.colors.items():
        out[int(ch)] = (c.r, c.g, c.b)
    return out


_sprite_cache: dict = {}


def get_sprite(oid: int, engine: dict, sx: float, sy: float, rot: float,
               flipx: bool, flipy: bool, target_w: float):
    key = (oid, round(sx, 3), round(sy, 3), round(rot, 1), flipx, flipy,
           round(target_w, 1))
    if key in _sprite_cache:
        return _sprite_cache[key]
    base, nat = sprite_for(oid, engine)
    if base is None or nat == 0:
        _sprite_cache[key] = None
        return None
    w = max(1, int(round(target_w)))
    h = max(1, int(round(base.height * (w / base.width))))
    img = base.resize((w, h), Image.LANCZOS)
    if flipx or flipy:
        img = img.transpose(Image.FLIP_LEFT_RIGHT if flipx else Image.FLIP_TOP_BOTTOM)
    if abs(rot) > 0.01:
        img = img.rotate(-rot, expand=True, resample=Image.BICUBIC)
    _sprite_cache[key] = img
    if len(_sprite_cache) > 4000:
        _sprite_cache.clear()
    return img


def render(level, engine: dict, x0: float, x1: float, pxu: float,
           y0: float = -120.0, y1: float = 420.0, bg=(18, 20, 34),
           show_grid: bool = True, ground_line: float = 0.0) -> Image.Image:
    W = max(1, int((x1 - x0) * pxu))
    H = max(1, int((y1 - y0) * pxu))
    canvas = Image.new("RGBA", (W, H), bg + (255,))
    draw = ImageDraw.Draw(canvas)

    if show_grid:
        step = BLOCK * pxu
        gx = x0 - (x0 % BLOCK)
        while gx < x1:
            sx = (gx - x0) * pxu
            draw.line([(sx, 0), (sx, H)], fill=(38, 42, 62, 255), width=1)
            gx += BLOCK
        gy = y0 - (y0 % BLOCK)
        while gy < y1:
            sy = H - (gy - y0) * pxu
            draw.line([(0, sy), (W, sy)], fill=(38, 42, 62, 255), width=1)
            gy += BLOCK

    if ground_line is not None and y0 <= ground_line <= y1:
        gy = H - (ground_line - y0) * pxu
        draw.line([(0, gy), (W, gy)], fill=(120, 200, 255, 255), width=2)

    colors = color_map(level)
    objs = [o for o in level.objects if x0 - 90 <= o.x <= x1 + 90]
    objs.sort(key=lambda o: (o.get(24, 0) or 0, o.get(25, 0) or 0))

    drawn = 0
    for o in objs:
        d = engine.get(str(int(o.id))) or {}
        gw = d.get("gridW") or 1
        sx_prop = o.get(128, o.get(32, 1)) or 1
        sy_prop = o.get(129, o.get(32, 1)) or 1
        try:
            sx_prop = float(sx_prop); sy_prop = float(sy_prop)
        except (TypeError, ValueError):
            sx_prop = sy_prop = 1.0
        if sx_prop == 0:
            sx_prop = 1.0
        target_w = gw * BLOCK * sx_prop * pxu
        if target_w < 1:
            continue
        img = get_sprite(int(o.id), engine, sx_prop, sy_prop,
                         float(o.get(6, 0) or 0), o.get(4) == 1, o.get(5) == 1,
                         target_w)
        if img is None:
            continue
        ch = o.get(21) or d.get("default_base_color_channel")
        rgb = colors.get(int(ch)) if ch else None
        if rgb:
            img = tint(img, rgb)
        px = int((o.x - x0) * pxu - img.width / 2)
        py = int(H - (o.y - y0) * pxu - img.height / 2)
        canvas.alpha_composite(img, (px, py))
        drawn += 1
    return canvas, drawn, len(objs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("gmd")
    ap.add_argument("--out", default=None)
    ap.add_argument("--outdir", default="out/refs")
    ap.add_argument("--pxu", type=float, default=0.55, help="pixels per unit")
    ap.add_argument("--width", type=float, default=3200.0, help="units per image")
    ap.add_argument("--strip", action="store_true")
    ap.add_argument("--y0", type=float, default=-90.0)
    ap.add_argument("--y1", type=float, default=420.0)
    ap.add_argument("--max-images", type=int, default=8)
    args = ap.parse_args()

    engine = load_engine()
    level = read_gmd(args.gmd)
    xs = [o.x for o in level.objects] or [0]
    xmin, xmax = min(xs), max(xs)
    print(f"{os.path.basename(args.gmd)}: {len(level.objects)} objects, "
          f"x {xmin:.0f}..{xmax:.0f} ({xmax/30:.0f} blocks), "
          f"name={level.name!r}")
    if not engine:
        print("WARNING: engine_defs.json missing; run node /tmp/wd/dump.js")

    os.makedirs(args.outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.gmd))[0]
    ranges = []
    if args.strip:
        n = min(args.max_images, max(1, int(math.ceil((xmax - xmin) / args.width))))
        step = (xmax - xmin) / n if n else 0
        for i in range(n):
            ranges.append((xmin + i * step, xmin + (i + 1) * step))
    else:
        ranges.append((xmin, min(xmax, xmin + args.width)))

    for i, (a, b) in enumerate(ranges):
        img, drawn, total = render(level, engine, a, b, args.pxu,
                                   args.y0, args.y1)
        out = args.out or os.path.join(args.outdir, f"{base}_{i:02d}.png")
        if len(ranges) > 1:
            out = os.path.join(args.outdir, f"{base}_{i:02d}.png")
        img.convert("RGB").save(out)
        print(f"  {out}  ({drawn}/{total} objects drawn)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
