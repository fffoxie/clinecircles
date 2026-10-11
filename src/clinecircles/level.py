"""The level container: header settings, colours, and the object list."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator

from . import gamedata as gd
from .model import Color, LevelObject, default_colors


@dataclass
class Level:
    """A whole Geometry Dash level.

    ``header`` holds the inner level-string keys (kA2, kA4, kA6 ...) that are
    not colours or objects. ``settings`` holds the .gmd plist keys (k2 name,
    k13 editable ...). Splitting them keeps serialisation explicit.
    """

    name: str = "CLINE CIRCLES"
    description: str = ""
    creator: str = "Cline"
    song_id: int = 0
    objects: list[LevelObject] = field(default_factory=list)
    colors: dict[int, Color] = field(default_factory=default_colors)

    # inner level-string header (see docs/VERIFICATION.md section 1a)
    speed: gd.Speed = gd.Speed.NORMAL
    game_mode: gd.GameMode = gd.GameMode.CUBE
    mini: bool = False
    dual: bool = False
    background_id: int = 1
    ground_id: int = 1
    middle_id: int = 0
    two_player: bool = False
    start_speed_locked: bool = True

    # .gmd plist keys
    gmd_header: dict[str, object] = field(default_factory=dict)

    # bookkeeping
    groups_used: set[int] = field(default_factory=set)

    # ------------------------------------------------------------------
    def add(self, *objs: LevelObject) -> LevelObject:
        self.objects.extend(objs)
        return objs[-1]

    def extend(self, objs: Iterable[LevelObject]) -> None:
        for o in objs:
            self.objects.append(o)

    def __len__(self) -> int:
        return len(self.objects)

    def __iter__(self) -> Iterator[LevelObject]:
        return iter(self.objects)

    def next_group_id(self, start: int = 1) -> int:
        """A free group id, skipping reserved low ids used by GD."""
        g = start
        while g in self.groups_used or g <= 0:
            g += 1
        self.groups_used.add(g)
        return g

    def claim_group(self, g: int) -> int:
        self.groups_used.add(int(g))
        return int(g)

    def set_color(self, channel: int, r: int, g: int, b: int, *,
                  blending: bool = False, opacity: float = 1.0,
                  player: int = -1) -> Color:
        c = Color(channel=channel, r=r, g=g, b=b, blending=blending,
                  opacity=opacity, player=player)
        self.colors[channel] = c
        return c

    def bounds(self) -> tuple[float, float, float, float]:
        if not self.objects:
            return (0.0, 0.0, 0.0, 0.0)
        xs = [o.x for o in self.objects]
        ys = [o.y for o in self.objects]
        return (min(xs), min(ys), max(xs), max(ys))

    def object_ids(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        for o in self.objects:
            counts[o.id] = counts.get(o.id, 0) + 1
        return counts
