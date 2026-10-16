"""The level's colour script.

A deliberate palette that evolves across the level instead of generic neon
spam. Channels 1..999 are GD's creator range (verified: gd.docs "Level
Colors"), so every channel below is a custom one and can be re-coloured by
triggers on any bar line.

Channels are grouped by *role*, not by section: the whole level uses the same
set of channels and moves them between sections with colour triggers. That is
what makes a level read as one place instead of as noise.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..level import Level
from ..model import Color

# -- channel allocation (full table in docs/groups.md) --------------------
CH_SKY = 1          # background top
CH_SKY2 = 2         # background bottom
CH_GROUND = 3       # ground
CH_GROUND2 = 4      # ground line
CH_DECO_FAR = 5     # far background geometry (B5)
CH_DECO_MID = 6     # mid background geometry (B3)
CH_DECO_NEAR = 7    # gameplay-adjacent deco (B1)
CH_ACCENT = 8       # highlights, rings, gear teeth
CH_GLOW = 9         # additive light (blend mode)
CH_HAZARD = 10      # spikes and saws
CH_SOLID = 11       # solid gameplay blocks
CH_SOLID_EDGE = 12  # block detail
CH_CLINE_BODY = 13
CH_CLINE_DARK = 14
CH_CLINE_EYE = 15
CH_ANTI_A = 16      # Antigravity gradient, top
CH_ANTI_B = 17      # Antigravity gradient, bottom
CH_ANTI_EYE = 18
CH_TEXT = 19
CH_PARTICLE = 20
CH_WHITE = 21

ALL_CHANNELS = [CH_SKY, CH_SKY2, CH_GROUND, CH_GROUND2, CH_DECO_FAR,
                CH_DECO_MID, CH_DECO_NEAR, CH_ACCENT, CH_GLOW, CH_HAZARD,
                CH_SOLID, CH_SOLID_EDGE, CH_CLINE_BODY, CH_CLINE_DARK,
                CH_CLINE_EYE, CH_ANTI_A, CH_ANTI_B, CH_ANTI_EYE, CH_TEXT,
                CH_PARTICLE, CH_WHITE]


@dataclass(frozen=True)
class Palette:
    """A named colour identity for one section."""

    name: str
    sky: tuple[int, int, int]
    sky2: tuple[int, int, int]
    ground: tuple[int, int, int]
    ground2: tuple[int, int, int]
    deco_far: tuple[int, int, int]
    deco_mid: tuple[int, int, int]
    deco_near: tuple[int, int, int]
    accent: tuple[int, int, int]
    glow: tuple[int, int, int]
    hazard: tuple[int, int, int]
    solid: tuple[int, int, int]
    solid_edge: tuple[int, int, int]
    text: tuple[int, int, int]
    particle: tuple[int, int, int]


#: channel -> Palette field name
FIELDS = {
    CH_SKY: "sky", CH_SKY2: "sky2", CH_GROUND: "ground",
    CH_GROUND2: "ground2", CH_DECO_FAR: "deco_far", CH_DECO_MID: "deco_mid",
    CH_DECO_NEAR: "deco_near", CH_ACCENT: "accent", CH_GLOW: "glow",
    CH_HAZARD: "hazard", CH_SOLID: "solid", CH_SOLID_EDGE: "solid_edge",
    CH_TEXT: "text", CH_PARTICLE: "particle",
}

#: the mascot channels never change, so the characters stay recognisable
FIXED = {
    CH_CLINE_BODY: (240, 237, 250),
    CH_CLINE_DARK: (62, 52, 96),
    CH_CLINE_EYE: (32, 28, 52),
    CH_ANTI_A: (236, 72, 64),
    CH_ANTI_B: (60, 120, 230),
    CH_ANTI_EYE: (26, 26, 40),
    CH_WHITE: (255, 255, 255),
}


def _p(name, sky, sky2, ground, ground2, far, mid, near, accent, glow,
       hazard, solid, edge, text, particle) -> Palette:
    return Palette(name, sky, sky2, ground, ground2, far, mid, near, accent,
                   glow, hazard, solid, edge, text, particle)


# Palette identities read off the supplied style sheet
# (rfimage/Gemini_Generated_Image_e6jui6e6jui6e6ju.jpg) and the two
# HYPER-DIMENSION concept frames.
P_INTRO = _p("cold void", (8, 10, 28), (16, 30, 62), (6, 8, 22), (14, 26, 54),
             (44, 92, 168), (70, 140, 210), (110, 190, 230), (250, 214, 120),
             (120, 220, 255), (255, 92, 120), (38, 52, 92), (96, 130, 190),
             (226, 240, 255), (150, 220, 255))

P_BUILD = _p("teal ascent", (6, 16, 30), (14, 44, 70), (4, 12, 24),
             (12, 38, 62), (28, 120, 140), (60, 190, 190), (120, 235, 220),
             (255, 214, 120), (140, 255, 240), (255, 120, 90), (30, 64, 84),
             (86, 150, 176), (230, 250, 250), (150, 250, 240))

P_DROP1 = _p("hot magenta", (12, 4, 26), (44, 10, 62), (8, 3, 18), (32, 8, 48),
             (120, 24, 150), (200, 40, 190), (255, 90, 210), (255, 245, 255),
             (255, 120, 230), (255, 70, 110), (52, 14, 66), (150, 60, 190),
             (255, 235, 255), (255, 150, 240))

P_COLLIDE = _p("colour collision", (6, 22, 16), (16, 54, 32), (4, 16, 10),
               (12, 42, 24), (150, 240, 60), (60, 230, 255), (240, 60, 200),
               (255, 255, 255), (150, 255, 120), (255, 90, 90), (22, 56, 34),
               (120, 200, 90), (245, 255, 245), (190, 255, 140))

P_WAVE = _p("neon spine", (18, 4, 30), (48, 10, 66), (12, 3, 20), (36, 8, 50),
            (255, 60, 190), (180, 40, 220), (255, 140, 240), (255, 255, 255),
            (255, 150, 240), (255, 60, 120), (44, 10, 56), (160, 50, 200),
            (255, 240, 255), (255, 170, 250))

P_ROBOT = _p("alive architecture", (34, 8, 28), (66, 20, 54), (24, 6, 20),
             (52, 16, 44), (255, 110, 160), (190, 110, 220), (255, 200, 230),
             (255, 240, 250), (255, 170, 220), (255, 80, 120), (60, 20, 46),
             (170, 110, 190), (255, 245, 252), (255, 190, 235))

P_GROOVE = _p("surreal void", (6, 6, 14), (20, 18, 38), (4, 4, 10),
              (16, 14, 32), (236, 120, 190), (120, 90, 180), (255, 170, 220),
              (255, 255, 255), (200, 160, 255), (240, 90, 110), (26, 22, 44),
              (110, 96, 160), (245, 242, 255), (200, 170, 255))

P_BREAK = _p("cold hush", (10, 12, 24), (26, 30, 56), (6, 8, 18), (20, 24, 48),
             (90, 110, 180), (130, 150, 220), (190, 210, 255), (255, 250, 220),
             (170, 200, 255), (255, 110, 130), (30, 34, 60), (110, 125, 180),
             (232, 240, 255), (180, 205, 255))

P_FINAL = _p("climax forge", (30, 8, 4), (72, 24, 6), (22, 6, 3), (58, 18, 5),
             (255, 150, 30), (255, 210, 120), (255, 240, 190), (255, 255, 240),
             (255, 220, 150), (255, 70, 40), (64, 22, 8), (200, 120, 40),
             (255, 250, 235), (255, 210, 140))

P_OUTRO = _p("white gold", (214, 220, 238), (176, 190, 226), (196, 204, 228),
             (160, 176, 216), (90, 200, 255), (255, 255, 255), (120, 240, 200),
             (60, 80, 130), (150, 220, 255), (230, 90, 110), (226, 232, 246),
             (150, 170, 210), (36, 46, 78), (170, 210, 255))

SECTION_PALETTE = {
    "intro": P_INTRO, "build": P_BUILD, "drop1": P_DROP1,
    "drop1b": P_COLLIDE, "fill": P_WAVE, "drop2": P_WAVE,
    "drop2b": P_ROBOT, "groove": P_GROOVE, "break": P_BREAK,
    "build2": P_BREAK, "final": P_FINAL, "outro": P_OUTRO,
}


def apply_palette(level: Level, pal: Palette) -> None:
    """Write a palette into the level's colour channels."""
    for ch, field in FIELDS.items():
        r, g, b = getattr(pal, field)
        level.colors[ch] = Color(channel=ch, r=r, g=g, b=b,
                                 blending=(field == "glow"))
    for ch, (r, g, b) in FIXED.items():
        level.colors[ch] = Color(channel=ch, r=r, g=g, b=b)


def apply_initial(level: Level) -> None:
    """Starting colours: the intro palette, plus the built-in channels."""
    apply_palette(level, P_INTRO)
    from ..gamedata import ColorChannel as C
    level.colors[C.BG] = Color(C.BG, *P_INTRO.sky)
    level.colors[C.G1] = Color(C.G1, *P_INTRO.ground)
    level.colors[C.G2] = Color(C.G2, *P_INTRO.ground2)
    level.colors[C.LINE] = Color(C.LINE, 255, 255, 255)
    level.colors[C.OBJ] = Color(C.OBJ, *P_INTRO.solid)
    level.colors[C.P1] = Color(C.P1, player=1)
    level.colors[C.P2] = Color(C.P2, player=2)
