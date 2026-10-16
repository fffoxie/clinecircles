"""Verified Geometry Dash identifiers, with explicit provenance.

Nothing here is invented. Every object id and property key the generator uses
has an entry in the tables below, and :func:`unverified_objects` /
:func:`unverified_props` return the ones that do not. ``tests/test_ids.py``
fails when those lists are non-empty, so an unverified id cannot silently reach
a level file.

Provenance tags
---------------
``table``   present in ``data/object_table.csv`` / ``data/prop_table.csv``.
            Those tables come from the game's own object and property data and
            are vendored from UHDanke/gmdkit (MIT; see
            data/GMDKIT_LICENSE_MIT.txt).
``level``   observed while decoding a real level in ``rflevels/``.
``engine``  confirmed by running the object in a game engine and reading its
            state back (Web Dashers, tools/wd_object_test.py).
``docs``    documented in gd.docs / the GD wiki.

Portals: the *header* game-mode value (``kA2``) and the *portal object* id are
different things - :data:`MODE_PORTAL` maps one to the other.
"""

from __future__ import annotations

from .gamedata import (  # noqa: F401  (re-exported for convenience)
    BLOCK_UNITS, Easing, GameMode, Obj, Prop, Speed,
)

TABLE = "table"
LEVEL = "level"
ENGINE = "engine"
DOCS = "docs"


def _parse(text: str) -> dict[int, tuple[str, str]]:
    """``id tag evidence`` per line -> ``{id: (tag, evidence)}``."""
    out: dict[int, tuple[str, str]] = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        oid, tag, evidence = line.split(None, 2)
        out[int(oid)] = (tag, evidence.strip())
    return out


_OBJECTS = """
# portals
12    table CubePortalObject; rflevels/Nine Circles.gmd
13    table ShipPortalObject; rflevels/Nine Circles.gmd
47    table BallPortalObject; rflevels/Nine Circles.gmd
111   table BirdPortalObject (UFO); rflevels/Layout.gmd
660   table DartPortalObject (wave); rflevels/Nine Circles.gmd
745   table RobotPortalObject; rflevels/Artemis 13.gmd
1331  table SpiderPortalObject
1933  table SwingPortalObject
10    table GravityPortalDown; rflevels/Nine Circles.gmd
11    table GravityPortalUp; rflevels/Nine Circles.gmd
99    table NormalSizePortalObject
101   table MiniSizePortalObject
286   table DualPortalObject
287   table DualEndPortalObject
45    table MirrorPortalObject
46    table MirrorExitPortalObject
747   table TeleportPortalObject
# speed portals
200   table SlowSpeedObject (0.5x)
201   table NormalSpeedObject (1x)
202   table FastSpeedObject (2x)
203   table FasterSpeedObject (3x)
1334  table FastestSpeedObject (4x)
# pads
35    engine YellowJumpPad; tools/wd_object_test.py
140   table PinkJumpPad
1332  table RedJumpPad
67    table BlueJumpPad (gravity flip)
# orbs
36    engine YellowJumpRing; tools/wd_object_test.py
141   table PinkJumpRing
1333  table RedJumpRing
84    table BlueJumpRing (gravity flip)
1022  table GreenJumpRing (gravity flip)
1330  table BlackJumpRing
1594  table ToggleJumpRing
1704  table GreenDashRing
1751  table PinkDashRing
# hazards
8     level SpikeObject; rflevels/Layout.gmd
39    table ShortSpikeObject
103   table SpikeObject2 (small)
144   table InvisibleSpikeObject
1705  table SawObjectLarge
1706  table SawObjectMedium
1707  table SawObjectSmall
135   table ThornObject (hazard)
123   table ThornObjectLarge
127   table ThornObjectSmall
15    table RodObject tall
16    table RodObject medium
17    table RodObject short
# structure / deco
1     level BlockObject; rflevels/Layout.gmd
2     table GridBlockObject
890   table BeveledBlockObject; rflevels/Realistic deco.gmd
1764  table CircleObjectSmall
51    table BasicRingObject
1838  table QuarterCircleObject
1000  table SplitObjectXS
1841  table ExpandObjectL
914   table TextGameObject (string in prop 31, base64)
50    table Pulsing Filled Circle (editor tab 12)
51    table Pulsing Circle (editor tab 12)
236   table Large Pulsing Hollow Circle (tab 12)
497   table Large Pulsing Circle (tab 12)
997   table Large Split Circle (tab 12)
998   table Medium Split Circle (tab 12)
999   table Small Split Circle (tab 12)
1000  table Very Small Split Circle (tab 12)
1841  table Large Expanding Circle Animation (tab 7)
1842  table Small Expanding Circle Animation (tab 7)
1837  table Large Quarter Circle (tab 11)
1838  table Small Quarter Circle (tab 11)
85    table Large Decorative Gear (tab 12)
86    table Medium Decorative Gear (tab 12)
87    table Small Decorative Gear (tab 12)
1702  table Spiked Circle Hazard (tab 12)
498   table Chain Link (tab 11)
1603  table Cartoon Arrow (tab 11)
1525  table Large Rotating Particle (tab 12)
1526  table Medium Rotating Particle (tab 12)
1527  table Small Rotating Particle (tab 12)
18    table Large Decorative Spikes (editor tab 11)
19    table Medium Decorative Spikes (editor tab 11)
20    table Small Decorative Spikes (editor tab 11)
21    table Very Small Decorative Spikes (editor tab 11)
"""


_TRIGGERS = """
899   table ColorTriggerGameObject
901   table MoveTriggerGameObject
1006  table PulseTriggerGameObject
1007  table AlphaTriggerGameObject
1049  table ToggleTriggerGameObject
1268  table SpawnTriggerGameObject
1346  table RotateTriggerGameObject
1347  table FollowTriggerGameObject
1520  table ShakeTriggerGameObject
1585  table AnimateTriggerGameObject
1595  table TouchTriggerGameObject
1616  table StopTriggerGameObject
1611  table CountTriggerGameObject
1812  table OnDeathTriggerGameObject
1814  table FollowPlayerYTriggerObject
1815  table CollisionTriggerGameObject
1816  table CollisionBlockObject
1817  table PickupTriggerGameObject
1818  table BGEffectOnTriggerObject
1819  table BGEffectOffTriggerObject
1912  table RandomTriggerGameObject
1913  table CameraZoomTriggerObject
1914  table StaticCameraTriggerObject
1915  table EnterTriggerGameObject
1916  table CameraOffsetTriggerObject
31    level StartPosObject; rflevels/Nine Circles.gmd
32    table PlayerTrailObject
33    table PlayerTrailOffObject
3033  table KeyframeObject
# 2.2 shaders
2904  table ShaderOptionsTrigger
2905  table ShockWaveShader
2907  table ShockLineShader
2909  table GlitchShader
2910  table ChromaticAberrationShader
2911  table ChromaticGlitchShader
2912  table PixelateShader
2913  table LensCircleShader
2914  table RadialBlurShader
2915  table MotionBlurShader
2916  table BulgeShader
2917  table PinchShader
2919  table GrayscaleShader
2920  table SepiaShader
2921  table InvertColorShader
2922  table HueShiftShader
2923  table ShaderColorTrigger
2924  table SplitScreenShader
"""

_OBJ_PROPS = """
2     table object.X
3     table object.Y
4     table object.FLIP_X
5     table object.FLIP_Y
6     table object.ROTATION
7     table object.RED
8     table object.GREEN
9     table object.BLUE
10    table object.DURATION (seconds)
11    table object.TOUCH_TRIGGER
20    table object.EDITOR_LAYER_1
21    table object.COLOR_1 (main colour channel)
22    table object.COLOR_2 (detail colour channel)
23    table object.CHANNEL (target colour channel)
24    table object.Z_LAYER
25    table object.Z_ORDER
28    table object.MOVE_X
29    table object.MOVE_Y
30    table object.EASING
31    table object.TEXT (base64)
34    table object.GROUP_PARENT
35    table object.OPACITY
41    table object.HSV_ENABLED_1
43    table object.HSV_1
45    table object.FADE_IN (pulse)
46    table object.HOLD (pulse)
47    table object.FADE_OUT (pulse)
51    table object.TARGET_ID (target group)
52    table object.TARGET_TYPE
56    table object.ACTIVATE_GROUP
57    table object.GROUPS (dot separated)
61    table object.EDITOR_LAYER_2
63    table object.SPAWN_DELAY
64    table object.DONT_FADE
67    table object.DONT_ENTER
68    table object.DEGREES (rotate trigger)
70    table object.LOCK_ROTATION
71    table object.CENTER_ID (rotate / follow centre)
72    table object.MOD_X (follow)
73    table object.MOD_Y (follow)
75    table object.SHAKE_STRENGTH
76    table object.ANIMATION_ID
77    table object.COUNT (count trigger)
80    table object.ITEM_ID (count trigger)
84    table object.SHAKE_INTERVAL
85    table object.EASE_RATE
86    table object.EXCLUSIVE (pulse)
97    table object.ROTATION_SPEED
128   table object.SCALE_X
129   table object.SCALE_Y
135   table object.HIDE
371   table trigger.zoom_camera.ZOOM
498   table object.BPM
580   table trigger.stop.STOP_MODE
1     table object.ID
13    table trigger.EDITOR_PREVIEW
14    table trigger.color.TINT_GROUND
15    table trigger.color.PLAYER_1
16    table trigger.color.PLAYER_2
17    table trigger.color.BLENDING
19    table object.OLD_COLOR_ID
32    table object.OLD_SCALE
42    table object.HSV_ENABLED_2
44    table object.HSV_2
48    table trigger.pulse.COLOR_TYPE
49    table trigger.pulse.HSV
50    table trigger.pulse.COPY_ID
69    table trigger.rotate.FULL
96    table object.NO_GLOW
103   table object.HIGH_DETAIL
108   table object.LINKED_GROUP
116   table object.NO_EFFECTS
121   table object.NO_TOUCH
131   table object.SKEW_X
132   table object.SKEW_Y
134   table object.PASSABLE
137   table object.ICE_BLOCK
200   table trigger.move.PLAYER_2 (also rotate / collision / song)
506   table trigger.camera_guide.PREVIEW_OPACITY
81    table trigger.touch.HOLD_MODE
82    table trigger.touch.TOGGLE_MODE
89    table trigger.touch.DUAL_MODE
102   table trigger.spawn.DISABLE_PREVIEW
104   table trigger.count.MULTI_ACTIVATE
441   table trigger.spawn.ORDERED
442   table trigger.spawn.REMAPS (group remaps, string)
175   table trigger.shader.GLITCH_SPEED / SHOCKWAVE_SPEED / CHROMATIC_GLITCH_SPEED
176   table trigger.shader.*_STRENGTH (GLITCH/BULGE/HUE/INVERT/LENS_CIRCLE/...)
179   table trigger.shader.*_SIZE / GLITCH_SLICE_HEIGHT / PINCH_MODIFIER
180   table trigger.shader.*_RADIUS / *_TARGET_X / CHROMATIC_GLITCH_RGB_OFFSET
512   table trigger.shader.SHOCKWAVE_MAX_SIZE / PINCH_RADIUS
514   table trigger.shader.*_RELATIVE
515   table trigger.shader.PIXELATE_HARD_EDGES
531   table trigger.shader.OPTIONS_DISABLE_PREVIEW
"""

OBJECT_SOURCE: dict[int, tuple[str, str]] = _parse(_OBJECTS + _TRIGGERS)
PROP_SOURCE: dict[int, tuple[str, str]] = _parse(_OBJ_PROPS)


_HEADERS = """
kS38  table level.COLORS
kA2   table level.GAME_MODE
kA3   table level.MINI_MODE
kA4   table level.START_SPEED
kA6   table level.BACKGROUND
kA7   table level.GROUND
kA8   table level.DUAL_MODE
kA9   table level.IS_START_POS
kA10  table level.INPUT_2P
kA11  table level.FLIP_GRAVITY
kA13  table level.SONG_OFFSET (float seconds) -- the song start offset
kA14  table level.SONG_GUIDELINES
kA15  table level.SONG_FADE_IN
kA16  table level.SONG_FADE_OUT
kA17  table level.GROUND_LINE
kA18  table level.FONT
kA20  table level.REVERSE_MODE
kA22  table level.PLATFORMER_MODE
kA25  table level.MIDDLE_GROUND
"""

_GMD_KEYS = """
kCEK  level encoder key (4 in every exported level we decoded)
k2    table level.NAME
k3    table level.DESCRIPTION (base64)
k4    table level.LEVEL_STRING (gzip + base64url)
k5    table level.CREATOR
k8    table level.OFFICIAL_SONG_ID
k13   table level.EDITABLE
k16   table level.VERSION
k21   table level.TYPE (2 = local)
k23   table level.LENGTH
k25   table level.DEMON
k45   table level.SONG_ID
k47   table level.MODIFIED
k48   table level.OBJECT_COUNT
k50   table level.BINARY_VERSION
k104  table level.SONGS
"""

HEADER_SOURCE: dict[str, tuple[str, str]] = {
    k: (tag, ev) for k, tag, ev in
    (ln.split(None, 2) for ln in _HEADERS.strip().splitlines())
}
GMD_SOURCE: dict[str, tuple[str, str]] = {
    k: (tag, ev) for k, tag, ev in
    (ln.split(None, 2) for ln in _GMD_KEYS.strip().splitlines())
}

#: header game-mode value -> portal object id
MODE_PORTAL: dict[int, int] = {
    int(GameMode.CUBE): 12, int(GameMode.SHIP): 13, int(GameMode.BALL): 47,
    int(GameMode.UFO): 111, int(GameMode.WAVE): 660, int(GameMode.ROBOT): 745,
    int(GameMode.SPIDER): 1331, int(GameMode.SWING): 1933,
}

#: header speed value -> speed portal object id
SPEED_PORTAL: dict[int, int] = {
    int(Speed.SLOW): 200, int(Speed.NORMAL): 201, int(Speed.FAST): 202,
    int(Speed.VERY_FAST): 203, int(Speed.SUPER_FAST): 1334,
}

#: units travelled per second at each speed (gd.docs; cross-checked in physics.py)
SPEED_UNITS_PER_SECOND: dict[int, float] = {
    int(Speed.SLOW): 251.16, int(Speed.NORMAL): 311.58, int(Speed.FAST): 387.42,
    int(Speed.VERY_FAST): 468.00, int(Speed.SUPER_FAST): 576.00,
}

#: editor Z layers (gd.docs "Z Layer"); B5 is furthest back, T5 in front
Z_LAYERS: dict[str, int] = {
    "B5": -5, "B4": -4, "B3": -3, "B2": -2, "B1": -1,
    "T1": 1, "T2": 2, "T3": 3, "T4": 4, "T5": 5,
}

CUSTOM_CHANNEL_RANGE = (1, 999)
BUILTIN_CHANNEL_BASE = 1000
MAX_GROUP_ID = 9999
MAX_OBJECTS = 65535


def unverified_objects() -> list[int]:
    """Object ids exposed by :class:`Obj` that have no provenance entry."""
    return sorted(int(m) for m in Obj if int(m) not in OBJECT_SOURCE)


def unverified_props() -> list[int]:
    """Property keys exposed by :class:`Prop` that have no provenance entry."""
    return sorted(int(m) for m in Prop if int(m) not in PROP_SOURCE)


def report() -> str:
    """A human-readable summary, used by ``docs/ids_verified.md``."""
    lines = [f"objects: {len(OBJECT_SOURCE)} verified, "
             f"{len(unverified_objects())} unverified",
             f"properties: {len(PROP_SOURCE)} verified, "
             f"{len(unverified_props())} unverified"]
    bad = unverified_objects()
    if bad:
        lines.append("UNVERIFIED OBJECT IDS: " + ", ".join(map(str, bad)))
    bad = unverified_props()
    if bad:
        lines.append("UNVERIFIED PROPERTY KEYS: " + ", ".join(map(str, bad)))
    return "\n".join(lines)
