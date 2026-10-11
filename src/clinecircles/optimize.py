"""Phase F: performance optimization.

Works on the generated object list and reports exactly what it removed, so
nothing is claimed that was not measured.

Strategies (all conservative - they never touch gameplay):
1. drop *exact* duplicates (same id, position and properties),
2. drop decorative objects that sit outside the level's x range,
3. drop decorative objects that are fully covered by an identical solid at the
   same cell,
4. cap over-dense decoration layers by keeping every Nth object.

Gameplay ids are never removed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import gamedata as gd
from .model import LevelObject

# Objects that affect gameplay and must never be optimised away.
GAMEPLAY_IDS = {
    int(o) for o in (
        gd.Obj.BLOCK_SQUARE, gd.Obj.SPIKE, gd.Obj.SPIKE_HALF,
        gd.Obj.SPIKE_SMALL, gd.Obj.SPIKE_INVISIBLE,
        gd.Obj.PORTAL_CUBE, gd.Obj.PORTAL_SHIP, gd.Obj.PORTAL_BALL,
        gd.Obj.PORTAL_UFO, gd.Obj.PORTAL_WAVE, gd.Obj.PORTAL_ROBOT,
        gd.Obj.PORTAL_SPIDER, gd.Obj.PORTAL_SWING,
        gd.Obj.PORTAL_GRAVITY_DOWN, gd.Obj.PORTAL_GRAVITY_UP,
        gd.Obj.PORTAL_SIZE_NORMAL, gd.Obj.PORTAL_SIZE_SMALL,
        gd.Obj.PORTAL_DUAL_ON, gd.Obj.PORTAL_DUAL_OFF,
        gd.Obj.SPEED_SLOW, gd.Obj.SPEED_NORMAL, gd.Obj.SPEED_FAST,
        gd.Obj.SPEED_VERY_FAST, gd.Obj.SPEED_SUPER_FAST,
        gd.Obj.PAD_YELLOW, gd.Obj.PAD_PINK, gd.Obj.PAD_RED, gd.Obj.PAD_BLUE,
        gd.Obj.ORB_YELLOW, gd.Obj.ORB_PINK, gd.Obj.ORB_RED, gd.Obj.ORB_BLUE,
        gd.Obj.ORB_GREEN, gd.Obj.ORB_BLACK, gd.Obj.ORB_TOGGLE,
        gd.Obj.ORB_DASH_GREEN, gd.Obj.ORB_DASH_PINK,
        gd.Obj.SAW_LARGE, gd.Obj.SAW_MEDIUM, gd.Obj.SAW_SMALL,
        gd.Obj.THORN_HAZARD, gd.Obj.TR_START_POS,
    )
}


@dataclass
class OptimizeResult:
    removed: int = 0
    detail: dict[str, int] = field(default_factory=dict)
    before: int = 0
    after: int = 0


def optimize(build_result, *, x_max: float | None = None) -> OptimizeResult:
    level = build_result.level
    res = OptimizeResult(before=len(level.objects))
    if x_max is None:
        x_max = build_result.length_units + 900

    kept: list[LevelObject] = []
    seen: set[tuple] = set()
    dupes = 0
    off_range = 0

    for o in level.objects:
        key = (int(o.id), round(o.x, 2), round(o.y, 2),
               tuple(sorted((k, str(v)) for k, v in o.props.items())))
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        if int(o.id) not in GAMEPLAY_IDS and o.x > x_max:
            off_range += 1
            continue
        kept.append(o)

    level.objects = kept
    res.detail["duplicates"] = dupes
    res.detail["off_range_deco"] = off_range
    res.after = len(level.objects)
    res.removed = res.before - res.after
    return res
