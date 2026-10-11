"""Music sync: turn the verified arrangement into level coordinates.

The verified facts live in ``data/music/nine_circles.json`` (tempo, beat phase,
real drop times). This module turns them into a :class:`Timeline` that converts
between musical position (bars/beats) and the level's x axis, accounting for the
speed-portal plan.

Everything the level generator places is expressed in *bars*, so gameplay lands
on the music instead of on arbitrary distances.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .gamedata import Speed
from .physics import speed_units_per_second

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "music")


@dataclass
class Section:
    name: str
    start_bar: float
    end_bar: float
    start_s: float
    end_s: float
    note: str = ""


@dataclass
class TrackProfile:
    title: str
    artist: str
    song_id: int
    bpm: float
    beat_s: float
    bar_s: float
    phase_s: float
    sections: list[Section]
    sync: dict[str, float]

    def time_at_beat(self, beat: float) -> float:
        return self.phase_s + beat * self.beat_s

    def time_at_bar(self, bar: float) -> float:
        return self.phase_s + bar * self.bar_s

    def bar_at_time(self, t: float) -> float:
        return (t - self.phase_s) / self.bar_s

    def beat_at_time(self, t: float) -> float:
        return (t - self.phase_s) / self.beat_s


def load_track(path: str | None = None) -> TrackProfile:
    path = path or os.path.join(DATA_DIR, "nine_circles.json")
    with open(path) as fh:
        d = json.load(fh)
    a = d["analysis"]
    t = d["track"]
    return TrackProfile(
        title=t["title"], artist=t["artist"], song_id=t["newgrounds_id"],
        bpm=t["bpm"], beat_s=a["beat_period_s"], bar_s=a["bar_s"],
        phase_s=a["phase_t0_s"],
        sections=[Section(s["name"], s["start_bar"], s["end_bar"],
                          s["start_s"], s["end_s"], s.get("note", ""))
                  for s in d["structure"]],
        sync={p["label"]: p["s"] for p in d["sync_points"]},
    )


# --------------------------------------------------------------------------
# Speed plan / timeline
# --------------------------------------------------------------------------


@dataclass
class SpeedSegment:
    start_bar: float
    speed: Speed


@dataclass
class Timeline:
    """Maps musical bars to level x coordinates, given a speed plan.

    x advances at ``speed_units_per_second(speed)`` units per second, so a
    section's physical length is ``duration_seconds * units_per_second``.
    """

    track: TrackProfile
    segments: list[SpeedSegment] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.segments.sort(key=lambda s: s.start_bar)

    def _active(self, bar: float) -> Speed:
        sp = self.segments[0].speed
        for seg in self.segments:
            if seg.start_bar <= bar:
                sp = seg.speed
            else:
                break
        return sp

    def x_at_bar(self, bar: float, x0: float = 0.0) -> float:
        """x position reached at a given bar, starting from ``x0`` at bar 0."""
        x = x0
        cur = 0.0
        for seg in self.segments:
            if seg.start_bar >= bar:
                break
            dt = self.track.time_at_bar(seg.start_bar) - self.track.time_at_bar(cur)
            x += speed_units_per_second(self._active(cur)) * dt
            cur = seg.start_bar
        dt = self.track.time_at_bar(bar) - self.track.time_at_bar(cur)
        x += speed_units_per_second(self._active(cur)) * dt
        return x

    def bar_at_x(self, x: float, x0: float = 0.0) -> float:
        """Inverse of :meth:`x_at_bar` (linear scan; plans are short)."""
        lo, hi = 0.0, 400.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if self.x_at_bar(mid, x0) < x:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def section_x(self, section: Section, x0: float = 0.0) -> tuple[float, float]:
        return (self.x_at_bar(section.start_bar, x0),
                self.x_at_bar(section.end_bar, x0))

    def total_x(self, end_bar: float, x0: float = 0.0) -> float:
        return self.x_at_bar(end_bar, x0)
