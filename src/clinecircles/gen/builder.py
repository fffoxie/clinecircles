"""Geometry construction primitives for the level generator.

Coordinate conventions (all GD units, 1 block = 30 units):

* the engine supplies the ground. A row of blocks **at** ground level is a wall
  the player collides with, not a floor - found the hard way in the original
  project's playtest (``tools/wd_probe8.py``), and the reason RobTop's own
  Stereo Madness has no solid object before x=1515.
* so **hazards** (spikes, saws) sit on the ground with centre ``y = 15``, and
  all **solid geometry floats above the run line with its bottom at y >= 60**
  (2 blocks), leaving the player's 30-unit body clear.
* flying modes use a corridor: a solid row at ``floor_y`` (centre 75, bottom 60)
  and a ceiling above the flyable gap.
* objects snap to the 15-unit half grid, which is what GD itself uses (Stereo
  Madness places a spike at ``2,135,3,135``).

The builder also *records* the geometry it creates (solids, hazards, portals,
orbs, pads) so the renderer, the physics simulator and the linter work on the
same data the level string came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import ids
from ..gamedata import GameMode, Obj, Prop, Speed
from ..level import Level
from ..model import LevelObject

BLOCK = 30.0
GROUND = 15.0          # centre of a ground-level object (spike, portal)
FLOAT_FLOOR = 75.0     # centre of the first floating row (bottom 60)
HALF = 15.0


def snap(v: float) -> float:
    """Snap a coordinate to the 15-unit half grid."""
    return round(v / HALF) * HALF


def by(s: Speed) -> float:
    """Horizontal units travelled per second at ``s``."""
    return ids.SPEED_UNITS_PER_SECOND[int(s)]


@dataclass
class Box:
    """An axis-aligned box in level units."""

    x0: float
    x1: float
    y0: float
    y1: float
    kind: str = "solid"

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2


@dataclass
class Portal:
    x: float
    y: float
    kind: str      # mode | speed | gravity | size | dual | mirror | orb | pad
    value: object


@dataclass
class Builder:
    """Places objects into a :class:`Level` while recording its geometry."""

    level: Level
    solids: list[Box] = field(default_factory=list)
    hazards: list[Box] = field(default_factory=list)
    portals: list[Portal] = field(default_factory=list)
    orbs: list[Portal] = field(default_factory=list)
    pads: list[Portal] = field(default_factory=list)
    markers: dict[str, float] = field(default_factory=dict)
    _cells: set = field(default_factory=set)
    _groups: dict[str, int] = field(default_factory=dict)

    # ---------------------------------------------------------------- groups
    def group(self, name: str) -> int:
        """A stable, named group id (cached, so modules can share them)."""
        g = self._groups.get(name)
        if g is None:
            g = self.level.next_group_id(2)
            self._groups[name] = g
        return g

    def fresh_group(self) -> int:
        return self.level.next_group_id(2)

    def group_ids(self) -> dict[str, int]:
        return dict(self._groups)

    # ------------------------------------------------------------- low level
    def raw(self, obj: int, x: float, y: float) -> LevelObject:
        return self.level.add(LevelObject(int(obj), snap(x), snap(y)))

    def _seen(self, obj: int, x: float, y: float, rot: float) -> bool:
        cell = (int(obj), round(x, 1), round(y, 1), round(rot, 1))
        if cell in self._cells:
            return True
        self._cells.add(cell)
        return False

    def _finish(self, o: LevelObject, *, color, color2, groups, z, rot,
                scale, opacity, flip_x, flip_y) -> LevelObject:
        if color is not None:
            o.color(int(color), None if color2 is None else int(color2))
        for g in groups or ():
            o.add_group(int(g))
        if z is not None:
            o.set(Prop.Z_LAYER, int(z)).set(Prop.Z_ORDER, 0)
        if rot:
            o.set(Prop.ROTATION, float(rot))
        if scale is not None:
            if isinstance(scale, (tuple, list)):
                o.set(Prop.SCALE_X, float(scale[0]))
                o.set(Prop.SCALE_Y, float(scale[1]))
            else:
                o.set(Prop.SCALE_X, float(scale))
                o.set(Prop.SCALE_Y, float(scale))
        if opacity is not None:
            o.set(Prop.OPACITY, float(opacity))
        if flip_x:
            o.set(Prop.FLIP_X, 1)
        if flip_y:
            o.set(Prop.FLIP_Y, 1)
        return o


    # ------------------------------------------------------------------ solid
    def block(self, x: float, y: float, *, w: float = BLOCK, h: float = BLOCK,
              obj: int = Obj.BLOCK_SQUARE, color: int | None = None,
              color2: int | None = None, groups: tuple[int, ...] = (),
              z: int | None = None, rot: float = 0.0, scale=None,
              opacity: float | None = None, flip_x: bool = False,
              flip_y: bool = False, record: bool = True) -> LevelObject | None:
        x, y = snap(x), snap(y)
        if record:
            self.solids.append(Box(x - w / 2, x + w / 2, y - h / 2, y + h / 2))
        if self._seen(obj, x, y, rot):
            return None
        o = self.raw(obj, x, y)
        return self._finish(o, color=color, color2=color2, groups=groups, z=z,
                            rot=rot, scale=scale, opacity=opacity,
                            flip_x=flip_x, flip_y=flip_y)

    def block_row(self, x0: float, x1: float, y: float, *, step: float = BLOCK,
                  **kw) -> int:
        """A solid row of blocks with centres from ``x0`` to ``x1``."""
        n = 0
        x = snap(x0)
        while x <= snap(x1) + 1e-6:
            if self.block(x, y, **kw) is not None:
                n += 1
            x += step
        return n

    def block_col(self, x: float, y0: float, y1: float, **kw) -> int:
        n = 0
        y = snap(y0)
        while y <= snap(y1) + 1e-6:
            if self.block(x, y, **kw) is not None:
                n += 1
            y += BLOCK
        return n

    def band(self, x: float, y0: float, y1: float, *, color: int | None = None,
             groups: tuple[int, ...] = (), z: int | None = None,
             step: float = BLOCK) -> int:
        """A vertical band of blocks between the centres ``y0`` and ``y1``."""
        n = 0
        y = snap(y0)
        while y <= snap(y1) + 1e-6:
            if self.block(x, y, color=color, groups=groups, z=z) is not None:
                n += 1
            y += step
        return n

    def corridor(self, x0: float, x1: float, *, gap: float,
                 centre: float = FLOAT_FLOOR + 90.0, color: int | None = None,
                 ceiling: bool = True, ceiling_color: int | None = None,
                 groups: tuple[int, ...] = (), z: int | None = None,
                 floor: bool = True) -> tuple[float, float]:
        """Two solid rows leaving a ``gap``-unit tall flyable slot.

        Returns ``(slot_bottom, slot_top)``.
        """
        lo = snap(centre - gap / 2)
        hi = snap(centre + gap / 2)
        if floor:
            self.block_row(x0, x1, lo - BLOCK / 2, color=color, groups=groups,
                           z=z)
        if ceiling:
            self.block_row(x0, x1, hi + BLOCK / 2,
                           color=color if ceiling_color is None else ceiling_color,
                           groups=groups, z=z)
        return (lo, hi)

    # ---------------------------------------------------------------- hazard
    def hazard(self, x: float, y: float = GROUND, *,
               obj: int = Obj.SPIKE, w: float = BLOCK, h: float = BLOCK,
               color: int | None = None, groups: tuple[int, ...] = (),
               flip_y: bool = False, rot: float = 0.0, z: int | None = None,
               record: bool = True) -> LevelObject | None:
        x, y = snap(x), snap(y)
        if record:
            self.hazards.append(Box(x - w / 2, x + w / 2, y - h / 2, y + h / 2,
                                    "hazard"))
        if self._seen(obj, x, y, rot):
            return None
        o = self.raw(obj, x, y)
        return self._finish(o, color=color, color2=None, groups=groups, z=z,
                            rot=rot, scale=None, opacity=None, flip_x=False,
                            flip_y=flip_y)

    def spikes_row(self, x0: float, x1: float, *, y: float = GROUND,
                   count: int | None = None, **kw) -> int:
        """A ground row of spikes between ``x0`` and ``x1``."""
        x0, x1 = snap(x0), snap(x1)
        if count is None:
            count = max(1, int(round((x1 - x0) / BLOCK)) + 1)
        xs = ([(x0 + x1) / 2] if count == 1
              else [x0 + i * (x1 - x0) / (count - 1) for i in range(count)])
        n = 0
        for x in xs:
            if self.hazard(x, y, **kw) is not None:
                n += 1
        return n


    # ------------------------------------------------------ portals / orbs
    def portal(self, x: float, y: float, obj: int, kind: str, value,
               groups: tuple[int, ...] = ()) -> LevelObject:
        x, y = snap(x), snap(y)
        self.portals.append(Portal(x, y, kind, value))
        o = self.raw(obj, x, y)
        for g in groups:
            o.add_group(int(g))
        return o

    def mode_portal(self, x: float, mode: GameMode, *, y: float = FLOAT_FLOOR,
                    groups: tuple[int, ...] = ()) -> LevelObject:
        return self.portal(x, y, ids.MODE_PORTAL[int(mode)], "mode", mode,
                           groups)

    def speed_portal(self, x: float, speed: Speed, *,
                     y: float = FLOAT_FLOOR) -> LevelObject:
        return self.portal(x, y, ids.SPEED_PORTAL[int(speed)], "speed", speed)

    def gravity_portal(self, x: float, down: bool, *,
                       y: float = FLOAT_FLOOR) -> LevelObject:
        obj = Obj.PORTAL_GRAVITY_DOWN if down else Obj.PORTAL_GRAVITY_UP
        return self.portal(x, y, obj, "gravity", down)

    def size_portal(self, x: float, small: bool, *,
                    y: float = FLOAT_FLOOR) -> LevelObject:
        obj = Obj.PORTAL_SIZE_SMALL if small else Obj.PORTAL_SIZE_NORMAL
        return self.portal(x, y, obj, "size", small)

    def dual_portal(self, x: float, on: bool, *,
                    y: float = FLOAT_FLOOR) -> LevelObject:
        obj = Obj.PORTAL_DUAL_ON if on else Obj.PORTAL_DUAL_OFF
        return self.portal(x, y, obj, "dual", on)

    def mirror_portal(self, x: float, on: bool, *,
                      y: float = FLOAT_FLOOR) -> LevelObject:
        obj = Obj.PORTAL_MIRROR_IN if on else Obj.PORTAL_MIRROR_OUT
        return self.portal(x, y, obj, "mirror", on)

    ORB = {"yellow": Obj.ORB_YELLOW, "pink": Obj.ORB_PINK, "red": Obj.ORB_RED,
           "blue": Obj.ORB_BLUE, "green": Obj.ORB_GREEN,
           "black": Obj.ORB_BLACK, "toggle": Obj.ORB_TOGGLE,
           "dash_green": Obj.ORB_DASH_GREEN, "dash_pink": Obj.ORB_DASH_PINK}
    PAD = {"yellow": Obj.PAD_YELLOW, "pink": Obj.PAD_PINK,
           "red": Obj.PAD_RED, "blue": Obj.PAD_BLUE}

    def orb(self, x: float, y: float, kind: str = "yellow") -> LevelObject:
        x, y = snap(x), snap(y)
        self.orbs.append(Portal(x, y, "orb", kind))
        return self.raw(self.ORB[kind], x, y)

    def pad(self, x: float, y: float = GROUND,
            kind: str = "yellow") -> LevelObject:
        x, y = snap(x), snap(y)
        self.pads.append(Portal(x, y, "pad", kind))
        return self.raw(self.PAD[kind], x, y)

    def orb_chain(self, x: float, y: float, kinds: tuple[str, ...],
                  step: float) -> None:
        for i, k in enumerate(kinds):
            self.orb(x + i * step, y, k)

    # ------------------------------------------------------------------ deco
    def deco(self, obj: int, x: float, y: float, *, color: int | None = None,
             color2: int | None = None, scale=None, rot: float = 0.0,
             z: int = -3, groups: tuple[int, ...] = (),
             opacity: float | None = None, flip_y: bool = False,
             w: float | None = None, h: float | None = None,
             solid: bool = False) -> LevelObject:
        """A decoration object. Recorded as solid only when ``solid`` is set."""
        x, y = snap(x), snap(y)
        if solid:
            w = BLOCK if w is None else w
            h = BLOCK if h is None else h
            self.solids.append(Box(x - w / 2, x + w / 2, y - h / 2, y + h / 2))
        o = self.raw(obj, x, y)
        return self._finish(o, color=color, color2=color2, groups=groups, z=z,
                            rot=rot, scale=scale, opacity=opacity, flip_x=False,
                            flip_y=flip_y)

    # ---------------------------------------------------------------- misc
    def mark(self, name: str, x: float) -> None:
        self.markers[name] = x

    def bounds(self) -> tuple[float, float, float, float]:
        xs = [o.x for o in self.level.objects] or [0.0]
        ys = [o.y for o in self.level.objects] or [0.0]
        return (min(xs), min(ys), max(xs), max(ys))
