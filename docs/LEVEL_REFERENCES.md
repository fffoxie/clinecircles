# Reference study: how these Geometry Dash levels are built

`rflevels/` holds the source levels; `urfimages/images/` holds 65 screenshots of
13 more. Neither is an asset to copy — they are there to learn technique from.

Everything below was read off renders produced by `tools/gd_visualize.py`, which
draws a `.gmd` using the game's own sprite atlases. Full contact sheets and
detail zooms for every level are in `out/refs/<level>/`.

---

## 0. What is actually in the folder

Not every `.gmd` contains a level. **`Aperture`, `Eta Carnis`, `Blackfire
Backfire`, `Wanna Talk About It` and `8 second snippet` are metadata stubs**:
they carry the level's name, id, creator and stats, but **no `k4` object
string**. They were exported as "level info" rather than as a level. Their
screenshots in `urfimages/` are still useful — only the source data is missing.

| level | objects | width | role |
|---|---|---|---|
| `Layout.gmd` | 1 667 | 850 blocks | pure gameplay layout |
| `Aci.gmd` | 433 | 202 blocks | small layout snippet |
| `Nine Circles.gmd` | 14 894 | 1 154 blocks | full classic level |
| `Realistic deco.gmd` | 1 167 | 29 blocks | decoration close-up |
| `effect layout .gmd` | 15 027 | 846 blocks | trigger/effect study |
| `3Depth.gmd` | 31 954 | 5 000 blocks | 3D technique showcase |
| `Artemis 13.gmd` | 51 879 | — | heavy decorated level |
| `WANNACRY.gmd` | 69 997 | — | heavy decorated level |
| `find the answer.gmd` | 89 650 | — | heavy decorated level |
| `Triple Six.gmd` | 194 190 | — | massive collab level |

The object counts are the first lesson: a serious decorated level is
**10k–200k objects**. A layout is 1–2k. Decoration is roughly 50–100x the
layout cost.

---

## 1. The trigger spine

Triple Six's contact sheet shows the single most important structural fact
about a well-made level: hundreds of **colour, pulse and move triggers laid out
in long horizontal rows**, usually hugging the ground line or hidden below the
play area.

In the render they appear as small labelled sprites (`Pulse`, `Color`, `Move`,
`Col 1`, `Col 3`) marching in a dead-straight line across the whole width.

Why it matters:

* every effect is fired by a trigger at one specific x, so the visual language
  of the level is *indexed to distance* — which is the same thing as time;
* straight rows keep the level editor-readable: you can see at a glance which
  beat a trigger belongs to;
* the rows sit at one fixed y, which makes them trivially copy-pasteable.

**The arithmetic.** Given BPM `b` and speed `v` (units/second), one beat lasts
`60/b` seconds, so one beat is `v * 60 / b` units of x. At 174 BPM:

| speed | units/s | units per beat | units per 4/4 bar |
|---|---|---|---|
| 1x | 311.58 | 107.4 | 429.6 |
| 2x | 387.42 | 133.6 | 534.2 |
| 3x | 468.00 | 161.4 | 645.5 |

A trigger every beat is a trigger every 107.4 units at 1x. That is the
arithmetic behind those straight rows.


---

## 2. Layout: how the playable part is built

From `Layout.gmd` and `Aci.gmd`:

**Spike corridors.** A tunnel is built from rows of spikes **rotated 45
degrees**, staggered so the tips interlock into a zigzag, with a gap left down
the middle. The spikes point inward from a block ceiling and a block floor.

**Corridors, not floors.** The solid floor sits *well above* the engine ground.
The engine ground carries the player; the level's own geometry is a tunnel
around the flight path. This matches what our own playtest found the hard way:
a continuous block row at ground level is a wall.

**Portals live in the open.** Every portal sits in empty space between two
pieces of geometry, never inside a corridor pinch. In the Layout render the
ship portal, the speed portals and the orbs all float in the clear gap between
the spike corridor and the block tunnel.

**Density is deliberate.** Layouts alternate tight clusters with long empty
runs. The empty runs are not laziness — they are where the player recovers and
where decoration will later breathe.

---

## 3. Decoration: the layered method

`Realistic deco.gmd` at 2.2 px/unit is the clearest teaching example. Every
cluster is built back-to-front in six passes:

1. **dark backing rectangles** — establish shadow and separate the cluster from
   the background;
2. **main block mass** — 3D-shaded blocks in small overlapping groups, never a
   flat grid;
3. **rotated thin beams** — long narrow rectangles crossing the cluster like
   structural struts; this is what stops it reading as a wall of cubes;
4. **edge shards** — small spiky rock sprites run along the *outer edge* of
   each cluster (the most recognisable part of the style);
5. **glow anchors** — ringed circles placed at the ends of beams;
6. **sparkle** — a handful of tiny coloured dots and arrows, deliberately
   sparse.

The transferable rule is not the style, it is the **order** and the
**clustering**: back layer, mass, structure, edge treatment, accent — repeated
in clumps with genuine empty space between them, never a uniform field.

---

## 4. Faking 3D

`3Depth.gmd` is built almost entirely from **wireframe boxes**: thin rectangles
rotated to draw the edges of a box in perspective. Chain boxes at different
scales and offsets and the eye reads depth. Also visible:

* a large flat scaled rectangle used as a void or screen;
* dotted lines made from long runs of small circle sprites;
* text objects used as on-canvas annotations;
* literal colour-palette swatches parked in the level as a working reference.

### The maths

Isometric projection of a 3D point (X, Y, Z) onto 2D:

```
sx = X + Z * cos(30deg)
sy = Y + Z * sin(30deg)
```

A box is eight projected corners and twelve edges. Each edge is one narrow
rectangle sprite placed at the midpoint, rotated by `atan2(dy, dx)`, with length
`hypot(dx, dy)` and a thin scale on the other axis. That is the whole trick.

For **true perspective** (the Aperture look), project with focal length `f`:

```
sx = f * X / (Z + f)
sy = f * Y / (Z + f)
```

and drive `Z` with a move trigger to fly the camera through the structure.


---

## 5. Radial and polar composition (Aperture)

`urfimages/images/Aperture/` shows a level built on **rotational symmetry**:
four identical beam structures rotated 90 degrees apart around a white central
iris, with a fan of thin lines radiating outward and a light bloom behind.

Build it with polar maths. For `n` copies at radius `r`:

```
for i in range(n):
    a   = 2*pi*i/n        # angle
    x   = cx + r*cos(a)   # position
    y   = cy + r*sin(a)
    rot = degrees(a)      # each copy faces outward
```

Rotational symmetry is cheap and reads as deliberate design: author one arm,
then rotate it. A radial line fan is the same loop with the sprite replaced by
a very thin, very long rectangle of length `r`.

A **spiral** grows both at once:

```
a = k * t
r = r0 + c * t        # t from 0..1
```

A **sine ribbon** (common for wave and background decoration):

```
y = A * sin(2*pi * x / lambda)
```

dropping a sprite every few units along `x`, rotated by the local slope
`atan(A * 2*pi/lambda * cos(...))` so the ribbon looks continuous.

---

## 6. Path-following decoration

The Triple Six zoom (`out/refs/Triple Six/zoom_0.png`) shows a chain of
identical spiky burst sprites laid along a path that starts horizontal, bends to
a diagonal, then runs straight up — evenly spaced the whole way.

The technique: define a polyline or curve, walk it at a fixed arc-length step,
and drop one sprite per step, rotated to the local tangent. With a Bézier or
Catmull-Rom spline through a few control points you can draw organic vines,
tentacles and shockwaves from a single repeated sprite.

---

## 7. Colour

Every reference keeps a **small, deliberate palette** and reuses it. The
`3Depth` render even parks literal swatch grids in the level. GD colour channels
are effectively free, but a level with a fixed set of 8–15 channels, moved
between sections by triggers, will always read as one place; a level that
re-colours objects ad-hoc reads as noise.

---

## 8. What this means for CLINE CIRCLES

1. **Build a trigger spine from the beat grid.** At 174 BPM a bar is 429.6
   units at 1x and 534.2 at 2x. One row per section, fixed y, one trigger per
   beat.
2. **Rebuild the wave section as a real spike corridor** — interlocked
   45-degree spikes between a block floor and ceiling, not the current
   scattered pinches.
3. **Budget decoration at 50–100x the layout.** 655 layout objects is on track
   to 30k–60k decorated.
4. **Use polar and isometric maths for the transitions**, not only shader
   triggers — Aperture and 3Depth prove that is where the spectacle comes from.
5. **Keep decoration clustered with real gaps**, and reserve tight geometry for
   gameplay areas only.

---

## 9. Image index

- Downscaled versions of all 65 screenshots: `out/refs/urfi2/`
- Full renders of the source levels: `out/refs/<level>/contact_sheet.png` and
  `zoom_*.png`

Levels with imagery but no source data: `Aperture`, `Eta Carnis`.

Levels with imagery and no `.gmd` at all: `Ascension To Heaven`, `Black
Blizzard`, `Bloodbath`, `Collab Level`, `Peaceful`, `Tidal Wave`, `Too Kid
Friendly`, `WHAT`.
