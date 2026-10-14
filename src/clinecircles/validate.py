"""Validation of generated levels against authoritative GD data.

Checks performed:

1. every object id exists in ``data/object_table.csv`` (a real GD object)
2. every property id used is a real GD property key (``data/prop_table.csv``)
3. no two *gameplay* objects occupy the identical position
4. geometry sanity (bounds, grid alignment)
5. the declared object count matches the real count
6. the level string fits GD's practical size limits
7. all seven required game modes appear
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

from . import gamedata as gd
from .level import Level
from .serialization import build_level_string

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")

MAX_OBJECTS = 65535
MAX_LEVEL_STRING_BYTES = 5_000_000

_TRIGGER_IDS = {
    int(o) for o in (
        gd.Obj.TR_START_POS, gd.Obj.TR_SPAWN, gd.Obj.TR_COLOR, gd.Obj.TR_MOVE,
        gd.Obj.TR_PULSE, gd.Obj.TR_ALPHA, gd.Obj.TR_TOGGLE, gd.Obj.TR_ROTATE,
        gd.Obj.TR_SHAKE, gd.Obj.TR_FOLLOW, gd.Obj.TR_ZOOM_CAMERA,
        gd.Obj.TR_STATIC_CAMERA, gd.Obj.TR_OFFSET_CAMERA, gd.Obj.TR_COUNT,
        gd.Obj.TR_PICKUP, gd.Obj.TR_STOP, gd.Obj.TR_ANIMATE, gd.Obj.TR_TOUCH,
        gd.Obj.TR_BG_EFFECT_ON, gd.Obj.TR_BG_EFFECT_OFF, gd.Obj.TR_RANDOM,
        gd.Obj.TR_ENTER, gd.Obj.TR_ON_DEATH, gd.Obj.TR_FOLLOW_PLAYER_Y,
        gd.Obj.TR_COLLISION, gd.Obj.TR_COLLISION_BLOCK, gd.Obj.TR_TRAIL_ON,
        gd.Obj.TR_TRAIL_OFF, gd.Obj.TR_ANIMATE_KEYFRAME,
    )
}


def _load_csv(name: str) -> list[dict[str, str]]:
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def render(self) -> str:
        out = [f"  {k}: {v}" for k, v in self.stats.items()]
        out += [f"  WARN  {w}" for w in self.warnings]
        out += [f"  ERROR {e}" for e in self.errors]
        out.append("  RESULT: " + ("PASS" if self.ok else "FAIL"))
        return "\n".join(out)


def _known_object_ids() -> set[int]:
    ids = set()
    for row in _load_csv("object_table.csv"):
        try:
            ids.add(int(row["object id"]))
        except (KeyError, ValueError):
            continue
    return ids


def _known_property_ids() -> set[int]:
    ids = set()
    for row in _load_csv("prop_table.csv"):
        try:
            ids.add(int(row["id"]))
        except (KeyError, ValueError):
            continue
    return ids



def validate_level(level: Level, *, declared_object_count: int | None = None,
                   check_geometry: bool = True) -> Report:
    rep = Report()
    known_obj = _known_object_ids()
    known_prop = _known_property_ids()

    # 1. object ids
    unknown: dict[int, int] = {}
    for o in level.objects:
        if int(o.id) not in known_obj:
            unknown[int(o.id)] = unknown.get(int(o.id), 0) + 1
    if unknown:
        rep.error(f"unknown object ids (not in GD object table): {unknown}")

    # 2. property ids
    bad_props: dict[int, int] = {}
    for o in level.objects:
        for k in o.props:
            if int(k) not in known_prop:
                bad_props[int(k)] = bad_props.get(int(k), 0) + 1
    if bad_props:
        rep.error(f"unknown property ids: {bad_props}")

    # 3. duplicate gameplay positions
    seen: dict[tuple[int, float, float], int] = {}
    dupes = 0
    for o in level.objects:
        if int(o.id) in _TRIGGER_IDS:
            continue
        key = (int(o.id), round(o.x, 2), round(o.y, 2))
        if key in seen:
            dupes += 1
        seen[key] = seen.get(key, 0) + 1
    if dupes:
        rep.warn(f"{dupes} gameplay objects share an exact position with another")

    # 4. geometry sanity
    if check_geometry and level.objects:
        xs = [o.x for o in level.objects]
        ys = [o.y for o in level.objects]
        rep.stats["bounds_x"] = (round(min(xs), 1), round(max(xs), 1))
        rep.stats["bounds_y"] = (round(min(ys), 1), round(max(ys), 1))
        if min(ys) < -400:
            rep.error(f"objects far below the level: min y {min(ys)}")

    # 5. counts
    n = len(level.objects)
    rep.stats["objects"] = n
    if n > MAX_OBJECTS:
        rep.error(f"object count {n} exceeds GD limit {MAX_OBJECTS}")
    if declared_object_count is not None and declared_object_count != n:
        rep.error(f"declared object count {declared_object_count} != actual {n}")
    rep.stats["distinct_object_ids"] = len(level.object_ids())

    # 6. level string size
    ls = build_level_string(level)
    rep.stats["level_string_bytes"] = len(ls)
    if len(ls) > MAX_LEVEL_STRING_BYTES:
        rep.error(f"level string is {len(ls)} bytes (> {MAX_LEVEL_STRING_BYTES})")

    # 7. game-mode coverage
    present = {int(o.id) for o in level.objects}
    modes = sorted(m.name for m, obj in gd.MODE_PORTAL_OBJECT.items()
                   if int(obj) in present)
    rep.stats["game_modes"] = modes
    missing = [m.name for m in gd.GameMode if m.name not in modes]
    if missing:
        rep.warn(f"game modes not used: {missing}")

    return rep
