"""Assemble the level: timeline + sections -> a real :class:`Level`."""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import gamedata as gd
from ..level import Level
from ..music import Section, SpeedSegment, Timeline, TrackProfile, load_track
from . import sections as S
from .primitives import BLOCK, Builder

END_BAR = 44.0  # verified: bar 44 = 60.777 s in the analysed arrangement


@dataclass
class BuildResult:
    level: Level
    builder: Builder
    timeline: Timeline
    track: TrackProfile
    section_x: dict[str, tuple[float, float]] = field(default_factory=dict)

    @property
    def length_units(self) -> float:
        return self.timeline.x_at_bar(END_BAR)

    @property
    def length_blocks(self) -> float:
        return self.length_units / BLOCK


def make_timeline(track: TrackProfile, sections: list[S.SectionSpec]) -> Timeline:
    segs: list[SpeedSegment] = []
    for sec in sections:
        if not segs or segs[-1].speed != sec.speed:
            segs.append(SpeedSegment(sec.start_bar, sec.speed))
    if not segs or segs[0].start_bar != 0:
        segs.insert(0, SpeedSegment(0, gd.Speed.NORMAL))
    return Timeline(track=track, segments=segs)


def build_level(track: TrackProfile | None = None,
                sections: list[S.SectionSpec] | None = None) -> BuildResult:
    track = track or load_track()
    sections = sections if sections is not None else S.SECTIONS
    tl = make_timeline(track, sections)

    level = Level(
        name="CLINE CIRCLES",
        description=("CLINE CIRCLES - an AI-assisted Geometry Dash experiment. "
                     "Made for research purposes only."),
        creator="Cline",
        song_id=track.song_id,
        speed=sections[0].speed,
        game_mode=sections[0].mode,
    )

    builder = Builder(level)
    section_x: dict[str, tuple[float, float]] = {}

    for sec in sections:
        x0 = tl.x_at_bar(sec.start_bar)
        x1 = tl.x_at_bar(sec.end_bar)
        section_x[sec.name] = (x0, x1)
        ctx = S.Ctx(build=builder, x0=x0, x1=x1, speed=sec.speed, mode=sec.mode)
        sec.build(ctx, tl, sec.start_bar)

    builder.mark("start", 0.0)
    builder.mark("end", tl.x_at_bar(END_BAR))
    for name, (x0, _) in section_x.items():
        builder.mark(name, x0)

    return BuildResult(level=level, builder=builder, timeline=tl, track=track,
                       section_x=section_x)
