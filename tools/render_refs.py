"""Render every reference level to contact sheets + detail zooms.

For each .gmd in rflevels/ that actually contains level data:
  * a CONTACT SHEET: the whole level as a stack of tiles, so the entire
    structure can be seen at once
  * DETAIL ZOOMS: close-ups at points chosen by object density, so the
    construction technique is visible

Output: out/refs/<level>/
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import gd_visualize as V  # noqa: E402

REFS = os.path.join(os.path.dirname(__file__), "..", "rflevels")
OUT = os.path.join(os.path.dirname(__file__), "..", "out", "refs")


def densest_windows(xs: list[float], width: float, n: int) -> list[float]:
    """Pick n start-x values for the densest windows of the given width."""
    if not xs:
        return []
    xs = sorted(xs)
    best: list[tuple[int, float]] = []
    i = 0
    for j in range(len(xs)):
        while xs[j] - xs[i] > width:
            i += 1
        best.append((j - i + 1, xs[i]))
    best.sort(key=lambda t: -t[0])
    chosen: list[float] = []
    for _, start in best:
        if all(abs(start - c) > width * 0.75 for c in chosen):
            chosen.append(start)
        if len(chosen) >= n:
            break
    return sorted(chosen)


def contact_sheet(level, engine, tiles: int = 6, tile_units: float = 1700.0,
                  pxu: float = 0.62, y0: float = -90.0, y1: float = 430.0):
    xs = [o.x for o in level.objects]
    xmin, xmax = (min(xs), max(xs)) if xs else (0, 0)
    span = max(1.0, xmax - xmin)
    starts = densest_windows(xs, tile_units, tiles)
    imgs = []
    for s in starts:
        img, drawn, total = V.render(level, engine, s, s + tile_units, pxu,
                                     y0, y1, show_grid=True)
        imgs.append((s, img, drawn, total))
    if not imgs:
        return None, 0
    W = max(i[1].width for i in imgs)
    label_h = 22
    H = sum(i[1].height + label_h for i in imgs)
    sheet = Image.new("RGB", (W, H), (12, 13, 22))
    draw = ImageDraw.Draw(sheet)
    y = 0
    for s, img, drawn, total in imgs:
        draw.text((6, y + 5), f"x={s:.0f}  ({s/30:.0f} blocks)   "
                              f"{drawn}/{total} objects drawn",
                  fill=(180, 200, 255))
        sheet.paste(img.convert("RGB"), (0, y + label_h))
        y += img.height + label_h
    return sheet, len(imgs)


def main() -> int:
    engine = V.load_engine()
    if not engine:
        print("engine_defs.json missing - run bash tools/wd_setup.sh")
        return 1
    os.makedirs(OUT, exist_ok=True)
    names = sorted(f for f in os.listdir(REFS) if f.endswith(".gmd"))
    for name in names:
        path = os.path.join(REFS, name)
        raw = open(path, errors="replace").read()
        stem = os.path.splitext(name)[0]
        if "<k>k4</k>" not in raw:
            print(f"{stem:26s} SKIP - metadata stub, no object data")
            continue
        try:
            level = V.read_gmd(path)
        except Exception as exc:
            print(f"{stem:26s} SKIP - {exc}")
            continue
        if not level.objects:
            print(f"{stem:26s} SKIP - 0 objects")
            continue
        d = os.path.join(OUT, stem)
        os.makedirs(d, exist_ok=True)
        sheet, n = contact_sheet(level, engine)
        if sheet is not None:
            sheet.save(os.path.join(d, "contact_sheet.png"))
        # detail zooms
        xs = [o.x for o in level.objects]
        for i, s in enumerate(densest_windows(xs, 420.0, 3)):
            img, drawn, total = V.render(level, engine, s, s + 420, 2.1,
                                         -60, 400, show_grid=True)
            img.convert("RGB").save(os.path.join(d, f"zoom_{i}.png"))
        print(f"{stem:26s} {len(level.objects):7d} objects -> "
              f"{n} tiles + zooms in out/refs/{stem}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
