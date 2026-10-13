"""Playtest CLINE CIRCLES in Web Dashers with a lookahead autopilot.

The autopilot presses real SPACE input, driven by the same hazard list the
generator produced, so it plays the level the way a player would: it can only
affect the game through normal input.

Usage:
  python3 tools/wd_play.py --section intro --seconds 30
  python3 tools/wd_play.py --all
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from clinecircles import gamedata as gd          # noqa: E402
from clinecircles.layout import build_level       # noqa: E402
from clinecircles.serialization import (          # noqa: E402
    build_level_string, compress_level_string,
)
from wd_harness import OUT, WebDashers            # noqa: E402

CENTER_X = 419.0          # screenWidth/2 - 150, from config.js
LEAD_MIN = 2.0            # jump when the hazard is within this window...
LEAD_MAX = 55.0           # ...measured in units ahead of the player
PRESS_S = 0.10            # how long to hold the jump


def collect_hazards(res) -> list[float]:
    return sorted(h.x0 for h in res.builder.hazards)


def collect_solids(res):
    return sorted((s.x0, s.x1, s.y0, s.y1) for s in res.builder.solids)


def autopilot(wd: WebDashers, hazards: list[float], solids, seconds: float,
              verbose: bool = True) -> dict:
    t_end = time.time() + seconds
    pressed = False
    press_until = 0.0
    cooldown = 0.0
    deaths: list[float] = []
    max_px = -1e9
    last_mode = "cube"
    last_dead = 0
    while time.time() < t_end:
        st = wd.state()
        if st is None:
            time.sleep(0.01)
            continue
        px = st["x"] - CENTER_X
        py = st["y"]
        mode = st["mode"]
        dead = st["dead"]
        last_mode = mode
        if dead and not last_dead:
            deaths.append(round(px, 1))
        last_dead = dead
        if not dead:
            max_px = max(max_px, px)

        now = time.time()
        want = False
        if mode in ("cube", "robot", "ball", "spider"):
            if st["g"] and now >= cooldown:
                for h in hazards:
                    d = h - px
                    if d > -20:
                        if LEAD_MIN <= d <= LEAD_MAX:
                            want = True
                        break
        else:
            target = 105.0
            want = py < target

        if want and not pressed:
            wd.hold(); pressed = True; press_until = now + PRESS_S
        elif pressed and (not want or now >= press_until):
            wd.release(); pressed = False; cooldown = now + 0.05
        time.sleep(0.004)
    if pressed:
        wd.release()
    return {"deaths": deaths, "max_px": max_px, "mode": last_mode}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", default="intro")
    ap.add_argument("--seconds", type=float, default=25.0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--shot", default=None)
    args = ap.parse_args()

    res = build_level()
    hazards = collect_hazards(res)
    solids = collect_solids(res)
    packed = compress_level_string(build_level_string(res.level))
    print(f"level: {len(res.level.objects)} objects, {len(hazards)} hazards, "
          f"{len(solids)} solids, {res.length_blocks:.0f} blocks")

    sx = res.section_x
    if args.all:
        runs = [(n, 0.0, res.length_units) for n in sx]
    else:
        runs = [(args.section, sx[args.section][0], sx[args.section][1])]

    with WebDashers() as wd:
        wd.install_level("CLINE CIRCLES", packed, song_id=-1, created_id=950000)
        if not wd.start_level(950000):
            print("failed to start"); return 1
        if not wd.wait_ready():
            print("not ready"); return 1
        wd.set_total(res.length_units)
        for name, x0, x1 in runs:
            wd.teleport(x0 + CENTER_X + 40)
            wd.page.wait_for_timeout(300)
            wd.sample_start()
            out = autopilot(wd, hazards, solids, args.seconds)
            print(f"  [{name:22s}] max_x={out['max_px']:9.1f} "
                  f"(section {x0:.0f}..{x1:.0f}) deaths={out['deaths'][:6]}"
                  f" last_mode={out['mode']}")
            if args.shot:
                wd.screenshot(f"{OUT}/{args.shot}_{name}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
