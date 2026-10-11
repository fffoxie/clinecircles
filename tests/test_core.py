"""Round-trip + validity tests that need no third-party dependencies."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clinecircles as cc  # noqa: E402
from clinecircles.level import Level  # noqa: E402
from clinecircles.model import LevelObject  # noqa: E402
from clinecircles.serialization import (  # noqa: E402
    build_gmd, build_level_string, compress_level_string,
    decompress_level_string, parse_gmd, parse_level_string,
)


def test_compress_roundtrip():
    s = "kS38,1_255_2_255_3_255_6_1000;1,1,2,15,3,15;"
    assert decompress_level_string(compress_level_string(s)) == s


def test_level_string_roundtrip():
    lv = Level(name="t")
    lv.add(LevelObject(cc.Obj.BLOCK_SQUARE, 15, 15))
    lv.add(LevelObject(cc.Obj.SPIKE, 45, 15).add_group(7))
    lv.colors[1005] = cc.Color(1005, player=1)
    s = build_level_string(lv)
    back = parse_level_string(s)
    assert len(back.objects) == 2, back.objects
    assert back.objects[0].id == cc.Obj.BLOCK_SQUARE
    assert back.objects[1].groups() == [7]
    assert back.objects[1].y == 15


def test_gmd_roundtrip():
    lv = Level(name="CLINE CIRCLES", creator="Cline", song_id=123)
    lv.add(LevelObject(cc.Obj.BLOCK_SQUARE, 15, 15))
    doc = build_gmd(lv)
    assert doc.startswith("<?xml")
    assert "<k>kCEK</k><i>4</i>" in doc
    back = parse_gmd(doc)
    assert back.name == "CLINE CIRCLES"
    assert back.song_id == 123
    assert len(back.objects) == 1


def test_groups_separator():
    o = LevelObject(1, 0, 0).add_group(2).add_group(3)
    assert o.get(cc.Prop.GROUPS) == "2.3"
    assert o.groups() == [2, 3]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok", fn.__name__)
    print(f"\n{len(fns)} tests passed")
