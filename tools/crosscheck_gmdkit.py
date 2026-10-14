"""Cross-validate a generated .gmd against gmdkit (independent implementation).

This is the strongest available evidence short of opening Geometry Dash: a
completely separate library parses our file, decompresses the level string, and
yields the same object list.

Usage:  python3 tools/crosscheck_gmdkit.py out/CLINE_CIRCLES.gmd
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clinecircles.serialization import read_gmd  # noqa: E402


def main(path: str) -> int:
    ours = read_gmd(path)
    print(f"ours: name={ours.name!r} objects={len(ours.objects)} song={ours.song_id}")

    try:
        from gmdkit.models.level import Level as GmdkitLevel
    except ImportError:
        print("SKIP: gmdkit not installed (pip install gmdkit)")
        return 0

    theirs = GmdkitLevel.from_file(path)
    their_objs = theirs.objects
    print(f"gmdkit: name={theirs.get('k2')!r} objects={len(their_objs)} "
          f"k45={theirs.get('k45')}")

    ok = True
    if len(their_objs) != len(ours.objects):
        print(f"MISMATCH object count: ours={len(ours.objects)} theirs={len(their_objs)}")
        ok = False

    # compare the first N objects deeply (id/x/y match)
    n = min(len(their_objs), len(ours.objects))
    bad = 0
    for i in range(n):
        a, b = ours.objects[i], their_objs[i]
        bid = b.get(1)
        if int(a.id) != int(bid) or abs(a.x - float(b.get(2))) > 1e-6 \
                or abs(a.y - float(b.get(3))) > 1e-6:
            bad += 1
            if bad <= 5:
                print(f"  object {i}: ours=({a.id},{a.x},{a.y}) "
                      f"theirs=({bid},{b.get(2)},{b.get(3)})")
    if bad:
        print(f"MISMATCH: {bad}/{n} objects differ")
        ok = False

    if theirs.get("k2") != ours.name:
        print(f"MISMATCH name: {theirs.get('k2')!r} != {ours.name!r}")
        ok = False

    print("CROSSCHECK PASS" if ok else "CROSSCHECK FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else
                          "out/CLINE_CIRCLES.gmd"))
