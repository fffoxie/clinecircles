# How to playtest the layouts

## What to play

`out/v3/CLINE CIRCLES.gmd` is the current **layout-only** build (no decoration).
Each version folder is a frozen snapshot; a new version never overwrites an old
one.

| version | what changed |
|---|---|
| `out/v1/` | first layout, built on the wrong assumption that the level needs its own floor. Superseded. |
| `out/v2/` | floor removed (the engine supplies ground); flight corridors no longer place a floor under the player. Superseded. |
| `out/v3/` | **current** — portals moved to the player's height (they were 450 units too high, so no mode or speed ever changed), speed portals added at every speed change, section extraction fixed. |

Each folder has:

```
CLINE CIRCLES.gmd            the level (import this)
CLINE CIRCLES.levelstring.txt  same level as a plaintext level string
level_info.json              object count, timing, validation result
screenshots/                 frames captured while autopilot played it
section_playtest.json        per-section autopilot results (v2/v3)
```

## Playing it in Geometry Dash

1. Install **Geode** and the **GDShare** mod.
2. **Create -> GDShare -> Import** and choose `out/v3/CLINE CIRCLES.gmd`.
3. Open it in the editor and press play.
4. Song: Newgrounds id **533927** (*Nine Circles*).

## Playing it in Web Dashers (no install)

`tools/wd_setup.sh` prepares a headless browser, then:

```
python3 tools/wd_lab.py --version v3 --all --seconds 12 --shots
python3 tools/wd_lab.py --version v3 --section intro --seconds 25 --shots
```

`--shots` writes frames to `out/<version>/screenshots/`. Section extraction
builds a standalone mini-level containing just that section, shifted to x=0, so
the player starts inside it (the game re-clamps the camera, so teleporting does
not persist).

## What to look for

- Can you clear the intro cube section without dying?
- Do the ship / UFO / wave / robot / spider corridors feel fair, and is the
  opening big enough to read?
- Does each mode change happen where the music changes?
- Anything that kills you with no warning.

## Known limitations of the test engine

- **Web Dashers does not implement Swing**, so that section can only be checked
  structurally.
- Its physics are **not** Geometry Dash's, and it is frame-rate dependent, so
  jump distances measured there do not transfer directly.
- Its speed values are per frame, so the autopilot's timings are approximate.

## The object catalogue

`data/objects.json` documents all **4082** editor objects:

- official name, GD class, editor tab and position
- **engine behaviour** (solid / soliddeco / hazard / portal / trigger / pad /
  ring / speed / deco / particle / pixel / coin)
- grid size, sprite, whether it can be coloured
- real hitbox size in units where known
- a written description of what it does and how it works
- 37 hand-written entries for the objects this project uses
- 33 entries with first-hand test results from Web Dashers

Each tested entry carries a `confidence` field: portal results are
**verified** (read from the engine's own state flags), while collision results
are marked **LOW** because the player-world-x to object-level-x frame could not
be confirmed in the test engine.

Rebuild it with:

```
node /tmp/wd/dump.js && python3 tools/build_object_catalog.py
python3 tools/wd_object_test.py --seconds 3   # re-run the object tests
```
