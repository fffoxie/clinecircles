"""Orchestrator: music map + sections + deco + effects -> a real Level."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..level import Level
from ..songmap import SongMap, load_song
from ..timeline import Timeline
from . import palette as PAL
from .builder import BLOCK, Builder
from .patterns import SecCtx
from .sections import SECTIONS

LEVEL_NAME = "THE FLAMES OF FATE"
CREATOR = "Cline"
DESCRIPTION = ("An AI-assisted Geometry Dash experiment. Medium Demon. "
               "Made for research purposes only - please do not rate.")


@dataclass
class BuildResult:
    level: Level
    builder: Builder
    song: SongMap
    timeline: Timeline
    section_x: dict[str, tuple[float, float]] = field(default_factory=dict)
    stats: dict[str, object] = field(default_factory=dict)

    @property
    def length_units(self) -> float:
        return self.timeline.x_at_time(
            self.song.time_at_bar(self.song.sections[-1].end_bar))

    @property
    def length_blocks(self) -> float:
        return self.length_units / BLOCK


def build_level(song: SongMap | None = None, *, deco: bool = True,
                effects: bool = True) -> BuildResult:
    song = song or load_song()
    tl = song.timeline()

    level = Level(name=LEVEL_NAME, description=DESCRIPTION, creator=CREATOR,
                  song_id=song.song_id, song_offset=song.start_s,
                  speed=song.sections[0].speed,
                  game_mode=song.sections[0].mode)
    PAL.apply_initial(level)

    b = Builder(level)
    section_x: dict[str, tuple[float, float]] = {}
    for spec in song.sections:
        x0, x1 = song.section_x_range(tl, spec.name)
        t0, t1 = song.section_time_range(spec.name)
        section_x[spec.name] = (x0, x1)
        ctx = SecCtx(b=b, song=song, tl=tl, spec=spec, x0=x0, x1=x1, t0=t0,
                     t1=t1)
        SECTIONS[spec.name](ctx)

    b.mark("start", 0.0)
    b.mark("end", song.length_units(tl))

    res = BuildResult(level=level, builder=b, song=song, timeline=tl,
                      section_x=section_x)
    res.stats["gameplay_objects"] = len(level.objects)

    if deco:
        from .deco import decorate
        res.stats["decoration"] = decorate(res)
    if effects:
        from .effects import apply_effects
        res.stats["effects"] = apply_effects(res)
    res.stats["objects"] = len(level.objects)
    return res
