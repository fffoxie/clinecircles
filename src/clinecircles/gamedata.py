"""Verified Geometry Dash constants: object ids, property keys, colours.

Every value here comes from the vendored authoritative tables in ``data/``
(objects/ids from the game via gmdkit, properties from GD's own property table)
or from gd.docs. Nothing here is invented.

GD stores object properties as numeric keys in the level string; ``Prop`` maps
human names to those verified numeric keys.
"""

from __future__ import annotations

from enum import IntEnum


class Prop(IntEnum):
    """Numeric property keys used in the level-string object encoding."""

    ID = 1
    X = 2
    Y = 3
    FLIP_X = 4
    FLIP_Y = 5
    ROTATION = 6
    RED = 7
    GREEN = 8
    BLUE = 9
    DURATION = 10
    TOUCH_TRIGGER = 11
    EDITOR_PREVIEW = 13
    TINT_GROUND = 14
    PLAYER_1 = 15
    PLAYER_2 = 16
    BLENDING = 17
    OLD_COLOR_ID = 19
    EDITOR_L1 = 20
    COLOR_1 = 21
    COLOR_2 = 22
    CHANNEL = 23
    Z_LAYER = 24
    Z_ORDER = 25
    MOVE_X = 28
    MOVE_Y = 29
    EASING = 30
    TEXT_DATA = 31
    OLD_SCALE = 32
    GROUP_PARENT = 34
    OPACITY = 35
    HSV_ENABLED_1 = 41
    HSV_ENABLED_2 = 42
    HSV_1 = 43
    HSV_2 = 44
    FADE_IN = 45
    HOLD = 46
    FADE_OUT = 47
    COLOR_TYPE = 48
    HSV = 49
    COPY_ID = 50
    TARGET_ID = 51
    TARGET_TYPE = 52
    GROUPS = 57
    EDITOR_L2 = 61
    SPAWN_DELAY = 63
    DONT_FADE = 64
    DONT_ENTER = 67
    DEGREES = 68
    FULL_ROTATION = 69
    LOCK_ROTATION = 70
    CENTER_ID = 71
    MOD_X = 72
    MOD_Y = 73
    SHAKE_STRENGTH = 75
    ANIMATION_ID = 76
    COUNT = 77
    ITEM_ID = 80
    SHAKE_INTERVAL = 84
    EASE_RATE = 85
    EXCLUSIVE = 86
    NO_GLOW = 96
    ROTATION_SPEED = 97
    HIGH_DETAIL = 103
    LINKED_GROUP = 108
    NO_EFFECTS = 116
    NO_TOUCH = 121
    SCALE_X = 128
    SCALE_Y = 129
    SKEW_X = 131
    SKEW_Y = 132
    PASSABLE = 134
    HIDE = 135
    ICE_BLOCK = 137
    PLAYER_2_MOVE = 200
    ACTIVATE_GROUP = 56
    BLOCK_ID = 80
    STOP_MODE = 580
    BPM = 498
    ZOOM = 371
    PREVIEW_OPACITY = 506


class Obj(IntEnum):
    """Verified object ids (see data/object_table.csv)."""

    # game-mode portals
    PORTAL_CUBE = 12
    PORTAL_SHIP = 13
    PORTAL_BALL = 47
    PORTAL_UFO = 111
    PORTAL_WAVE = 660
    PORTAL_ROBOT = 745
    PORTAL_SPIDER = 1331
    PORTAL_SWING = 1933
    # gravity + manipulation
    PORTAL_GRAVITY_DOWN = 10
    PORTAL_GRAVITY_UP = 11
    PORTAL_MIRROR_IN = 45
    PORTAL_MIRROR_OUT = 46
    PORTAL_SIZE_NORMAL = 99
    PORTAL_SIZE_SMALL = 101
    PORTAL_DUAL_ON = 286
    PORTAL_DUAL_OFF = 287
    PORTAL_TELEPORT = 747
    # speed portals
    SPEED_SLOW = 200
    SPEED_NORMAL = 201
    SPEED_FAST = 202
    SPEED_VERY_FAST = 203
    SPEED_SUPER_FAST = 1334
    # pads
    PAD_YELLOW = 35
    PAD_PINK = 140
    PAD_RED = 1332
    PAD_BLUE = 67
    # orbs
    ORB_YELLOW = 36
    ORB_PINK = 141
    ORB_RED = 1333
    ORB_BLUE = 84
    ORB_GREEN = 1022
    ORB_BLACK = 1330
    ORB_TOGGLE = 1594
    ORB_DASH_GREEN = 1704
    ORB_DASH_PINK = 1751
    # triggers
    TR_COLOR = 899
    TR_MOVE = 901
    TR_PULSE = 1006
    TR_ALPHA = 1007
    TR_TOGGLE = 1049
    TR_SPAWN = 1268
    TR_ROTATE = 1346
    TR_FOLLOW = 1347
    TR_SHAKE = 1520
    TR_ANIMATE = 1585
    TR_TOUCH = 1595
    TR_COUNT = 1611
    TR_STOP = 1616
    TR_ON_DEATH = 1812
    TR_FOLLOW_PLAYER_Y = 1814
    TR_COLLISION = 1815
    TR_COLLISION_BLOCK = 1816
    TR_PICKUP = 1817
    TR_BG_EFFECT_ON = 1818
    TR_BG_EFFECT_OFF = 1819
    TR_RANDOM = 1912
    TR_ZOOM_CAMERA = 1913
    TR_STATIC_CAMERA = 1914
    TR_ENTER = 1915
    TR_OFFSET_CAMERA = 1916
    TR_START_POS = 31
    TR_TRAIL_ON = 32
    TR_TRAIL_OFF = 33
    TR_ANIMATE_KEYFRAME = 3033
    # structural / deco
    BLOCK_SQUARE = 1
    BLOCK_GRID_TOP = 2
    SPIKE = 8
    SPIKE_HALF = 39
    SPIKE_SMALL = 103
    SPIKE_INVISIBLE = 144
    ROD_TALL = 15
    ROD_MEDIUM = 16
    ROD_SHORT = 17
    DECO_SPIKE_LARGE = 18
    DECO_SPIKE_MED = 19
    DECO_SPIKE_SMALL = 20
    DECO_SPIKE_TINY = 21
    THORN_LARGE = 123
    THORN_SMALL = 127
    THORN_HAZARD = 135
    SAW_LARGE = 1705
    SAW_MEDIUM = 1706
    SAW_SMALL = 1707


class ColorChannel(IntEnum):
    """Built-in colour channels (verified: gd.docs "Level Colors"). 1..999 = custom."""

    BG = 1000
    G1 = 1001
    LINE = 1002
    LINE_3D = 1003
    OBJ = 1004
    P1 = 1005
    P2 = 1006
    LBG = 1007
    G2 = 1009
    BLACK = 1010
    WHITE = 1011
    LIGHTER = 1012
    MG = 1013
    MG2 = 1014


CUSTOM_CHANNEL_BASE = 1


class Easing(IntEnum):
    NONE = 0
    IN_OUT = 1
    IN = 2
    OUT = 3
    ELASTIC_IN_OUT = 4
    ELASTIC_IN = 5
    ELASTIC_OUT = 6
    BOUNCE_IN_OUT = 7
    BOUNCE_IN = 8
    BOUNCE_OUT = 9
    EXP_IN_OUT = 10
    EXP_IN = 11
    EXP_OUT = 12
    SINE_IN_OUT = 13
    SINE_IN = 14
    SINE_OUT = 15
    BACK_IN_OUT = 16
    BACK_IN = 17
    BACK_OUT = 18


class Speed(IntEnum):
    """The numeric value used by the header (kA4) and speed-related triggers."""

    SLOW = 0
    NORMAL = 1
    FAST = 2
    VERY_FAST = 3
    SUPER_FAST = 4


SPEED_PORTAL_OBJECT = {
    Speed.SLOW: Obj.SPEED_SLOW,
    Speed.NORMAL: Obj.SPEED_NORMAL,
    Speed.FAST: Obj.SPEED_FAST,
    Speed.VERY_FAST: Obj.SPEED_VERY_FAST,
    Speed.SUPER_FAST: Obj.SPEED_SUPER_FAST,
}


class GameMode(IntEnum):
    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6
    SWING = 7


MODE_PORTAL_OBJECT = {
    GameMode.CUBE: Obj.PORTAL_CUBE,
    GameMode.SHIP: Obj.PORTAL_SHIP,
    GameMode.BALL: Obj.PORTAL_BALL,
    GameMode.UFO: Obj.PORTAL_UFO,
    GameMode.WAVE: Obj.PORTAL_WAVE,
    GameMode.ROBOT: Obj.PORTAL_ROBOT,
    GameMode.SPIDER: Obj.PORTAL_SPIDER,
    GameMode.SWING: Obj.PORTAL_SWING,
}


class PulseTarget(IntEnum):
    CHANNEL = 0
    GROUP = 1
    PLAYER_1 = 2
    PLAYER_2 = 3
    COLOR_1 = 4
    COLOR_2 = 5


class TouchMode(IntEnum):
    TOGGLE = 0
    HOLD = 1


# Editor layer ids (prop 20 / 61). B = background, T = foreground.
Z_LAYER = {
    "B5": -5, "B4": -4, "B3": -3, "B2": -2, "B1": -1,
    "T1": 1, "T2": 2, "T3": 3, "T4": 4, "T5": 5,
}

# 1 block = 30 units (verified: gd.docs player physics).
BLOCK_UNITS = 30.0
