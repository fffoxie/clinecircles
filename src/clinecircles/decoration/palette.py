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
# Section identities - taken from the supplied style sheet
# (rfimage/Gemini_Generated_Image_e6jui6e6jui6e6ju.jpg, panels 1-8).
# --------------------------------------------------------------------------

def _pal(name, sky, sky2, ground, ground2, deco, deco2, accent, eye, teeth,
         robot, robot_eye, robot_pupil, boss, glitch, text):
    return Palette(name, sky, sky2, ground, ground2, deco, deco2, accent,
                   eye, teeth, robot, robot_eye, robot_pupil, boss, glitch, text)


# panel 1 - IMPOSSIBLE GEOMETRY: teal/orange isometric on deep navy
P_INTRO = _pal(
    "impossible geometry",
    sky=(10, 12, 34), sky2=(20, 40, 62), ground=(8, 10, 28), ground2=(16, 34, 54),
    deco=(64, 196, 190), deco2=(240, 140, 60), accent=(255, 214, 120),
    eye=(120, 240, 235), teeth=(240, 246, 255), robot=(236, 232, 248),
    robot_eye=(255, 236, 190), robot_pupil=(28, 26, 52), boss=(240, 140, 60),
    glitch=(255, 120, 200), text=(228, 240, 255))

# panel 3 - TWISTING CORRIDOR: neon magenta/cyan on black
P_DROP1 = _pal(
    "twisting corridor",
    sky=(8, 4, 22), sky2=(30, 10, 56), ground=(6, 3, 18), ground2=(22, 8, 44),
    deco=(236, 40, 200), deco2=(60, 230, 255), accent=(255, 255, 255),
    eye=(255, 90, 220), teeth=(255, 250, 255), robot=(238, 234, 250),
    robot_eye=(255, 240, 120), robot_pupil=(30, 8, 40), boss=(236, 40, 200),
    glitch=(120, 255, 240), text=(255, 230, 250))

# panel 4 - COLOR COLLISION: lime / magenta / cyan
P_COLLIDE = _pal(
    "color collision",
    sky=(6, 20, 14), sky2=(14, 52, 30), ground=(4, 16, 10), ground2=(10, 42, 24),
    deco=(150, 240, 60), deco2=(240, 60, 200), accent=(60, 230, 255),
    eye=(200, 255, 90), teeth=(255, 255, 255), robot=(240, 244, 236),
    robot_eye=(255, 90, 90), robot_pupil=(10, 26, 14), boss=(240, 60, 200),
    glitch=(255, 255, 255), text=(240, 255, 220))

# panel 5 - WAVE SECTION: magenta / dark
P_BREAK = _pal(
    "wave section",
    sky=(16, 4, 26), sky2=(44, 8, 60), ground=(12, 3, 20), ground2=(34, 6, 48),
    deco=(255, 60, 190), deco2=(180, 40, 220), accent=(255, 220, 250),
    eye=(255, 140, 220), teeth=(250, 240, 255), robot=(240, 236, 250),
    robot_eye=(150, 240, 255), robot_pupil=(26, 6, 34), boss=(255, 60, 190),
    glitch=(90, 255, 240), text=(255, 235, 250))

# panel 2 - SURREAL VOID: near-black with pink eyes
P_VOID = _pal(
    "surreal void",
    sky=(6, 6, 12), sky2=(18, 16, 34), ground=(4, 4, 10), ground2=(14, 12, 28),
    deco=(236, 120, 190), deco2=(120, 90, 180), accent=(255, 255, 255),
    eye=(255, 170, 220), teeth=(245, 240, 250), robot=(240, 238, 248),
    robot_eye=(255, 200, 120), robot_pupil=(16, 14, 30), boss=(236, 120, 190),
    glitch=(120, 240, 255), text=(240, 240, 255))

# panel 7 - ALIVE ARCHITECTURE: pink / purple
P_ALIVE = _pal(
    "alive architecture",
    sky=(30, 8, 26), sky2=(60, 20, 52), ground=(22, 6, 20), ground2=(48, 16, 42),
    deco=(255, 110, 160), deco2=(190, 110, 220), accent=(255, 240, 250),
    eye=(255, 200, 230), teeth=(255, 250, 250), robot=(244, 240, 250),
    robot_eye=(255, 120, 140), robot_pupil=(32, 8, 26), boss=(255, 110, 160),
    glitch=(255, 255, 255), text=(255, 240, 250))

# panel 8 - CLIMAX PERSPECTIVE: orange / red / gold
P_BOSS = _pal(
    "climax perspective",
    sky=(26, 8, 4), sky2=(64, 22, 6), ground=(20, 6, 3), ground2=(52, 18, 5),
    deco=(255, 150, 30), deco2=(255, 210, 120), accent=(255, 255, 240),
    eye=(255, 190, 60), teeth=(255, 255, 255), robot=(250, 242, 230),
    robot_eye=(255, 70, 40), robot_pupil=(26, 8, 4), boss=(255, 120, 20),
    glitch=(255, 60, 40), text=(255, 248, 225))

# panel 6 - DIMENSIONAL TRANSITION: bright neon portal on white
P_FINALE = _pal(
    "dimensional transition",
    sky=(232, 236, 246), sky2=(200, 210, 235), ground=(214, 220, 236),
    ground2=(180, 194, 228), deco=(90, 200, 255), deco2=(255, 255, 255),
    accent=(120, 240, 200), eye=(120, 200, 255), teeth=(255, 255, 255),
    robot=(250, 250, 255), robot_eye=(80, 200, 255), robot_pupil=(40, 46, 70),
    boss=(120, 240, 200), glitch=(255, 255, 255), text=(40, 50, 80))

SECTION_PALETTES = {
    "intro": P_INTRO,
    "drop1_ship": P_DROP1,
    "drop1_ufo": P_COLLIDE,
    "breakdown_wave": P_BREAK,
    "breakdown_ball_spider": P_VOID,
    "drop2_robot": P_ALIVE,
    "drop2_swing": P_DROP1,
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
