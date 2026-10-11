"""Serialisation between :class:`Level` and real Geometry Dash data.

Two representations, both verified against actual GD files
(see docs/VERIFICATION.md):

* the **level string** - plaintext, ``<header kv pairs>;<object>;<object>;...``
* the **``.gmd`` container** - an XML plist whose ``k4`` value is the level
  string gzip-compressed and base64-URL-safe encoded.
"""

from __future__ import annotations

import base64
import gzip
import html
import re
import zlib

from . import gamedata as gd
from .level import Level
from .model import Color, LevelObject

GMD_BINARY_VERSION = 45

# Header keys we always emit, in the order real 2.2 levels use.
_FLAG_DEFAULTS: tuple[tuple[str, str], ...] = (
    ("kA13", "0"), ("kA15", "0"), ("kA16", "0"), ("kA14", ""),
    ("kA6", "1"), ("kA7", "1"), ("kA25", "0"), ("kA17", "0"), ("kA18", "0"),
    ("kS39", "0"), ("kA2", "0"), ("kA3", "0"), ("kA8", "0"), ("kA4", "1"),
    ("kA9", "0"), ("kA10", "0"), ("kA11", "0"), ("kA22", "0"), ("kA23", "0"),
    ("kA24", "0"), ("kA27", "1"), ("kA40", "1"), ("kA41", "1"), ("kA42", "1"),
    ("kA28", "0"), ("kA29", "0"), ("kA31", "1"), ("kA32", "1"), ("kA36", "0"),
    ("kA43", "0"), ("kA44", "0"), ("kA45", "1"), ("kA46", "0"), ("kA33", "1"),
    ("kA34", "1"), ("kA35", "0"), ("kA37", "1"), ("kA38", "1"), ("kA39", "1"),
    ("kA19", "0"), ("kA26", "0"), ("kA20", "0"), ("kA21", "0"),
)


def build_level_string(level: Level) -> str:
    """Encode a :class:`Level` as a plaintext GD level string."""
    header: list[tuple[str, str]] = [
        ("kS38", "|".join(c.to_string() for _, c in sorted(level.colors.items())))
    ]
    overrides = {
        "kA6": str(level.background_id),
        "kA7": str(level.ground_id),
        "kA25": str(level.middle_id),
        "kA2": str(int(level.game_mode)),
        "kA3": "1" if level.mini else "0",
        "kA8": "1" if level.dual else "0",
        "kA4": str(int(level.speed)),
        "kA10": "1" if level.two_player else "0",
    }
    seen = {"kS38"}
    for key, val in _FLAG_DEFAULTS:
        header.append((key, overrides.get(key, val)))
        seen.add(key)
    for key, val in (level.gmd_header.get("_level_string") or {}).items():
        if key not in seen:
            header.append((key, str(val)))

    body = ";".join(o.to_string() for o in level.objects)
    return ",".join(f"{k},{v}" for k, v in header) + ";" + body + (";" if body else "")


def parse_level_string(s: str) -> Level:
    """Decode a plaintext level string back into a :class:`Level`."""
    head, _, body = s.partition(";")
    level = Level()
    level.colors = {}
    tokens = head.split(",")
    for i in range(0, len(tokens) - 1, 2):
        k, v = tokens[i], tokens[i + 1]
        if k == "kS38":
            for chunk in v.split("|"):
                if chunk:
                    c = Color.from_string(chunk)
                    level.colors[c.channel] = c
        elif k == "kA4":
            level.speed = gd.Speed(int(v))
        elif k == "kA2":
            level.game_mode = gd.GameMode(int(v or 0))
        elif k == "kA3":
            level.mini = v == "1"
        elif k == "kA8":
            level.dual = v == "1"
        elif k == "kA6":
            level.background_id = int(v or 1)
        elif k == "kA7":
            level.ground_id = int(v or 1)
        elif k in ("kA13", "kA14", "kA15", "kA16", "kA17", "kA18", "kS39"):
            continue
        else:
            level.gmd_header.setdefault("_level_string", {})[k] = v
    for chunk in body.split(";"):
        if chunk.strip():
            level.objects.append(LevelObject.from_string(chunk))
    return level


def compress_level_string(s: str) -> str:
    return base64.urlsafe_b64encode(gzip.compress(s.encode())).decode()


def decompress_level_string(s: str) -> str:
    s = html.unescape(s)
    return zlib.decompress(base64.urlsafe_b64decode(s.encode()), 15 | 32).decode()


# --------------------------------------------------------------------------
# .gmd plist container
# --------------------------------------------------------------------------


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _b64_text(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def build_gmd(level: Level, *, object_count: int | None = None) -> str:
    """Serialise a :class:`Level` to a GDShare ``.gmd`` plist document."""
    ls = build_level_string(level)
    n = len(level.objects) if object_count is None else object_count

    fields: list[tuple[str, str]] = [("kCEK", "<i>4</i>"),
                                     ("k2", f"<s>{_xml_escape(level.name)}</s>")]
    if level.description:
        fields.append(("k3", f"<s>{_b64_text(level.description)}</s>"))
    fields.append(("k4", f"<s>{compress_level_string(ls)}</s>"))
    if level.creator:
        fields.append(("k5", f"<s>{_xml_escape(level.creator)}</s>"))
    fields += [
        ("k13", "<t />"),
        ("k21", "<i>2</i>"),
        ("k16", "<i>1</i>"),
        ("k23", "<i>4</i>"),   # level length bucket
        ("k25", "<t />"),      # is demon
        ("k45", f"<i>{int(level.song_id)}</i>"),
        ("k48", f"<i>{n}</i>"),  # object count
        ("k50", f"<i>{GMD_BINARY_VERSION}</i>"),
        ("k47", "<t />"),      # modified
    ]
    body = "".join(f"<k>{k}</k>{v}" for k, v in fields)
    return ("<?xml version='1.0' encoding='us-ascii'?>\n"
            f'<plist version="1.0" gjver="2.0"><dict>{body}</dict></plist>')


_GMD_FIELD_RE = re.compile(
    r"<k>(?P<k>[^<]*)</k>(?P<v><t />|<f />|<[sif][^>]*>[^<]*</[sif]>)", re.S)


def parse_gmd(text: str) -> Level:
    """Parse a ``.gmd`` plist document into a :class:`Level`."""
    level: Level = Level()
    for m in _GMD_FIELD_RE.finditer(text):
        k, v = m.group("k"), m.group("v")
        if k == "k4":
            inner = re.sub(r"^<s>|</s>$", "", v)
            parsed = parse_level_string(decompress_level_string(inner))
            parsed.name = level.name
            parsed.description = level.description
            parsed.creator = level.creator
            parsed.song_id = level.song_id
            level = parsed
        elif k == "k2":
            level.name = re.sub(r"^<s>|</s>$", "", v)
        elif k == "k3":
            raw = re.sub(r"^<s>|</s>$", "", v)
            try:
                level.description = base64.b64decode(raw).decode()
            except Exception:
                level.description = raw
        elif k == "k5":
            level.creator = re.sub(r"^<s>|</s>$", "", v)
        elif k == "k45":
            mm = re.search(r"<i>(-?\d+)</i>", v)
            if mm:
                level.song_id = int(mm.group(1))
    return level


def write_gmd(level: Level, path: str) -> str:
    doc = build_gmd(level)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return doc


def read_gmd(path: str) -> Level:
    with open(path, "r", encoding="utf-8") as fh:
        return parse_gmd(fh.read())

    return zlib.decompress(base64.urlsafe_b64decode(s.encode()), 15 | 32).decode()
