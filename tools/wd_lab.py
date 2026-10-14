"""Playtest one section of CLINE CIRCLES in Web Dashers.

Problem solved here: the game re-clamps the camera every frame, so teleporting
the player does not persist. Instead we EXTRACT a section's objects into a
standalone level, shifted so the section begins at x=0. The player then starts
inside the section naturally and can be played with normal input.

Usage:  python3 tools/wd_lab.py --version v1 --section intro --seconds 25
        python3 tools/wd_lab.py --version v1 --all
"""

from __future__ import annotations

import argparse
import copy
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from clinecircles import gamedata as gd            # noqa: E402
from clinecircles.layout import build_level         # noqa: E402
from clinecircles.layout.plan import SECTIONS       # noqa: E402
from clinecircles.level import Level                # noqa: E402
from clinecircles.serialization import (            # noqa: E402
    build_level_string, compress_level_string,
)
from wd_harness import WebDashers                   # noqa: E402

CENTER_X = 419.0
LEAD_IN = 760.0


def extract(res, name: str) -> tuple[Level, list[float], float]:
    x0, x1 = res.section_x[name]
    lo = max(0.0, x0 - LEAD_IN)
    spec = next(s for s in SECTIONS if s.name == name)
    lv = Level(name=f"CLINE {name}", creator="Cline", song_id=0,
               speed=spec.speed, game_mode=gd.GameMode.CUBE)
    kept = []
    for o in res.level.objects:
        if lo <= o.x <= x1:
            # COPY: shifting in place would corrupt the shared level and make
            # every later section's test meaningless.
            c = copy.deepcopy(o)
            c.x -= lo
            kept.append(c)
    lv.objects = kept
    haz = sorted(h.x0 - lo for h in res.builder.hazards
                 if lo <= h.x0 <= x1)
    return lv, haz, x1 - lo


def autopilot(wd, hazards, seconds, shots_dir=None, shot_prefix="",
              length=0.0) -> dict:
    t_end = time.time() + seconds
    pressed = False
    press_until = 0.0
    cooldown = 0.0
    next_shot = time.time() + 2.5
    deaths: list[float] = []
    max_px = -1e9
    modes: set[str] = set()
    last_dead = 0
    shot_i = 0
    while time.time() < t_end:
        st = wd.state()
        if st is None:
            time.sleep(0.01); continue
        px = st["x"] - CENTER_X
        py, mode, dead = st["y"], st["mode"], st["dead"]
        modes.add(mode)
        if dead and not last_dead:
            deaths.append(round(px, 1))
        last_dead = dead
        if not dead:
            max_px = max(max_px, px)
        now = time.time()
        if shots_dir and now >= next_shot:
            wd.screenshot(os.path.join(shots_dir,
                                       f"{shot_prefix}_{shot_i:02d}_x{int(max(0,px))}.png"))
            shot_i += 1
            next_shot = now + 2.5
        want = False
        if mode in ("cube", "robot", "ball", "spider"):
            if st["g"] and now >= cooldown:
                for h in hazards:
                    d = h - px
                    if d > -25:
                        if 44.0 <= d <= 104.0:
                            want = True
                        break
        else:
            target = 115.0
            want = py < target
        if want and not pressed:
            wd.hold(); pressed = True; press_until = now + 0.10
        elif pressed and (not want or now >= press_until):
            wd.release(); pressed = False; cooldown = now + 0.05
        time.sleep(0.002)
    if pressed:
        wd.release()
    return {"deaths": deaths, "max_px": max_px, "modes": sorted(modes),
            "length": length}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    ap.add_argument("--section", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--seconds", type=float, default=22.0)
    ap.add_argument("--shots", action="store_true")
    args = ap.parse_args()

    res = build_level()
    shots = os.path.join("/workspace/out", args.version, "screenshots")
    os.makedirs(shots, exist_ok=True)
    names = list(res.section_x) if args.all else [args.section]
    results = {}
    with WebDashers() as wd:
        for name in names:
            lv, haz, length = extract(res, name)
            packed = compress_level_string(build_level_string(lv))
            wd.install_level(f"CLINE {name}", packed, song_id=-1,
                             created_id=970000)
            if not wd.start_level(970000) or not wd.wait_ready():
                print(f"  [{name}] failed to start"); continue
            wd.set_total(length)
            wd.sample_start()
            out = autopilot(wd, haz, args.seconds,
                            shots if args.shots else None, name, length)
            pct = 100.0 * out["max_px"] / length if length else 0
            results[name] = out
            print(f"  [{name:22s}] len={length:7.0f}  max_x={out['max_px']:8.1f} "
                  f"({pct:5.1f}%)  modes={out['modes']}  "
                  f"deaths={out['deaths'][:4]}")
    import json
    with open(os.path.join("/workspace/out", args.version,
                           "section_playtest.json"), "w") as fh:
        json.dump({k: {kk: vv for kk, vv in v.items()} for k, v in results.items()},
                  fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
