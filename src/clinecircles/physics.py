"""Geometry Dash player physics constants.

Confidence levels are stated explicitly per constant. Anything marked
VERIFIED comes from gd.docs (boomlings.dev). Anything marked ESTIMATED is a
best-effort value used only by the offline playability checker, with the level
designed to tolerate the error.

Unit conventions (VERIFIED, gd.docs):
    1 block  = 30 units
    1 Vel    = 60 units / second
    tick rate = 240 ticks / second (GD 2.2 internal physics)
"""

from __future__ import annotations

from dataclasses import dataclass

from .gamedata import BLOCK_UNITS

# --- VERIFIED base units -------------------------------------------------
TICK_RATE = 240.0
UNITS_PER_VEL = 60.0
VELS_PER_TICK_TO_UNITS = UNITS_PER_VEL / TICK_RATE  # 0.25 units per (Vel*tick)

# --- VERIFIED horizontal speeds (units/second) ---------------------------
# Cross-validated: wave's documented vertical speeds (6.457 / 7.8 / 9.6 Vels at
# 2x/3x/4x) exactly equal these horizontal speeds / 60, and gd.docs states a
# wave's vertical speed matches its horizontal speed.
SPEED_UNITS_PER_SECOND = {
    0: 251.16,  # 0.5x  (8.372 blocks/s)
    1: 311.58,  # 1x    (10.386 blocks/s)  = 5.193 Vels
    2: 387.42,  # 2x    (12.914 blocks/s)  = 6.457 Vels
    3: 468.00,  # 3x    (15.6   blocks/s)  = 7.8   Vels
    4: 576.00,  # 4x    (19.2   blocks/s)  = 9.6   Vels
}

# --- VERIFIED jump / hold velocities, in Vels, indexed by speed (0..4) ---
# gd.docs "Gamemodes". 0.5x column was truncated in the source; values are
# carried over from 1x and marked ESTIMATED.
CUBE_JUMP_VEL = {0: 11.18, 1: 11.18, 2: 11.42, 3: 11.23, 4: 11.23}  # 0 ESTIMATED
ROBOT_HOLD_VEL = {0: 5.31, 1: 5.59, 2: 5.71, 3: 5.615, 4: 5.615}
BALL_CLICK_VEL = {0: 3.354, 1: 3.354, 2: 3.426, 3: 3.369, 4: 3.369}  # 0,1 = 0.3*cube
UFO_CLICK_VEL = {0: 7.0, 1: 7.0, 2: 7.0, 3: 7.0, 4: 7.0}  # 1x ESTIMATED
WAVE_VEL = {0: 4.186, 1: 5.193, 2: 6.457, 3: 7.8, 4: 9.6}  # = horizontal speed
SHIP_HOLD_VEL = 8.0   # VERIFIED
SHIP_DROP_VEL = -6.4  # VERIFIED

# --- VERIFIED terminal (falling) velocities, in Vels ---------------------
MAX_FALL_VEL = {
    "cube": 15.0, "ship": 6.4, "ball": 15.0, "ufo": 6.4, "wave": 15.0,
    "robot": 15.0, "spider": 15.0, "swing": 8.0,
}
SHIP_MAX_RISE_VEL = 8.0  # VERIFIED

# --- ESTIMATED gravity acceleration (Vels per tick) ----------------------
# 1x value is VERIFIED (gd.docs: "in the case of 240tps, that would be
# 11.18 - 0.216"). The others are ESTIMATED to keep the cube's jump arc
# plausible; the level is built with >= 1.5 blocks of clearance so a 20% error
# here cannot make a section impossible.
GRAVITY_VELS_PER_TICK = {0: 0.216, 1: 0.216, 2: 0.252, 3: 0.288, 4: 0.324}

# --- VERIFIED orb multipliers (relative to the cube jump velocity) -------
ORB_MULT = {
    "cube": {"yellow": 1.0, "pink": 0.72, "red": 1.38, "blue": -1.0},
    "ship": {"yellow": 1.0, "pink": 0.37, "red": 1.0, "blue": -0.7},
    "ball": {"yellow": 0.7, "pink": 0.77, "red": 1.34, "blue": -1.0},
    "ufo": {"yellow": 1.0, "pink": 0.42, "red": 1.02, "blue": -1.0},
    "robot": {"yellow": 0.9, "pink": 0.72, "red": 1.28, "blue": -1.0},
    "spider": {"yellow": 0.7, "pink": 0.77, "red": 1.34, "blue": -1.0},
    "wave": {},  # blue/green only toggle gravity
}
ORB_BLUE_TOGGLES = True   # blue orbs multiply then toggle gravity (VERIFIED)
ORB_GREEN_TOGGLES = True  # green orbs multiply by -1 then toggle (VERIFIED)

# --- VERIFIED pad velocities (Vels, relative to gravity direction) -------
PAD_VEL = {
    "cube": {"yellow": 16.0, "pink": 10.4, "red": 20.0, "blue": 6.4},
    "ship": {"yellow": 16.0, "pink": 5.6, "red": 10.08, "blue": 6.4},
    "ball": {"yellow": 9.6, "pink": 6.72, "red": 12.0, "blue": 3.84},
    "ufo": {"yellow": 16.0, "pink": 6.4, "red": 9.6, "blue": 6.4},
    "robot": {"yellow": 16.0, "pink": 10.4, "red": 20.0, "blue": 6.4},
    "spider": {"yellow": 9.6, "pink": 6.72, "red": 12.0, "blue": 3.84},
    "swing": {"yellow": 9.6, "pink": 6.24, "red": 12.0, "blue": 3.84},
}
PAD_BLUE_TOGGLES = True  # VERIFIED

# --- VERIFIED hitboxes (units) ------------------------------------------
@dataclass(frozen=True)
class Hitbox:
    blue: float   # inner (non-lethal) hitbox size, square
    red: float    # outer (lethal) hitbox size, square


HITBOX = {
    "cube": Hitbox(9.0, 30.0),
    "ship": Hitbox(9.0, 30.0),
    "ball": Hitbox(9.0, 30.0),
    "ufo": Hitbox(9.0, 30.0),
    "wave": Hitbox(3.0, 10.0),
    "robot": Hitbox(9.0, 30.0),
    "spider": Hitbox(9.0, 27.5),
    "swing": Hitbox(9.0, 30.0),
}

# Vertical grid sizes used by flight modes (VERIFIED, GD wiki Portals page).
VERTICAL_GRID = {"ship": 10.0, "ufo": 10.0, "wave": 10.0, "ball": 8.0,
                 "spider": 9.0, "cube": None, "robot": None, "swing": None}


def speed_units_per_second(speed: int) -> float:
    return SPEED_UNITS_PER_SECOND[int(speed)]


def speed_blocks_per_second(speed: int) -> float:
    return speed_units_per_second(speed) / BLOCK_UNITS


def cube_jump_height_blocks(speed: int = 1, gravity_mult: float = 1.0) -> float:
    """Apex height of a cube jump, in blocks (uses the constants above)."""
    v0 = CUBE_JUMP_VEL[speed]
    g = GRAVITY_VELS_PER_TICK[speed] * gravity_mult
    apex_vel_ticks = (v0 * v0) / (2 * g)
    return apex_vel_ticks * VELS_PER_TICK_TO_UNITS / BLOCK_UNITS


def cube_jump_length_blocks(speed: int = 1, gravity_mult: float = 1.0) -> float:
    """Horizontal distance covered by a full cube jump, in blocks."""
    v0 = CUBE_JUMP_VEL[speed]
    g = GRAVITY_VELS_PER_TICK[speed] * gravity_mult
    airtime_s = (2 * v0 * UNITS_PER_VEL) / (g * UNITS_PER_VEL * TICK_RATE)
    return speed_units_per_second(speed) * airtime_s / BLOCK_UNITS
