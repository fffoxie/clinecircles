"""Core data model: colour channels, objects and helper formatting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import gamedata as gd


# --------------------------------------------------------------------------
# Numbers
# --------------------------------------------------------------------------


def fnum(v: Any) -> str:
    """Format a value the way GD does: no trailing zeros, max 3 decimals."""
    if isinstance(v, bool):
        return "1" if v else "0"
    f = float(v)
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    return (f"{f:.3f}".rstrip("0").rstrip(".")) or "0"


# --------------------------------------------------------------------------
# Colour channels
# --------------------------------------------------------------------------


@dataclass
class Color:
    """A colour channel entry, stored in the ``kS38`` string.

    Sub-key layout (verified by decoding real levels):
        1=r 2=g 3=b 4=player(-1 none) 5=blending 6=channel 7=opacity
        8=toggle 11/12/13=hsv 15,18=flags
    """

    channel: int
    r: int = 255
    g: int = 255
    b: int = 255
    player: int = -1
    blending: bool = False
    opacity: float = 1.0
    hsv_enabled: bool = False
    hsv: str | None = None

    def to_string(self) -> str:
        parts = ["1", str(int(self.r)), "2", str(int(self.g)), "3", str(int(self.b)),
                 "11", "255", "12", "255", "13", "255", "4", str(int(self.player))]
        if self.blending:
            parts += ["5", "1"]
        parts += ["6", str(int(self.channel)), "7", fnum(self.opacity),
                  "15", "1", "18", "0", "8", "1"]
        if self.hsv_enabled and self.hsv:
            parts += ["41", "1", "43", self.hsv]
        return "_".join(parts)

    @staticmethod
    def from_string(s: str) -> "Color":
        kv = s.split("_")
        d = {int(kv[i]): kv[i + 1] for i in range(0, len(kv) - 1, 2)}
        c = Color(channel=int(float(d.get("6", 1))))
        c.r, c.g, c.b = (int(float(d.get("1", 255))), int(float(d.get("2", 255))),
                         int(float(d.get("3", 255))))
        c.player = int(float(d.get("4", -1)))
        c.blending = d.get("5", "0") == "1"
        c.opacity = float(d.get("7", 1))
        if d.get("41") == "1" and "43" in d:
            c.hsv_enabled, c.hsv = True, d["43"]
        return c


def default_colors() -> dict[int, Color]:
    """The built-in channels GD always writes, so the level renders sanely."""
    C = gd.ColorChannel
    return {
        C.BG: Color(C.BG, 20, 24, 40),
        C.G1: Color(C.G1, 12, 14, 26),
        C.LINE: Color(C.LINE, 255, 255, 255),
        C.LINE_3D: Color(C.LINE_3D, 255, 255, 255),
        C.OBJ: Color(C.OBJ, 255, 255, 255),
        C.P1: Color(C.P1, player=1),
        C.P2: Color(C.P2, player=2),
        C.LBG: Color(C.LBG, 44, 52, 78),
        C.G2: Color(C.G2, 30, 36, 58),
        C.BLACK: Color(C.BLACK, 0, 0, 0),
        C.WHITE: Color(C.WHITE, 255, 255, 255),
        C.LIGHTER: Color(C.LIGHTER, 255, 255, 255),
        C.MG: Color(C.MG, 30, 34, 52),
        C.MG2: Color(C.MG2, 24, 28, 44),
    }



# --------------------------------------------------------------------------
# Objects
# --------------------------------------------------------------------------


@dataclass
class LevelObject:
    """One object in the level: an id, a position and extra properties."""

    id: int
    x: float = 0.0
    y: float = 0.0
    props: dict[int, Any] = field(default_factory=dict)

    # -- construction helpers -------------------------------------------
    def set(self, prop: int | gd.Prop, value: Any) -> "LevelObject":
        self.props[int(prop)] = value
        return self

    def get(self, prop: int | gd.Prop, default: Any = None) -> Any:
        return self.props.get(int(prop), default)

    def groups(self) -> list[int]:
        raw = self.props.get(int(gd.Prop.GROUPS))
        if raw is None:
            return []
        if isinstance(raw, (list, tuple)):
            return [int(g) for g in raw]
        return [int(g) for g in str(raw).split(".") if g]

    def add_group(self, *g: int) -> "LevelObject":
        cur = self.groups()
        for x in g:
            if int(x) not in cur:
                cur.append(int(x))
        self.props[int(gd.Prop.GROUPS)] = ".".join(str(int(v)) for v in cur)
        return self

    def color(self, channel: int, detail: int | None = None) -> "LevelObject":
        self.props[int(gd.Prop.COLOR_1)] = int(channel)
        if detail is not None:
            self.props[int(gd.Prop.COLOR_2)] = int(detail)
        return self

    def z(self, layer: int, order: int = 0) -> "LevelObject":
        self.props[int(gd.Prop.Z_LAYER)] = int(layer)
        self.props[int(gd.Prop.Z_ORDER)] = int(order)
        return self

    def rot(self, degrees: float) -> "LevelObject":
        self.props[int(gd.Prop.ROTATION)] = float(degrees)
        return self

    def scale(self, xy: float, y: float | None = None) -> "LevelObject":
        self.props[int(gd.Prop.SCALE_X)] = float(xy)
        self.props[int(gd.Prop.SCALE_Y)] = float(xy if y is None else y)
        return self

    def editor_layer(self, l1: int, l2: int = 0) -> "LevelObject":
        self.props[int(gd.Prop.EDITOR_L1)] = int(l1)
        self.props[int(gd.Prop.EDITOR_L2)] = int(l2)
        return self

    def hide(self) -> "LevelObject":
        return self.set(gd.Prop.HIDE, 1)

    # -- serialisation ---------------------------------------------------
    def to_string(self) -> str:
        out = [str(int(gd.Prop.ID)), str(int(self.id)),
               str(int(gd.Prop.X)), fnum(self.x),
               str(int(gd.Prop.Y)), fnum(self.y)]
        for k in sorted(self.props):
            if k in (1, 2, 3):
                continue
            v = self.props[k]
            if v is None or v == "":
                continue
            out += [str(int(k)), fnum(v) if isinstance(v, (int, float, bool)) else str(v)]
        return ",".join(out)

    @staticmethod
    def from_string(s: str) -> "LevelObject":
        parts = s.split(",")
        d: dict[int, str] = {}
        for i in range(0, len(parts) - 1, 2):
            try:
                d[int(parts[i])] = parts[i + 1]
            except ValueError:
                continue
        obj = LevelObject(id=int(float(d.get(1, 1))), x=float(d.get(2, 0)),
                          y=float(d.get(3, 0)))
        for k, v in d.items():
            if k in (1, 2, 3):
                continue
            obj.props[k] = _coerce(v)
        return obj


def _coerce(v: str) -> Any:
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v
