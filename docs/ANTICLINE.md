# ANTICLINE CIRCLES

1990s-CGI Geometry Dash level. Deliverable: `out/v4/Anticline Circles.gdlvl`.

## Build

```
python3 -m clinecircles anticline --version v4
```

Writes, into `out/v4/`:

| file | purpose |
|---|---|
| `Anticline Circles.gdlvl` | **the deliverable** - Base64(Gzip(XML)) |
| `Anticline Circles.gmd` | same level in the GDShare container, for cross-checking |
| `Anticline Circles.levelstring.txt` | the plaintext inner level string |

## The .gdlvl container

Outer representation is the **whole plist XML**, gzip-compressed, then
Base64-encoded:

```
encode: xml -> utf-8 bytes -> gzip -> base64 -> .gdlvl
 decode: base64 -> gunzip -> xml
```

This is the opposite emphasis to `.gmd`, which leaves the XML in the clear and
compresses only the inner `k4` level string. Both are implemented in
`src/clinecircles/serialization.py` (`build_gdlvl` / `parse_gdlvl` vs
`build_gmd` / `parse_gmd`).

The inner `k4` level string follows the documented format: a start-config
block of `key,value` pairs, then `;`, then objects (`1,id,2,x,3,y,...`) each
terminated by `;`. See `docs/VERIFICATION.md`.

## Content

- 15,732 objects, 704 blocks, ~61 s at the current tempo grid
- all eight modes: cube, ship, ball, UFO, wave, robot, spider, swing
- palette: chrome, chrome-dark, luminous grid, monster purple, teeth white,
magenta accent, cyan glow, near-black sky

### Decoration system (`src/clinecircles/anticline_deco.py`)

Built with real maths rather than eyeballed placement:

- `wire_box()` - isometric wireframe box: 8 projected corners, 12 rods, edges
  drawn along the projected vectors
- `grid_hall()` - receding luminous grid of risers and rails
- `chrome_tower()` - alternating lit/shadowed bevelled blocks
- `machinery()` - gear + bolted industrial blocks + chain run
- `monster()` - clubstep face: skull disc, two oversized ringed eyes with
  pupils, brow ridges, a row of jagged teeth, and a ring of silhouette shards
  placed on a semicircle
- `teeth_maw()` - ring of teeth with a configurable opening so gameplay can
  pass through it
- `radial_fan()` - polar line fan (the Aperture look)
- `rotating_ring()` - ring of gears for rotate triggers
- `_line()` - any straight edge, built from rods placed along a vector at fixed
  spacing (path-following decoration)

### Trigger spine

`_spine()` lays one pulse trigger **per beat** in a dead-straight row at a fixed
y below the play area - the structure every high-end reference level uses (see
`docs/LEVEL_REFERENCES.md`).

## Honest limitations

1. **Song sync is not for Flames of Fate.** Newgrounds, GDBrowser and the GD
   song API are all blocked from this sandbox, so the audio could not be
   downloaded or analysed. The beat grid inherited from the previous build
   (174 BPM from *Nine Circles*) is still in use, so the sync does **not** match
   Flames of Fate yet. Replacing `data/music/nine_circles.json` with an
   analysis of the real track is the fix; `tools/analyze_track.py` does that
   work automatically once the audio is available.
2. **Song id is unverified.** `SONG_ID_FLAMES_OF_FATE = 1377561` is a single
   constant in `src/clinecircles/__main__.py` and is flagged there. It could
   not be confirmed here. Setting `k45` cannot embed audio.
3. **Not tested in Geometry Dash.** No GD client is available. The file is
   validated structurally, round-trips through this project's own decoder, and
   its `.gmd` twin parses identically in gmdkit (an independent library). That
   is not the same as a successful in-game import.
4. **Decoration is sparse relative to the references.** 15.7k objects against
   Triple Six's 194k. The systems are in place but the density is not there yet.
