"""Test individual Geometric Dash objects in Web Dashers and record behaviour.

For each object we build a minimal level: a long run-in, the object placed at
a known x, then open space. We then play it with NO input and with a single
jump, and record:

  * whether the player dies, and at what x (=> does it collide?)
  * whether the player's mode / gravity / size changes (=> is it a portal?)
  * whether the player passes straight through (=> decoration)

Results are written to data/objects_tested.json, which
build_object_catalog.py merges into data/objects.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from clinecircles import gamedata as gd          # noqa: E402
from clinecircles.level import Level              # noqa: E402
from clinecircles.model import LevelObject        # noqa: E402
from clinecircles.serialization import (          # noqa: E402
    build_level_string, compress_level_string,
)
from wd_harness import WebDashers                 # noqa: E402

CENTER_X = 419.0
TEST_X = 600.0          # where the object under test sits
GROUND = 15.0           # centre y of a ground-level object
FLOAT = 75.0            # centre y of a floating row

# id -> (label, y placement)
GROUND_TESTS = [
    (1, "solid block at ground level", GROUND),
    (2, "grid-topped block at ground level", GROUND),
    (5, "inner-square block at ground level", GROUND),
    (90, "coloured block at ground level", GROUND),
    (1, "solid block floating 2 blocks up", FLOAT),
    (8, "ground spike", GROUND),
    (39, "half spike", GROUND),
    (103, "small spike", GROUND),
    (144, "invisible spike", GROUND),
    (135, "thorn pit hazard", GROUND),
    (1705, "large saw blade", GROUND + 60),
    (1706, "medium saw blade", GROUND + 30),
    (12, "cube portal", GROUND),
    (13, "ship portal", GROUND),
    (47, "ball portal", GROUND),
    (111, "ufo portal", GROUND),
    (660, "wave portal", GROUND),
    (745, "robot portal", GROUND),
    (1331, "spider portal", GROUND),
    (10, "blue gravity portal (normal)", GROUND),
    (11, "yellow gravity portal (inverted)", GROUND),
    (99, "green size portal (normal)", GROUND),
    (101, "pink size portal (small)", GROUND),
    (200, "speed portal 0.5x", GROUND),
    (202, "speed portal 2x", GROUND),
    (203, "speed portal 3x", GROUND),
    (1334, "speed portal 4x", GROUND),
    (35, "yellow jump pad", GROUND),
    (1332, "red jump pad", GROUND),
    (67, "blue gravity pad", GROUND),
    (36, "yellow jump orb", GROUND + 30),
    (1333, "red jump orb", GROUND + 30),
    (84, "blue gravity orb", GROUND + 30),
    (1022, "green gravity orb", GROUND + 30),
]


def build_test_level(obj_id: int, y: float, jump_expected: bool = False):
    lv = Level(name=f"test {obj_id}", creator="Cline", song_id=0,
               speed=gd.Speed.NORMAL)
    lv.add(LevelObject(obj_id, TEST_X, y))
    return lv


def probe(wd, seconds: float) -> dict:
    wd.sample_start()
    t_end = time.time() + seconds
    deaths: list[float] = []
    max_px = -1e9
    flags: set[str] = set()
    last_dead = 0
    while time.time() < t_end:
        st = wd.state()
        if st is None:
            time.sleep(0.01); continue
        px = st["x"] - CENTER_X
        if st["dead"] and not last_dead:
            deaths.append(round(px, 1))
        last_dead = st["dead"]
        if not st["dead"]:
            max_px = max(max_px, px)
        for f in st.get("flags", []) or []:
            flags.add(f)
        time.sleep(0.004)
    return {"deaths": deaths, "max_px": round(max_px, 1),
            "flags": sorted(flags)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    tests = GROUND_TESTS
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        tests = [t for t in tests if t[0] in wanted]

    results: dict[int, dict] = {}
    if os.path.exists("data/objects_tested.json"):
        with open("data/objects_tested.json") as fh:
            results = {int(k): v for k, v in json.load(fh).items()}

    with WebDashers() as wd:
        for oid, label, y in tests:
            lv = build_test_level(oid, y)
            packed = compress_level_string(build_level_string(lv))
            wd.install_level(label, packed, song_id=-1, created_id=980000)
            if not wd.start_level(980000) or not wd.wait_ready():
                print(f"  {oid:5d} {label:36s} FAILED TO START")
                continue
            out = probe(wd, args.seconds)
            # The player is killed by the object if it never gets meaningfully
            # past it. Otherwise it ran through / over it.
            reached_past = out["max_px"] > TEST_X + 60
            if out["deaths"] and not reached_past:
                verdict = "BLOCKS or kills the player"
            elif out["flags"]:
                verdict = "triggers a state change"
            else:
                verdict = "player passes through"
            note = {
                "label": label,
                "placement_y": y,
                "verdict": verdict,
                "deaths": out["deaths"][:3],
                "max_x": out["max_px"],
                "flags": out["flags"],
                "engine": "Web Dashers (browser GD reimplementation)",
            }
            results[oid] = note
            print(f"  {oid:5d} {label:36s} -> {verdict:18s} "
                  f"max_x={out['max_px']:8.1f} flags={out['flags']}")
            time.sleep(0.2)

    with open("data/objects_tested.json", "w") as fh:
        json.dump({str(k): v for k, v in sorted(results.items())}, fh, indent=1)
    print(f"\nwrote data/objects_tested.json ({len(results)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
