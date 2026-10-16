"""Musical time <-> level x axis, across speed changes.

Two clocks have to be reconciled:

* the **music grid**, absolute in the audio: beat ``n`` happens at
  ``audio_time = phase_t0 + n * beat_s``. Because the level's song offset
  (``kA13``) starts playback at ``segment.start_s``, level time is
  ``audio_time - segment.start_s``.
* the **level's x axis**, which advances at the *current* player speed:
  ``dx = speed_units_per_second(speed) * dt``. A speed portal therefore changes
  the units-per-beat rate from that point on, so x is a piecewise integral.

Everything the generator places is expressed as a **beat index** or a **level
time** and converted to x through this module, so gameplay lands on the music
instead of on arbitrary distances.

Verified speed constants (see ids.py / physics.py for provenance):

===========  ====================
speed        units per second
===========  ====================
0.5x          251.16
1x            311.58
2x            387.42
3x            468.00
4x            576.00
===========  ====================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .gamedata import Speed
from .ids import SPEED_UNITS_PER_SECOND

SPEED_BY_NAME = {"0.5x": Speed.SLOW, "1x": Speed.NORMAL, "2x": Speed.FAST,
                 "3x": Speed.VERY_FAST, "4x": Speed.SUPER_FAST}
SPEED_NAME = {int(v): k for k, v in SPEED_BY_NAME.items()}


@dataclass(frozen=True)
class SpeedSpan:
    """Player speed applies from level time ``start_s`` (inclusive)."""

    start_s: float
    speed: Speed

    def __post_init__(self) -> None:
        object.__setattr__(self, "speed", Speed(int(self.speed)))


@dataclass
class Timeline:
    """Beat grid + speed plan -> x positions."""

    beat_s: float
    bar_s: float
    first_beat_s: float            # level time of beat 0 (>= 0, < beat_s)
    spans: list[SpeedSpan] = field(default_factory=list)
    beats_per_bar: int = 4

    def __post_init__(self) -> None:
        self.spans = sorted(self.spans, key=lambda s: s.start_s)
        if not self.spans or self.spans[0].start_s > 0.0:
            self.spans.insert(0, SpeedSpan(0.0, Speed.NORMAL))
        for a, b in zip(self.spans, self.spans[1:]):
            if b.start_s <= a.start_s:
                raise ValueError("speed spans must be strictly increasing")

    # -- speed -----------------------------------------------------------
    def speed_at(self, t: float) -> Speed:
        sp = self.spans[0].speed
        for span in self.spans:
            if span.start_s <= t + 1e-12:
                sp = span.speed
            else:
                break
        return sp

    def units_at(self, t: float) -> float:
        return SPEED_UNITS_PER_SECOND[int(self.speed_at(t))]

    # -- time <-> x ------------------------------------------------------
    def x_at_time(self, t: float) -> float:
        """Distance travelled by level time ``t`` (x = 0 at t = 0)."""
        if t <= 0.0:
            return 0.0
        x = 0.0
        cur = 0.0
        for span in self.spans:
            if span.start_s >= t:
                break
            x += SPEED_UNITS_PER_SECOND[int(self.speed_at(cur))] * (
                span.start_s - cur)
            cur = span.start_s
        x += SPEED_UNITS_PER_SECOND[int(self.speed_at(cur))] * (t - cur)
        return x

    def time_at_x(self, x: float) -> float:
        """Inverse of :meth:`x_at_time` (analytic, piecewise linear)."""
        if x <= 0.0:
            return 0.0
        travelled = 0.0
        cur = 0.0
        for span in self.spans:
            v = SPEED_UNITS_PER_SECOND[int(self.speed_at(cur))]
            if span.start_s > cur:
                seg = v * (span.start_s - cur)
                if travelled + seg >= x:
                    return cur + (x - travelled) / v
                travelled += seg
                cur = span.start_s
        v = SPEED_UNITS_PER_SECOND[int(self.speed_at(cur))]
        return cur + (x - travelled) / v

    # -- beats / bars ----------------------------------------------------
    def time_at_beat(self, beat: float) -> float:
        return self.first_beat_s + beat * self.beat_s

    def beat_at_time(self, t: float) -> float:
        return (t - self.first_beat_s) / self.beat_s

    def time_at_bar(self, bar: float) -> float:
        return self.first_beat_s + bar * self.bar_s

    def bar_at_time(self, t: float) -> float:
        return (t - self.first_beat_s) / self.bar_s

    def x_at_beat(self, beat: float) -> float:
        return self.x_at_time(self.time_at_beat(beat))

    def beat_at_x(self, x: float) -> float:
        return self.beat_at_time(self.time_at_x(x))

    def x_at_bar(self, bar: float) -> float:
        return self.x_at_time(self.time_at_bar(bar))

    def bar_at_x(self, x: float) -> float:
        return self.bar_at_time(self.time_at_x(x))

    # -- convenience -----------------------------------------------------
    def units_per_beat(self, t: float) -> float:
        return self.units_at(t) * self.beat_s

    def units_per_bar(self, t: float) -> float:
        return self.units_at(t) * self.bar_s

    def beat_times(self, b0: float, b1: float, step: float = 1.0) -> list[float]:
        """Level times of beats ``b0``, ``b0+step``, ... strictly below ``b1``."""
        out = []
        n = b0
        while n < b1 - 1e-9:
            out.append(self.time_at_beat(n))
            n += step
        return out

    def describe(self) -> str:
        parts = []
        for i, span in enumerate(self.spans):
            end = self.spans[i + 1].start_s if i + 1 < len(self.spans) else None
            parts.append(f"{SPEED_NAME[int(span.speed)]} from {span.start_s:.3f}s"
                         + (f" to {end:.3f}s" if end is not None else ""))
        return " | ".join(parts)
