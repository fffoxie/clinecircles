# Playtesting report

## Environment

**Web Dashers** (https://web-dashers.github.io/) — a fan-made browser
reimplementation of Geometry Dash (Phaser 3.90, WebGL). It is *not* the
original engine, and its physics differ from GD's.

Driven headlessly with Playwright + Chromium (`tools/wd_setup.sh` prepares the
shared libraries the browser needs, which cannot be apt-installed without
root). See `tools/wd_harness.py`.

### What was verified about the interchange

Web Dashers' `parseLevel()` (assets/scripts/core/level.js) does:

```
base64url decode -> pako.inflate -> split on ';'
-> first part = settings, rest = objects
-> each object = key,value pairs with the SAME numeric keys we emit
```

That is byte-identical to this project's level-string format, so the generated
level loads **without any conversion**. Confirmed live: `start_level -> True`,
`ready -> True`, and screenshots show the cube, spikes and ground rendering
(`out/cline_*.png`).

## Findings that changed the level

### 1. A ground-level block row is lethal, not a floor

`tools/wd_probe8.py` ran four controlled levels:

| test | contents | result |
|---|---|---|
| A | continuous blocks at y=15, no hazards | **dies at x≈21** |
| B | empty level | runs freely on the engine ground |
| C | continuous y=15 blocks + one spike | **dies at x≈21** |
| D | floating blocks at y=75 | runs past, no deaths |

Geometry Dash supplies the ground itself. Blocks placed *at* ground level are
obstacles the player collides with, not a floor.

Cross-checked against RobTop's own data: `assets/levels/1.txt` (Stereo Madness)
has **no solid object at all before x=1515**, and uses y=15 for spikes and for
platforms that are only ever *landed on after a jump*.

**Change made:** the level was rebuilt to run on the engine ground, with spikes
at y=15 and all solid geometry floating above the run line (bottom ≥ y=60).
`src/clinecircles/layout/plan.py` documents this convention.

### 2. Web Dashers' physics are not GD's

`tools/wd_calibrate.py` measured the cube's jump by reading the engine's own
PlayerState:

| speed | jump height | jump length (noisy) |
|---|---|---|
| 0.5x | 3.16 blocks | 8.83 blocks |
| 1x | 3.18 blocks | 6.70 blocks |
| 2x | 3.18 blocks | 10.76 blocks |

Height is consistent (~3.17 blocks) but GD's documented height is ~2.1-2.4
blocks, and length was unstable because the headless framerate is ~10-20 fps
with stalls. **Conclusion: Web Dashers is useful for navigation and rendering
validation, not for measuring GD's exact timings.** The layout therefore keeps
its safety margins and uses GD's documented constants (`physics.py`) for
timing, not Web Dashers' numbers.

## Autopilot playtest

`tools/wd_play.py` plays the level with real SPACE input. It reads the hazard
list the generator produced and jumps when the next hazard is 2-95 units ahead
while grounded; in flight modes it steers toward the corridor centre.

Result on the intro section (bars 0-12, cube, 1x):

```
max_x = 1224   deaths = [1236, 1242]
```

The first three spike clusters sit at x = 430, 845/875 and 1289. The autopilot
clears the first two and dies at the third, repeatably.

**Interpretation (deliberately cautious):** a crude 10-20 fps bot failing at a
plain single spike is weak evidence about the difficulty of that spike. It does
show the route is traversable for the first ~1200 units with ordinary input.

## What was NOT verified

- **Later sections.** The harness can set `_playerWorldX`, but the game
  re-clamps the camera each frame, so section-restricted runs kept restarting
  from x=0. Only the intro was genuinely played.
- **Ship / UFO / wave / robot / spider / swing flight feel.** Loaded and
  rendered, but not navigated by the bot.
- **Native Geometry Dash.** Not tested at all — out of scope for this sandbox.
- **Frame rate in GD.** Not measurable here.
- **Song whitelist** for Newgrounds id 533927 — the GD API is blocked here
  (Cloudflare 403).

## Validation status by category

| category | status |
|---|---|
| Structural | **PASS** — `validate.py`: every object id and property key exists in GD's real tables; 1951 objects; 8/8 modes present |
| Independent parse | **PASS** — gmdkit reparses the `.gmd` and returns the same name, song id and object list |
| Simulator | **PASS (loads and plays)** — Web Dashers loads the file natively and renders it |
| Gameplay | **PARTIAL** — intro navigable by autopilot; later sections not exercised |
| Native compatibility | **NOT TESTED** — requires a real GD client |
