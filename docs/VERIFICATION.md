# Technical Verification — CLINE CIRCLES

This document records what was **verified from authoritative sources** before any
implementation decisions were made. It separates verified facts, reasonable
assumptions, and open questions.

Sources used (all inspectable):

- `boomlings.dev` / `gd-programming/gd.docs` — community documentation,
  generated from the game's own object/property data.
- `UHDanke/gmdkit` (MIT) — a working Python toolkit that reads and writes real
  `.gmd` files. Its data tables are derived from the game binary and are copied
  into `data/` with attribution (`data/GMDKIT_LICENSE_MIT.txt`).
- Real official level files shipped inside gmdkit
  (`data/gmd/official/*.gmd`), decoded during verification.

---

## 1. How Geometry Dash levels are actually stored

**VERIFIED.** A Geometry Dash level has two layers:

### 1a. The inner *level string* (the playable data)

Plaintext, human-readable, composed of:

1. A **header** of `key,value` pairs separated by `,`. Real example decoded from
   the bundled official level *Stereo Madness*:

   ```
   kS29,1_40_2_62_3_255_...,kS30,...,kA13,0,kA15,0,kA16,0,kA14,,kA6,0,...,kA11,0
   ```

   Colour channels are `kS29`..`kS39`-style keys whose value is
   `1_<r>_2_<g>_3_<b>_4_<player>_6_.._7_.._11_.._12_.._13_.._14_.._15_.._18_..`
   (`_`-separated sub key/value pairs). Audio is `kA13,kA14,...`.

2. A **`;` separator**, then the **object string**.

3. The **object string**: objects separated by `;`, properties separated by `,`,
   encoded as `propId,value,propId,value,...`. Verified real object:

   ```
   1,29,2,135,3,135,7,...
   ```

   → object id `29` at x `135`, y `135`, plus further properties.

### 1b. The *`.gmd` container* (the file you import into GD)

**VERIFIED** by inspecting `data/gmd/official/*.gmd` and `gmdkit/defaults/level.py`.

A `.gmd` file is an **XML plist**:

```xml
<?xml version='1.0' encoding='us-ascii'?>
<plist version="1.0" gjver="2.0"><dict>
  <k>kCEK</k><i>4</i>
  <k>k2</k><s>LEVEL NAME</s>
  <k>k4</k><s>H4sIAAAA...BASE64...</s>       <!-- compressed level string -->
  <k>k13</k><t />                             <!-- editable -->
  <k>k21</k><i>2</i>                          <!-- level type: local -->
  <k>k16</k><i>1</i>                          <!-- version -->
  <k>k50</k><i>45</i>                         <!-- binary version -->
</dict></plist>
```

- `kCEK = 4` is the encoder key.
- `k4` holds the **level string compressed with gzip and base64-URL-safe
  encoded** (this is the only value that is compressed; the other keys are
  plain).
- Level header keys are documented in `data/level_table.csv`
  (`k1` id, `k2` name, `k3` description (base64), `k4` object string, `k5`
  creator, `k13` editable, `k16` version, `k18` attempts, `k21` level type,
  `k23` length, `k25` demon flag, `k45` song id, `k48` object count, `k50`
  binary version…).

### 1c. Compression

**VERIFIED** (`docs/topics/levelstring_encoding_decoding.md`):

- encode: `base64.urlsafe_b64encode(gzip.compress(level_string.encode()))`

---

## 2. Can a generated level actually be loaded by Geometry Dash?

**VERIFIED (approach) / NEEDS FIELD TEST (end-to-end).**

The `.gmd` format is the interchange format of the **GDShare** mod (by HJfod,
available on **Geode**, the 2.2 mod loader). GDShare supports *Import* and
*Export* of levels as `.gmd`. Therefore:

> `clinecircles` generates a `.gmd` -> the user imports it via GDShare -> the
> level appears in the GD editor as a real, editable, playable level.

This is the **primary, verified delivery path**. The generated `.gmd` also
contains the plaintext object string, so the level can additionally be pasted
via any level-string importer.

**Not claimed:** uploading to the GD servers, official rating, or that the exact
byte layout is accepted by every GD build. `k50` (binary version) is set to a
2.2-era value; this must be confirmed on a real client.

---

## 3. What can realistically be generated?

**VERIFIED** from the object table (`data/object_table.csv`, 4000+ ids) and
property table (`data/prop_table.csv`):

| Capability | Verified object id(s) |
|---|---|
| Cube / Ship / Ball / UFO / Wave / Robot / Spider portals | 12 / 13 / 47 / 111 / 660 / 745 / 1331 |
| Gravity portals (blue/yellow) | 10 / 11 |
| Size portals, mirror, dual, teleport | 99,101 / 45,46 / 286,287 / 747 |
| Speed portals (slow->super-fast) | 200,201,202,203,1334 |
| Jump pads / orbs (all colours), dash orbs | 35,67,140,1332 / 36,84,141,1022,1333,1330,1594 / 1704,1751 |
| Blocks, spikes, hazards | ids 1.., 8, spike family (30x30 / 60x60 hitboxes) |
| **Triggers**: colour 899, move 901, pulse 1006, alpha 1007, toggle 1049, spawn 1268, rotate 1346, follow 1347, shake 1520, animate 1585, touch 1595, count 1611, stop 1616, on-death 1812, follow-player-y 1814, collision 1815, collision block 1816, pickup 1817, bg effect 1818/1819, random 1912, zoom 1913, static camera 1914, offset camera 1916 |
| Camera control | zoom 1913, static 1914, offset 1916, camera guide/mode props in `prop_table` |

So: **all seven game modes, speed changes, portals, orbs, pads, and the full
2.2 trigger suite incl. camera and keyframe/advanced effects are generatable.**

### Effects / "shaders"

**VERIFIED:** GD 2.2 added *shader* and advanced *effect* objects; their
properties exist in `prop_table.csv` (`trigger.shader.*`, `trigger.effect.*`,
`trigger.enter_preset.*`, `trigger.keyframe.*`). There is **no user-authored
GLSL** — effects are parameterized objects. 3D illusions must be built from 2D
objects (layering, scale, rotation, move triggers), which is what mainstream
demon creators do.

### Things GD does **not** let us do (VERIFIED limits)

- Custom end-screen *UI* is not authorable per level; the "level complete"
  screen is engine UI. We emulate an endscreen with in-level objects + triggers
  in the final seconds. **Documented limitation.**
- No procedural textures; sprites come from fixed sprite sheets (object ids).
- Physics is fixed by the engine; we cannot change gravity constants, only use
  portals/pads/orbs.

---

## 4. Validation strategy

1. **Unit + round-trip tests** in Python.
2. **Independent round-trip validation with `gmdkit`** (dev dependency): parse
   our `.gmd` with a *different* implementation and assert fields/objects match.
   This is the strongest available evidence short of opening the game.
3. **Structural validators**: every object id exists in `object_table.csv`;
   every property id is valid for that object; no gameplay object overlaps a
   hazard; every object sits on a reachable path (layout checks).
4. **Level-string size / object-count checks** (GD caps objects; we check `k48`).

---

## 5. Open questions (need a real client to close)

- Exact `k50`/`k17` binary/game-version values a 2.2 client expects on import.
- Whether GDShare's importer validates `k48` (object count) strictly.
- Real in-game frame rate of the finished level (cannot be measured here).
- Newgrounds song approval cannot be verified from this sandbox.

- decode: `zlib.decompress(base64.urlsafe_b64decode(s), 15 | 32)`

Official levels additionally strip the first 13 base64 chars
(`H4sIAAAAAAAAA`), which is irrelevant for custom-level export.

---

## 6. Shaders - a capability discovered after the first pass

**VERIFIED (upgraded finding).** The first survey under-sold what GD 2.2 can
do. `data/object_table.csv` contains a whole `ShaderGameObject` family
(editor tab 13), i.e. **real GPU post-processing triggers**:

| Shader | id | Shader | id |
|---|---|---|---|
| Shader options | 2904 | Pixelate | 2912 |
| Shock wave | 2905 | Lens circle | 2913 |
| Shock line | 2907 | Radial blur | 2914 |
| Glitch | 2909 | Motion blur | 2915 |
| Chromatic aberration | 2910 | Bulge | 2916 |
| Chromatic glitch | 2911 | Pinch | 2917 |
| Grayscale / Sepia | 2919 / 2920 | Invert / Hue | 2921 / 2922 |
| Edit colour | 2923 | Split screen | 2924 |

Their properties are fully documented in `data/prop_table.csv`
(`trigger.shader.*`), including strength (176), speed (175), size (179/512),
centre group (51), tint channel (71) and fade time (10).

**Consequence:** the level can use genuine screen-space distortion -
`pinch`/`bulge`/`lens_circle`/`radial_blur` create real perspective warping,
and `glitch`/`chromatic_glitch`/`pixelate` create real digital artefacts. The
"3D transitions" are therefore not purely fake 2.5D: they combine 2D object
choreography with real post-processing.

**Text is also available** (object id 914, `TextGameObject`), with the string
stored base64-encoded in property 31. This is what makes a real in-level
endscreen possible (see `effects.endscreen`).

## 7. The hard limit that remains

GD levels cannot contain **custom textures or sprites**. The Cline mascot is
therefore composed from existing GD objects (circles, rods, blocks) and is an
original interpretation, not a reproduction of any supplied logo. This is
documented in `src/clinecircles/decoration/robot.py`.
