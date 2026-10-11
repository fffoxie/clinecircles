"""CLI: build, validate and export the CLINE CIRCLES level.

    python -m clinecircles build     # generate out/CLINE CIRCLES.gmd + info
    python -m clinecircles info      # print the section/timing plan only
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .layout import build_level
from .serialization import build_level_string, write_gmd
from .validate import validate_level

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "out")


def cmd_info(args: argparse.Namespace) -> int:
    res = build_level()
    t = res.track
    print(f"CLINE CIRCLES  |  {t.title} - {t.artist} (NG {t.song_id})")
    print(f"  {t.bpm} BPM, beat {t.beat_s:.5f}s, bar {t.bar_s:.5f}s, "
          f"phase {t.phase_s:.4f}s")
    print(f"  length: {res.length_units:.0f} units = "
          f"{res.length_blocks:.1f} blocks "
          f"({res.timeline.x_at_bar(44) and ''}"
          f"{t.time_at_bar(44):.2f}s)")
    print("  sections:")
    for sec in res.timeline.segments:
        print(f"    speed {sec.speed.name} from bar {sec.start_bar}")
    for name, (x0, x1) in res.section_x.items():
        print(f"    {name:24s} x {x0:9.0f} -> {x1:9.0f}  "
              f"({(x1 - x0) / 30:.1f} blocks)")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    res = build_level()
    level = res.level

    rep = validate_level(level)
    print(f"CLINE CIRCLES  |  {len(level.objects)} objects")
    print(rep.render())

    name = "CLINE CIRCLES"
    gmd_path = os.path.join(OUT_DIR, f"{name}.gmd")
    ls_path = os.path.join(OUT_DIR, f"{name}.levelstring.txt")
    write_gmd(level, gmd_path)
    with open(ls_path, "w", encoding="utf-8") as fh:
        fh.write(build_level_string(level))

    meta = {
        "name": name,
        "version": __version__,
        "song": {"title": res.track.title, "artist": res.track.artist,
                 "newgrounds_id": res.track.song_id},
        "bpm": res.track.bpm,
        "objects": len(level.objects),
        "length_units": round(res.length_units, 2),
        "length_blocks": round(res.length_blocks, 2),
        "duration_s": round(res.track.time_at_bar(44), 3),
        "sections": {k: [round(v[0], 2), round(v[1], 2)]
                     for k, v in res.section_x.items()},
        "validation": {"ok": rep.ok, "errors": rep.errors,
                       "warnings": rep.warnings},
    }
    with open(os.path.join(OUT_DIR, "level_info.json"), "w") as fh:
        json.dump(meta, fh, indent=2)

    print(f"\n  wrote {gmd_path}")
    print(f"  wrote {ls_path}")
    print(f"  wrote {os.path.join(OUT_DIR, 'level_info.json')}")
    return 0 if rep.ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="clinecircles")
    ap.add_argument("command", choices=["build", "info"])
    args = ap.parse_args(argv)
    return {"build": cmd_build, "info": cmd_info}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
