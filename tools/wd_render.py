"""Render a section of a level through Web Dashers (a real GD-compatible engine).

This is the visual feedback loop: my own PIL renderer does not do backgrounds,
glow, blending or colour-channel correctness, so it lies. Web Dashers does.

  python3 tools/wd_render.py --section intro --shots 6
"""

from __future__ import annotations

import argparse
import copy
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from clinecircles.level import Level                      # noqa: E402
from clinecircles.serialization import (                    # noqa: E402
    build_level_string, compress_level_string,
)
from wd_harness import WebDashers                           # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "out")
CENTER_X = 419.0


def extract(level, x0, x1):
    lo = max(0.0, x0 - 400.0)
    lv = Level(name="render", creator="Cline", song_id=0)
    kept = []
    for o in level.objects:
        if lo <= o.x <= x1:
            c = copy.deepcopy(o)
            c.x -= lo
            kept.append(c)
    lv.objects = kept
    lv.colors = level.colors
    return lv


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", default="intro")
    ap.add_argument("--shots", type=int, default=5)
    ap.add_argument("--span", type=float, default=1600.0)
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()

    from clinecircles.anticline_build import assemble
    res, level = assemble()
    if args.section not in res.section_x:
        print("sections:", list(res.section_x))
        return 1
    x0, x1 = res.section_x[args.section]
    part = extract(level, x0, min(x1, x0 + args.span))
    packed = compress_level_string(build_level_string(part))
    print(f"{args.section}: {len(part.objects)} objects, x {x0:.0f}..{x1:.0f}")

    d = args.outdir or os.path.join(OUT, "v4", "engine")
    os.makedirs(d, exist_ok=True)
    with WebDashers() as wd:
        wd.install_level("anticline render", packed, song_id=-1,
                         created_id=990001)
        if not wd.start_level(990001) or not wd.wait_ready():
            print("failed to start")
            return 1
        wd.set_total(x1 - x0)
        wd.hold()
        for i in range(args.shots):
            wd.page.wait_for_timeout(850)
            st = wd.state() or {}
            px = (st.get("x") or 0) - CENTER_X
            wd.screenshot(os.path.join(d, f"{args.section}_{i}_x{int(px)}.png"))
            print(f"  shot {i}: x={px:.0f} y={st.get('y')} mode={st.get('mode')}")
        wd.release()
    return 0


if __name__ == "__main__":
    sys.exit(main())
