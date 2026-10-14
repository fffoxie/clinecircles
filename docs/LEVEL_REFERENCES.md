# What the reference levels teach

`rflevels/` holds 15 real `.gmd` levels, from bare layouts to full decoration
to 3D-effect showcases. They are **references, not assets** - the goal is to
learn the techniques, not to copy the geometry.

The browser test engine does not implement every GD object, so these cannot be
played there. `tools/gd_visualize.py` renders them from the game's own sprite
atlases instead, so the structure can actually be seen.

```
python3 tools/gd_visualize.py "rflevels/Layout.gmd" --out out/refs/Layout.png
python3 tools/gd_visualize.py "rflevels/Realistic deco.gmd" --pxu 2.2
python3 tools/gd_visualize.py "rflevels/3Depth.gmd" --strip --pxu 0.5
```

Renders land in `out/refs/`. The tool merges the game's object table with the
engine's sprite definitions and a global frame index across the
`GJ_GameSheet*` atlases, so it draws real sprites with real colours, scale,
rotation and flips.

## Inventory of the references

| file | objects | width | what it is |
|---|---|---|---|
| `Layout.gmd` | 1 667 | 850 blocks | pure gameplay layout |
| `Aci.gmd` | 433 | 202 blocks | small gameplay snippet |
| `Nine Circles.gmd` | 14 894 | 1 154 blocks | a full classic level |
| `Realistic deco.gmd` | 1 167 | 29 blocks | decoration close-up |
| `effect layout .gmd` | 15 027 | 846 blocks | effect/trigger study |
| `3Depth.gmd` | 31 954 | 5 000 blocks | 3D technique showcase |
| `WANNACRY.gmd` | - | - | large deco level |
| `Artemis 13.gmd` | - | - | large deco level |
| `Triple Six.gmd` | - | - | 2.7 MB, very heavy |
| `Aperture.gmd`, `Eta Carnis.gmd`, `Blackfire Backfire.gmd`, `Wanna Talk About It.gmd`, `8 second snippet.gmd` | - | - | small snippets |

## Technique 1 - layout: the spike corridor

`Layout.gmd` shows the standard way to build a tunnel: rows of **spikes rotated
45 degrees**, interleaved to form a zigzag, with a gap left down the middle for
the player. A long block ceiling and floor then form the corridor proper. Note
how the corridor's own floor sits well above the engine ground, and portals are
placed in the open space between corridors - never inside the geometry.

## Technique 2 - "realistic" decoration

`Realistic deco.gmd` (rendered at 2.2 px/unit in
`out/refs/Realistic_deco_zoom.png`) is a textbook example. Every cluster is
built in layers, back to front:

1. **dark backing rectangles** - create shadow and separate the cluster from
   the background
2. **main blocks** - 3D-shaded rectangular blocks, in small overlapping groups,
   never a flat grid
3. **rotated thin beams** - long narrow rectangles at angles, crossing the
   cluster like struts; this is what stops it looking like a wall of cubes
4. **edge shards** - small spiky rock sprites run along the *outer edge* of
   every cluster; this is the single most recognisable part of the style
5. **glow anchors** - ringed circles (green, orange) placed at the ends of
   beams to anchor the composition
6. **sparkle** - a handful of tiny coloured dots and arrows, deliberately
   sparse

The takeaway is not the style but the *method*: back layer, mass, structure,
edge treatment, accents - in that order, and always in clusters with empty
space between them.

## Technique 3 - faking 3D

`3Depth.gmd` (see `out/refs/3Depth_core.png`) is built almost entirely from
**wireframe boxes**: thin rectangles rotated to form the edges of a box drawn
in perspective. Chain several boxes at different scales and offsets and the eye
reads depth. Other things visible in it:

* a large flat scaled rectangle used as a void/screen
* dotted lines made from long runs of small circle sprites
* text objects used as on-canvas annotations
* literal colour-palette swatches placed in the level as a reference

For CLINE CIRCLES this is directly useful: the dive-through-the-pupil, world-rotate and collapse-to-a-point transitions can be built from rotated wireframe geometry rather than only from shader triggers.
