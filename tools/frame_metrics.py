"""Measure a rendered frame numerically - the substitute for having eyes.

A level that LOOKS full has, roughly:
  * high coverage      - most of the frame is not empty background
  * high colour spread - several distinct hues, not monochrome
  * high edge density  - lots of small detail, not big flat blocks

This computes those from a screenshot or from our own renderer, so decoration
can be tuned against numbers when the image channel is unavailable.

  python3 tools/frame_metrics.py out/v4/engine/*.png
"""

from __future__ import annotations

import glob
import sys

from PIL import Image


def metrics(path: str) -> dict:
    im = Image.open(path).convert("RGB")
    im.thumbnail((640, 640))
    w, h = im.size
    px = list(im.getdata())
    n = len(px)

    # dominant colour = background
    from collections import Counter
    q = [(r // 24, g // 24, b // 24) for r, g, b in px]
    bg, bg_n = Counter(q).most_common(1)[0]

    def is_bg(c):
        return (c[0] // 24, c[1] // 24, c[2] // 24) == bg

    non_bg = sum(1 for c in px if not is_bg(c))
    coverage = non_bg / n

    # colour spread: how many distinct coarse hues among non-background pixels
    hues = set()
    sat_sum = 0
    for r, g, b in px:
        if is_bg((r, g, b)):
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        sat_sum += (mx - mn)
        if mx > 40:
            hues.add((r // 64, g // 64, b // 64))
    colour_spread = len(hues)
    mean_sat = sat_sum / max(1, non_bg)

    # edge density: neighbouring pixels that differ a lot
    edges = 0
    for y in range(1, h, 2):
        base = y * w
        for x in range(1, w, 2):
            i = base + x
            a, b2 = px[i], px[i - 1]
            if abs(a[0] - b2[0]) + abs(a[1] - b2[1]) + abs(a[2] - b2[2]) > 90:
                edges += 1
    edge_density = edges / max(1, (w // 2) * (h // 2))

    return {"file": path.split("/")[-1], "coverage": round(coverage, 3),
            "colour_spread": colour_spread, "mean_saturation": round(mean_sat, 1),
            "edge_density": round(edge_density, 3)}


def main() -> int:
    paths = []
    for a in sys.argv[1:]:
        paths.extend(glob.glob(a))
    if not paths:
        print("usage: frame_metrics.py <images...>")
        return 1
    print(f"{'file':34s} {'cover':>6s} {'hues':>5s} {'sat':>6s} {'edges':>6s}")
    for p in sorted(paths):
        m = metrics(p)
        print(f"{m['file']:34s} {m['coverage']:6.3f} {m['colour_spread']:5d} "
              f"{m['mean_saturation']:6.1f} {m['edge_density']:6.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
