"""Smoke test: load a level built by this project into Web Dashers and play it.

    python3 tools/wd_test.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from clinecircles import gamedata as gd          # noqa: E402
from clinecircles.level import Level              # noqa: E402
from clinecircles.model import LevelObject        # noqa: E402
from clinecircles.serialization import (          # noqa: E402
    build_level_string, compress_level_string,
)
from wd_harness import OUT, WebDashers            # noqa: E402


def make_test_level() -> Level:
    """Flat ground with a single spike, then a ship portal: the simplest
    possible thing that exercises movement, jumping and a mode change."""
    lv = Level(name="WD SMOKE TEST", creator="Cline", song_id=0)
    # 60 blocks of floor
    for i in range(60):
        lv.add(LevelObject(gd.Obj.BLOCK_SQUARE, 15 + i * 30, 15))
    # one spike at block 20
    lv.add(LevelObject(gd.Obj.SPIKE, 615, 15))
    # ship portal at block 35
    lv.add(LevelObject(gd.Obj.PORTAL_SHIP, 1065, 105))
    return lv


def main() -> int:
    level = make_test_level()
    raw = build_level_string(level)
    packed = compress_level_string(raw)
    print(f"test level: {len(level.objects)} objects, "
          f"{len(raw)} bytes raw, {len(packed)} packed")

    with WebDashers() as wd:
        wd.install_level("WD SMOKE TEST", packed, song_id=-1)
        ok = wd.start_level()
        print("start_level ->", ok)
        ready = wd.wait_ready()
        print("ready ->", ready)
        if not ready:
            wd.screenshot(f"{OUT}/wd_fail.png")
            print("console:", *wd.console[-10:], sep="\n  ")
            print("errors:", *wd.errors[-5:], sep="\n  ")
            return 1

        wd.sample_start()
        print("idle 1.5s (no input)...")
        wd.page.wait_for_timeout(1500)
        s0 = wd.state()
        print("  state:", s0)

        print("tap jump...")
        wd.tap(120)
        wd.page.wait_for_timeout(1200)
        s1 = wd.state()
        print("  state:", s1)

        print("hold (fly) 2.5s...")
        wd.hold()
        wd.page.wait_for_timeout(2500)
        s2 = wd.state()
        wd.release()
        print("  state:", s2)
        print("  percent:", wd.percent())

        wd.screenshot(f"{OUT}/wd_01_smoke.png")

        trace = wd.sample()
        print(f"\ntrace frames: {len(trace)}")
        if trace:
            xs = [f["x"] for f in trace]
            print(f"  x range: {min(xs):.1f} .. {max(xs):.1f}")
            modes = sorted({f["mode"] for f in trace})
            print(f"  modes seen: {modes}")
            print(f"  deaths in trace: {sum(f['dead'] for f in trace)}")
            ys = [f["y"] for f in trace]
            print(f"  y range: {min(ys):.1f} .. {max(ys):.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
