"""Gameplay construction primitives.

Everything is expressed in GD units (1 block = 30 units, ground surface at
y = 0). A 30x30 object resting on the ground has its centre at y = 15, which
matches real levels (verified against Stereo Madness: a spike at ``3,15``).

The :class:`Builder` also records solid and hazard geometry so the playability
validator can check the layout later.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import gamedata as gd
from ..level import Level
from ..model import LevelObject

BLOCK = 30.0


def b(n: float) -> float:
    """Blocks -> units."""
    return n * BLOCK


def snap_ground(y_blocks: float = 0.0) -> float:
    """Centre y of an object whose *bottom* sits at ``y_blocks`` blocks."""
    return b(y_blocks) + BLOCK / 2


@dataclass
class Solid:
    """An axis-aligned solid box (units)."""

    x0: float
    x1: float
    y0: float
    y1: float


@dataclass
class Hazard:
    x0: float
    x1: float
    y0: float
    y1: float


@dataclass
class Builder:
    """Places objects into a level while tracking geometry."""

    level: Level
    solids: list[Solid] = field(default_factory=list)
    hazards: list[Hazard] = field(default_factory=list)
    markers: dict[str, float] = field(default_factory=dict)
    _cells: set = field(default_factory=set)

    def _seen(self, obj: int, x: float, y: float) -> bool:
        """True if an identical object already occupies this cell."""
        cell = (int(obj), round(x * 100), round(y * 100))
        if cell in self._cells:
            return True
        self._cells.add(cell)
        return False

    # ------------------------------------------------------------------
    def solid(self, x: float, y: float, w: float = BLOCK, h: float = BLOCK,
              color: int | None = None, obj: int = gd.Obj.BLOCK_SQUARE,
              groups: tuple[int, ...] = ()) -> LevelObject:
        """Place a solid block centred at (x, y)."""
        self.solids.append(Solid(x - w / 2, x + w / 2, y - h / 2, y + h / 2))
        if self._seen(obj, x, y):
            return LevelObject(int(obj), x, y)
        o = LevelObject(obj, x, y)
        if color is not None:
            o.color(color)
        if groups:
            o.add_group(*groups)
        self.level.add(o)
        return o

    def hazard(self, x: float, y: float, w: float = BLOCK, h: float = BLOCK,
               obj: int = gd.Obj.SPIKE, color: int | None = None,
               groups: tuple[int, ...] = ()) -> LevelObject:
        self.hazards.append(Hazard(x - w / 2, x + w / 2, y - h / 2, y + h / 2))
        if self._seen(obj, x, y):
            return LevelObject(int(obj), x, y)
        o = LevelObject(obj, x, y)
        if color is not None:
            o.color(color)
        if groups:
            o.add_group(*groups)
        self.level.add(o)
        return o

    # ------------------------------------------------------------------
    def floor(self, x0: float, x1: float, y_blocks: float = 0.0,
              color: int | None = None, obj: int = gd.Obj.BLOCK_SQUARE,
              step: float = BLOCK) -> int:
        """A solid row of blocks from x0 to x1 at the given height."""
        n = 0
        x = x0
        while x <= x1 + 1e-6:
            self.solid(x, snap_ground(y_blocks), BLOCK, BLOCK, color, obj)
            x += step
            n += 1
        return n

    def ceiling(self, x0: float, x1: float, y_blocks: float,
                color: int | None = None, obj: int = gd.Obj.BLOCK_SQUARE,
                step: float = BLOCK) -> int:
        """A solid row of blocks whose *bottom* is at ``y_blocks`` blocks."""
        n = 0
        x = x0
        yc = b(y_blocks) + BLOCK / 2
        while x <= x1 + 1e-6:
            self.solid(x, yc, BLOCK, BLOCK, color, obj)
            x += step
            n += 1
        return n

    def wall(self, x: float, y0_blocks: float, y1_blocks: float,
             color: int | None = None, obj: int = gd.Obj.BLOCK_SQUARE) -> int:
        """A vertical column of blocks (centres from y0 to y1 blocks)."""
        n = 0
        y = y0_blocks
        while y <= y1_blocks + 1e-6:
            self.solid(x, snap_ground(y), BLOCK, BLOCK, color, obj)
            y += 1
            n += 1
        return n

    def spikes(self, x0: float, x1: float, y_blocks: float = 0.0,
               color: int | None = None, obj: int = gd.Obj.SPIKE,
               count: int | None = None) -> int:
        """A row of spikes on the ground between x0 and x1."""
        span = x1 - x0
        n = count if count is not None else max(1, int(round(span / BLOCK)) + 1)
        xs = [x0] if n == 1 else [x0 + i * span / (n - 1) for i in range(n)]
        for x in xs:
            self.hazard(x, snap_ground(y_blocks), BLOCK, BLOCK, obj, color)
        return len(xs)

    def spike_ceiling(self, x0: float, x1: float, y_blocks: float,
                      color: int | None = None) -> int:
        n = max(1, int(round((x1 - x0) / BLOCK)) + 1)
        step = (x1 - x0) / (n - 1) if n > 1 else 0
        for i in range(n):
            x = x0 + i * step
            o = LevelObject(gd.Obj.SPIKE, x, b(y_blocks) + BLOCK / 2)
            if color is not None:
                o.color(color)
            o.set(gd.Prop.FLIP_Y, 1)
            self.level.add(o)
            self.hazards.append(Hazard(x - BLOCK / 2, x + BLOCK / 2,
                                       b(y_blocks), b(y_blocks) + BLOCK))
        return n

    # ------------------------------------------------------------------
    def portal(self, x: float, y_blocks: float, obj: gd.Obj,
               groups: tuple[int, ...] = ()) -> LevelObject:
        o = LevelObject(obj, x, b(y_blocks) + BLOCK / 2)
        if groups:
            o.add_group(*groups)
        return self.level.add(o)

    def speed(self, x: float, y_blocks: float, speed: gd.Speed) -> LevelObject:
        return self.portal(x, y_blocks, gd.SPEED_PORTAL_OBJECT[speed])

    def mode(self, x: float, y_blocks: float, mode: gd.GameMode) -> LevelObject:
        return self.portal(x, y_blocks, gd.MODE_PORTAL_OBJECT[mode])

    def pad(self, x: float, y_blocks: float, kind: str = "yellow") -> LevelObject:
        obj = {"yellow": gd.Obj.PAD_YELLOW, "pink": gd.Obj.PAD_PINK,
               "red": gd.Obj.PAD_RED, "blue": gd.Obj.PAD_BLUE}[kind]
        return self.portal(x, y_blocks, obj)

    def orb(self, x: float, y_blocks: float, kind: str = "yellow") -> LevelObject:
        obj = {"yellow": gd.Obj.ORB_YELLOW, "pink": gd.Obj.ORB_PINK,
               "red": gd.Obj.ORB_RED, "blue": gd.Obj.ORB_BLUE,
               "green": gd.Obj.ORB_GREEN, "black": gd.Obj.ORB_BLACK,
               "toggle": gd.Obj.ORB_TOGGLE, "dash_green": gd.Obj.ORB_DASH_GREEN,
               "dash_pink": gd.Obj.ORB_DASH_PINK}[kind]
        return self.portal(x, y_blocks, obj)

    def mark(self, name: str, x: float) -> None:
        self.markers[name] = x
