# Architecture

```
clinecircles/
├── data/                     vendored authoritative GD tables (MIT, see data/GMDKIT_LICENSE_MIT.txt)
│   ├── object_table.csv      4000+ real object ids / classes / editor tabs
│   ├── prop_table.csv        every real object property key
│   ├── hitbox_table.csv      per-object hitbox sizes
│   ├── level_table.csv       .gmd level header keys
│   └── music/nine_circles.json   derived (not copyrighted) arrangement data
├── src/clinecircles/
│   ├── gamedata.py           verified ids: Obj, Prop, ColorChannel, Easing, Speed, GameMode
│   ├── physics.py            GD physics constants with VERIFIED/ESTIMATED markers
│   ├── model.py              Color, LevelObject, number formatting
│   ├── level.py              Level container (header, colours, objects, group alloc)
│   ├── serialization.py      level string <-> Level, .gmd plist writer/parser
│   ├── music.py              TrackProfile + Timeline (bars <-> x via speed plan)
│   ├── triggers.py           TriggerSet: every verified trigger type
│   ├── shaders.py            ShaderSet: GD 2.2 GPU shader triggers
│   ├── layout/               Phase A - gameplay
│   │   ├── primitives.py     Builder: blocks, floors, corridors, portals, cell dedupe
│   │   ├── patterns.py       safety-margined gameplay patterns
│   │   ├── sections.py       the 9-section CLINE CIRCLES plan
│   │   └── build.py          orchestrator -> BuildResult
│   ├── decoration/           Phase C - art
│   │   ├── palette.py        6 evolving colour identities, 15 custom channels
│   │   ├── shapes.py         eyes, teeth, maws, spirals, lattices, glitch strips
│   │   ├── robot.py          the CLINE mascot (built from real GD objects)
│   │   └── decorate.py       per-section decoration + colour script
│   ├── effects.py            Phase D/E - transitions, boss, endscreen
│   ├── optimize.py           Phase F - conservative performance pass
│   ├── validate.py           checks output against the real GD tables
│   └── __main__.py           CLI
├── tools/
│   ├── analyze_track.py      offline music analysis (tempo, drops)
│   └── crosscheck_gmdkit.py  independent validation via gmdkit
├── tests/test_core.py
└── out/                      generated artifacts (gitignored)
```

## Data flow

```
nine_circles.json ──► TrackProfile ──► Timeline ─┐
                                                 │ (bars -> x, speed-aware)
sections.py ──► Builder ──► Level.objects ◄──────┘
                              │
        decoration/ ──────────┤  (objects + groups + colour triggers)
        triggers.py ──────────┤
        shaders.py ───────────┤
        effects.py ───────────┘
                              │
                       optimize.py
                              │
                       validate.py  ──► Report
                              │
                    serialization.py ──► "CLINE CIRCLES.gmd"  (+ .levelstring.txt)
```

## Key design decisions

**Bars, not pixels.** Every gameplay and decoration placement is expressed in
musical bars and converted to x through `Timeline`, which integrates the speed
plan. Moving a section means changing one number.

**Safety margins over precision.** The physics constants carry explicit
confidence markers. Patterns leave ≥ 4 blocks of clearance in flight corridors
and ≥ 1.5 blocks on cube jumps, so a 20% error in the estimated gravity cannot
make a section impossible.

**Groups everywhere.** Objects are tagged with group ids at creation, so
triggers can move/rotate/fade whole structures without re-scanning the level.

**Verification is a first-class component.** `validate.py` re-checks every
object id and property key against the vendored tables, and
`tools/crosscheck_gmdkit.py` reparses the output with a completely independent
library (gmdkit). Both run on every build.

## Determinism

The generator is fully deterministic: decoration "randomness" comes from an
explicit LCG with fixed seeds, so rebuilding produces byte-identical output
(verified by rebuilding and comparing the level string).
