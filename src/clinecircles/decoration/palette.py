"""The CLINE CIRCLES colour script.

A deliberate palette that evolves across the level instead of generic neon
spam. Each section owns a small set of custom colour channels (1..999, which GD
reserves for creators - verified in gd.docs "Level Colors"), and the sections
hand over to each other through colour triggers on the downbeats.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..level import Level
from ..model import Color

# Custom channels used by the level (1..999 are the creator range).
CH_SKY = 1
CH_SKY2 = 2
CH_GROUND = 3
CH_GROUND2 = 4
CH_DECO = 5
CH_DECO2 = 6
CH_ACCENT = 7
CH_EYE = 8
CH_TEETH = 9
CH_ROBOT = 10
CH_ROBOT_EYE = 11
CH_ROBOT_PUPIL = 12
CH_BOSS = 13
CH_GLITCH = 14
CH_TEXT = 15

ALL_CHANNELS = [CH_SKY, CH_SKY2, CH_GROUND, CH_GROUND2, CH_DECO, CH_DECO2,
                CH_ACCENT, CH_EYE, CH_TEETH, CH_ROBOT, CH_ROBOT_EYE,
                CH_ROBOT_PUPIL, CH_BOSS, CH_GLITCH, CH_TEXT]


@dataclass(frozen=True)
class Palette:
    """A named colour identity for one section."""

    name: str
    sky: tuple[int, int, int]
    sky2: tuple[int, int, int]
    ground: tuple[int, int, int]
    ground2: tuple[int, int, int]
    deco: tuple[int, int, int]
    deco2: tuple[int, int, int]
    accent: tuple[int, int, int]
    eye: tuple[int, int, int]
    teeth: tuple[int, int, int]
    robot: tuple[int, int, int]
    robot_eye: tuple[int, int, int]
    robot_pupil: tuple[int, int, int]
    boss: tuple[int, int, int]
    glitch: tuple[int, int, int]
    text: tuple[int, int, int]


# --------------------------------------------------------------------------
# Section identities
# --------------------------------------------------------------------------

P_INTRO = Palette(
    "intro (indigo calm)",
    sky=(10, 12, 30), sky2=(22, 20, 58), ground=(16, 14, 40), ground2=(28, 24, 66),
    deco=(52, 46, 110), deco2=(80, 70, 150), accent=(120, 200, 255),
    eye=(140, 220, 255), teeth=(255, 255, 255), robot=(190, 200, 235),
    robot_eye=(90, 235, 255), robot_pupil=(18, 20, 40), boss=(90, 60, 160),
    glitch=(255, 90, 200), text=(200, 225, 255))

P_DROP1 = Palette(
    "drop1 (hot magenta)",
    sky=(28, 4, 24), sky2=(64, 8, 48), ground=(22, 2, 18), ground2=(48, 6, 34),
    deco=(180, 24, 110), deco2=(255, 60, 150), accent=(255, 210, 80),
    eye=(255, 90, 200), teeth=(255, 240, 240), robot=(240, 200, 220),
    robot_eye=(255, 240, 90), robot_pupil=(40, 0, 20), boss=(255, 40, 120),
    glitch=(90, 255, 220), text=(255, 220, 240))

P_BREAK = Palette(
    "breakdown (bone teal)",
    sky=(8, 18, 20), sky2=(16, 34, 36), ground=(6, 14, 16), ground2=(14, 30, 32),
    deco=(70, 110, 110), deco2=(120, 170, 165), accent=(220, 230, 225),
    eye=(200, 255, 250), teeth=(235, 230, 220), robot=(225, 230, 225),
    robot_eye=(150, 255, 240), robot_pupil=(10, 20, 22), boss=(60, 120, 110),
    glitch=(255, 255, 255), text=(230, 245, 240))

P_DROP2 = Palette(
    "drop2 (toxic green)",
    sky=(6, 20, 6), sky2=(14, 44, 12), ground=(4, 16, 4), ground2=(10, 36, 8),
    deco=(60, 200, 60), deco2=(140, 255, 90), accent=(255, 255, 255),
    eye=(180, 255, 60), teeth=(255, 255, 200), robot=(200, 235, 190),
    robot_eye=(255, 80, 80), robot_pupil=(6, 16, 6), boss=(120, 255, 40),
    glitch=(255, 0, 90), text=(230, 255, 210))

P_BOSS = Palette(
    "boss (black gold)",
    sky=(4, 4, 6), sky2=(16, 12, 4), ground=(2, 2, 4), ground2=(12, 9, 2),
    deco=(255, 190, 40), deco2=(255, 235, 150), accent=(255, 255, 255),
    eye=(255, 200, 60), teeth=(255, 255, 255), robot=(235, 225, 200),
    robot_eye=(255, 60, 60), robot_pupil=(8, 6, 4), boss=(255, 170, 20),
    glitch=(255, 40, 40), text=(255, 245, 220))

P_FINALE = Palette(
    "finale (warm white)",
    sky=(40, 36, 44), sky2=(90, 80, 90), ground=(30, 26, 34), ground2=(70, 62, 72),
    deco=(255, 230, 200), deco2=(255, 255, 255), accent=(255, 200, 120),
    eye=(255, 245, 220), teeth=(255, 255, 255), robot=(255, 250, 245),
    robot_eye=(255, 180, 90), robot_pupil=(30, 24, 20), boss=(255, 210, 140),
    glitch=(255, 255, 255), text=(255, 255, 255))


SECTION_PALETTES = {
    "intro": P_INTRO,
    "drop1_ship": P_DROP1,
    "drop1_ufo": P_DROP1,
    "breakdown_wave": P_BREAK,
    "breakdown_ball_spider": P_BREAK,
    "drop2_robot": P_DROP2,
    "drop2_swing": P_DROP2,
    "boss_fight": P_BOSS,
    "finale": P_FINALE,
}

_FIELDS = {
    CH_SKY: "sky", CH_SKY2: "sky2", CH_GROUND: "ground",
    CH_GROUND2: "ground2", CH_DECO: "deco", CH_DECO2: "deco2",
    CH_ACCENT: "accent", CH_EYE: "eye", CH_TEETH: "teeth",
    CH_ROBOT: "robot", CH_ROBOT_EYE: "robot_eye",
    CH_ROBOT_PUPIL: "robot_pupil", CH_BOSS: "boss", CH_GLITCH: "glitch",
    CH_TEXT: "text",
}


def apply_palette(level: Level, pal: Palette) -> None:
    """Write a palette into the level's colour channels."""
    for ch, fieldname in _FIELDS.items():
        r, g, b = getattr(pal, fieldname)
        level.colors[ch] = Color(channel=ch, r=r, g=g, b=b)


def apply_initial(level: Level) -> None:
    """Set the starting colours (the intro palette)."""
    apply_palette(level, P_INTRO)
    # built-in channels keep the level readable
    C = __import__("clinecircles.gamedata", fromlist=["ColorChannel"]).ColorChannel
    level.colors[C.BG].r, level.colors[C.BG].g, level.colors[C.BG].b = P_INTRO.sky
    level.colors[C.G1].r, level.colors[C.G1].g, level.colors[C.G1].b = P_INTRO.ground
