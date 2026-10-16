"""The music map: measured audio analysis + the curated section design.

``data/music/the_flames_of_fate.json`` is produced by
``tools/analyze_song.py`` and holds *measurements* (tempo, beat grid, per-bar
band energies, detected structural boundaries). This module adds the *design*:
which gameplay goes where, at what speed, and how intense the visuals are.

The design is expressed in **level bars** (bar 0 starts at the first downbeat,
``level_grid.first_beat_in_level_s`` seconds into the level). ``verify_design``
checks every design boundary against the measured boundaries, so a section
cannot drift away from a real change in the music without a test failing.

Terminology
-----------
``kind``       measured character of the music (drop / build / break / outro)
``mode``       the game mode the section opens in
``speed``      the player speed through the section
``intensity``  0..4 hint used by the decoration pass (0 calm, 4 peak)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .gamedata import GameMode, Speed
from .timeline import SpeedSpan, Timeline

DEFAULT_JSON = os.path.join(os.path.dirname(__file__), "..", "..", "data",
                            "music", "the_flames_of_fate.json")


@dataclass(frozen=True)
class SectionDesign:
    name: str
    kind: str
    start_bar: int
    end_bar: int
    mode: GameMode
    speed: Speed
    intensity: int
    note: str

    @property
    def bars(self) -> int:
        return self.end_bar - self.start_bar


# --------------------------------------------------------------------------
# The design. Bar numbers are level bars; every boundary below is either a
# measured structural boundary from analyze_song.py or an 8-bar phrase line.
# --------------------------------------------------------------------------
DESIGN: list[SectionDesign] = [
    SectionDesign("intro", "build", 0, 8, GameMode.CUBE, Speed.NORMAL, 1,
                  "calm reveal: both mascots drift in, easy cube, deco at B5-B4"),
    SectionDesign("build", "build", 8, 15, GameMode.SHIP, Speed.FAST, 2,
                  "build-up: cube into ship, deco layers fill in, palette warms"),
    SectionDesign("drop1", "drop", 15, 24, GameMode.SHIP, Speed.FAST, 3,
                  "first drop: ship rhythm locked to the kick, camera zoom in"),
    SectionDesign("drop1b", "drop", 24, 30, GameMode.UFO, Speed.FAST, 3,
                  "UFO beats, mascot cameo, transitions start firing"),
    SectionDesign("fill", "drop", 30, 32, GameMode.WAVE, Speed.FAST, 3,
                  "two-bar fill: wipe transition into the wave"),
    SectionDesign("drop2", "drop", 32, 40, GameMode.WAVE, Speed.FAST, 4,
                  "wave corridors on the melody, brightest palette so far"),
    SectionDesign("drop2b", "drop", 40, 48, GameMode.ROBOT, Speed.FAST, 4,
                  "robot hold-jumps, Antigravity defies gravity, screen shake"),
    SectionDesign("groove", "drop", 48, 61, GameMode.BALL, Speed.NORMAL, 2,
                  "technical groove: ball then spider then swing"),
    SectionDesign("break", "break", 61, 63, GameMode.SWING, Speed.FAST, 1,
                  "the only real dip in the track: quiet 2 bars, mascot scene"),
    SectionDesign("build2", "build", 63, 66, GameMode.SWING, Speed.FAST, 3,
                  "short second build: swing climbs back to full brightness"),
    SectionDesign("final", "drop", 66, 79, GameMode.CUBE, Speed.VERY_FAST, 4,
                  "final drop: fastest and densest, brief 4x burst, duo showcase"),
    SectionDesign("outro", "outro", 79, 94, GameMode.CUBE, Speed.NORMAL, 1,
                  "outro: credits text, mascots wave, end wall at the music end"),
]

BY_NAME = {s.name: s for s in DESIGN}



# --------------------------------------------------------------------------
# Song map
# --------------------------------------------------------------------------


@dataclass
class SongMap:
    raw: dict
    sections: list[SectionDesign] = field(default_factory=lambda: list(DESIGN))

    # -- measured facts --------------------------------------------------
    @property
    def title(self) -> str:
        return self.raw["track"]["title"]

    @property
    def song_id(self) -> int:
        return int(self.raw["track"]["newgrounds_id"])

    @property
    def bpm(self) -> float:
        return float(self.raw["analysis"]["bpm"])

    @property
    def beat_s(self) -> float:
        return float(self.raw["analysis"]["beat_period_s"])

    @property
    def bar_s(self) -> float:
        return float(self.raw["analysis"]["bar_s"])

    @property
    def phase_s(self) -> float:
        return float(self.raw["analysis"]["phase_t0_s"])

    @property
    def start_s(self) -> float:
        return float(self.raw["segment"]["start_s"])

    @property
    def end_s(self) -> float:
        return float(self.raw["segment"]["end_s"])

    @property
    def length_s(self) -> float:
        return self.end_s - self.start_s

    @property
    def first_beat_s(self) -> float:
        return float(self.raw["level_grid"]["first_beat_in_level_s"])

    def measured_boundaries(self) -> list[int]:
        """Level-bar indices where the analysis found a structural change."""
        base = int(self.raw["segment"]["start_bar"])
        return sorted({int(s["start_bar"]) - base for s in self.raw["structure"]})

    def timeline(self) -> Timeline:
        """Build the :class:`Timeline` from the design's speed plan."""
        spans: list[SpeedSpan] = []
        for s in self.sections:
            t = self.time_at_bar(s.start_bar)
            if not spans or spans[-1].speed != s.speed:
                spans.append(SpeedSpan(t, s.speed))
        return Timeline(beat_s=self.beat_s, bar_s=self.bar_s,
                        first_beat_s=self.first_beat_s, spans=spans)

    # -- design -> time / bar -------------------------------------------
    def time_at_bar(self, bar: float) -> float:
        return self.first_beat_s + bar * self.bar_s

    def bar_at_time(self, t: float) -> float:
        return (t - self.first_beat_s) / self.bar_s

    def time_at_beat(self, beat: float) -> float:
        return self.first_beat_s + beat * self.beat_s

    def bar_range(self, name: str) -> tuple[int, int]:
        s = BY_NAME[name]
        return (s.start_bar, s.end_bar)

    def section_time_range(self, name: str) -> tuple[float, float]:
        s = BY_NAME[name]
        return (self.time_at_bar(s.start_bar), self.time_at_bar(s.end_bar))

    def section_x_range(self, tl: Timeline, name: str) -> tuple[float, float]:
        a, b = self.section_time_range(name)
        return (tl.x_at_time(a), tl.x_at_time(b))

    def section_x(self, tl: Timeline) -> dict[str, tuple[float, float]]:
        return {s.name: self.section_x_range(tl, s.name) for s in self.sections}

    def length_units(self, tl: Timeline) -> float:
        return tl.x_at_time(self.time_at_bar(self.sections[-1].end_bar))

    def beats_in(self, name: str) -> int:
        return BY_NAME[name].bars * 4

    def describe(self) -> str:
        tl = self.timeline()
        lines = [f"{self.title} - NG {self.song_id}, {self.bpm:.2f} BPM, "
                 f"bar {self.bar_s:.4f}s",
                 f"segment {self.start_s}..{self.end_s}s "
                 f"({self.length_s:.1f}s), song offset kA13={self.start_s}",
                 f"level x length {self.length_units(tl):.0f} units "
                 f"({self.length_units(tl) / 30:.1f} blocks)",
                 f"speeds: {tl.describe()}"]
        for s in self.sections:
            t0, t1 = self.section_time_range(s.name)
            x0, x1 = self.section_x_range(tl, s.name)
            lines.append(
                f"  {s.name:8s} bar {s.start_bar:>3d}-{s.end_bar:<3d} "
                f"t {t0:7.3f}-{t1:7.3f}s x {x0:8.0f}-{x1:8.0f} "
                f"{s.mode.name.lower():6s} {int(s.speed)}x int{s.intensity} "
                f"{s.kind}")
        return "\n".join(lines)


def load_song(path: str | None = None) -> SongMap:
    with open(path or DEFAULT_JSON, encoding="utf-8") as fh:
        return SongMap(json.load(fh))


# --------------------------------------------------------------------------
# Design validation
# --------------------------------------------------------------------------


def verify_design(song: SongMap, *, tolerance_bars: int = 1) -> list[str]:
    """Return a list of problems with the design (empty = consistent).

    Every section boundary must either be a measured structural boundary
    (within ``tolerance_bars``) or land on a multiple of 4 bars from the level
    start, so the gameplay cannot drift away from the music unnoticed.
    """
    problems: list[str] = []
    measured = set(song.measured_boundaries())
    if song.sections[0].start_bar != 0:
        problems.append("the first section must start at bar 0")
    for s in song.sections:
        if s.end_bar <= s.start_bar:
            problems.append(f"{s.name}: end_bar must exceed start_bar")
        if not (0 <= s.intensity <= 4):
            problems.append(f"{s.name}: intensity {s.intensity} out of range")
        for bar in (s.start_bar, s.end_bar):
            near = any(abs(bar - m) <= tolerance_bars for m in measured)
            if not (near or bar % 4 == 0):
                problems.append(
                    f"{s.name}: boundary bar {bar} is neither a measured "
                    f"boundary (within {tolerance_bars}) nor a 4-bar phrase line")
    for a, b in zip(song.sections, song.sections[1:]):
        if a.end_bar != b.start_bar:
            problems.append(f"gap/overlap between {a.name} and {b.name}")
    tl = song.timeline()
    if abs(tl.time_at_x(tl.x_at_time(10.0)) - 10.0) > 1e-6:
        problems.append("timeline round trip failed")
    return problems
