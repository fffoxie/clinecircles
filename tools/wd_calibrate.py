"""Empirically calibrate the player's jump arc in Web Dashers.

Geometry Dash (and Web Dashers) provides the ground automatically, so an empty
level is playable. This measures, for each speed portal, the cube's jump height
and jump length in the engine's own units, by reading the real PlayerState.

Usage:  python3 tools/wd_calibrate.py
"""

from __future__ import annotations

import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from clinecircles import gamedata as gd          # noqa: E402
from clinecircles.level import Level              # noqa: E402
from clinecircles.serialization import (          # noqa: E402
    build_level_string, compress_level_string,
)
from wd_harness import OUT, WebDashers            # noqa: E402


def empty_level(speed: gd.Speed) -> Level:
    lv = Level(name=f"calib {int(speed)}", creator="Cline", song_id=0)
    lv.speed = speed
    return lv


def measure(wd: WebDashers) -> dict | None:
    """Tap once and return the resulting jump arc."""
    wd.sample_start()
    wd.page.wait_for_timeout(500)
    wd.tap(60)
    wd.page.wait_for_timeout(1600)
    tr = wd.trace()
    if len(tr) < 6:
        return None
    # find takeoff: first frame where onGround goes 1 -> 0
    takeoff = None
    for i in range(1, len(tr)):
        if tr[i - 1]["g"] == 1 and tr[i]["g"] == 0 and not tr[i]["dead"]:
            takeoff = i
            break
    if takeoff is None:
        return None
    # landing: next frame after takeoff with g == 1
    land = None
    for j in range(takeoff + 1, len(tr)):
        if tr[j]["g"] == 1:
            land = j
            break
    if land is None:
        return None
    x0, x1 = tr[takeoff]["x"], tr[land]["x"]
    ys = [tr[k]["y"] for k in range(takeoff, land + 1)]
    return {"length": x1 - x0, "height": max(ys) - tr[takeoff]["y"],
            "x0": x0, "frames": land - takeoff,
            "peak_y": max(ys), "start_y": tr[takeoff]["y"]}


def main() -> int:
    results: dict[int, list[dict]] = {}
    with WebDashers() as wd:
        for sp in (gd.Speed.SLOW, gd.Speed.NORMAL, gd.Speed.FAST,
                   gd.Speed.VERY_FAST, gd.Speed.SUPER_FAST):
            lv = empty_level(sp)
            wd.install_level(f"calib{int(sp)}",
                             compress_level_string(build_level_string(lv)),
                             song_id=-1, created_id=910000 + int(sp))
            if not wd.start_level(910000 + int(sp)):
                print("start failed for speed", int(sp))
                continue
            if not wd.wait_ready():
                print("not ready for speed", int(sp))
                continue
            wd.page.wait_for_timeout(1200)
            got = []
            for _ in range(4):
                m = measure(wd)
                if m and m["length"] > 1:
                    got.append(m)
            results[int(sp)] = got
            if got:
                L = statistics.median(m["length"] for m in got)
                H = statistics.median(m["height"] for m in got)
                print(f"speed {int(sp)} ({gd.Speed(sp).name:10s}) "
                      f"jump length {L:7.2f} u = {L/30:5.2f} blocks | "
                      f"height {H:6.2f} u = {H/30:4.2f} blocks  (n={len(got)})")
            else:
                print(f"speed {int(sp)}: no measurement")
        # sanity: capture the empty level running
        wd.screenshot(f"{OUT}/wd_calib.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
