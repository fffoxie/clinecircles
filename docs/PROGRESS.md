# Progress

## Done

### Phase 0 - verification (docs/VERIFICATION.md)
- Level string, `.gmd` container and gzip/base64 encoding verified against real
  GD files shipped in gmdkit.
- Object ids, property keys, hitboxes and colour channels taken from the game's
  own tables (vendored in `data/`).
- GD physics constants recorded with explicit VERIFIED / ESTIMATED markers.
- Music: *Nine Circles* (NIGHTkilla/Rukkus, Newgrounds 533927) chosen and its
  real arrangement analysed from the audio.

### Phase A - gameplay layout
9 sections, 703.5 blocks, 60.78 s, synced to bars 0/12/20/27/40/44.
All 7 required modes plus ball:
`cube → ship → ufo → wave → ball → spider → robot → swing → cube+ship → cube`.

### Phase B - triggers
`TriggerSet` emits every verified trigger type: move, rotate, alpha, pulse,
colour, toggle, spawn, shake, zoom, offset camera, follow, stop, touch, animate,
bg-effect, count.

### Phase C - decoration
Evolving palette (6 identities, 15 custom channels), giant eyes, jagged teeth
and maws, spirals, impossible lattices, glitch strips, particle fields, and the
CLINE robot mascot with per-part animation groups.

### Phase D/E - transitions and endscreen
5 major transitions (dive-through-pupil, world rotate, collapse to point,
teeth close, boss transform) using real 2.2 GPU shader triggers, plus an
in-level endscreen built from real Text objects.

### Phase F - optimization
Cell dedupe (2164 -> 2074 objects) and a conservative post-pass that never
touches gameplay ids.

### Validation
- `validate.py`: PASS (all object ids + property keys exist in the real tables).
- `tools/crosscheck_gmdkit.py`: PASS - gmdkit independently parses the `.gmd`
  and returns the same name, song id and object list.

## Open / next

- **Gameplay tuning.** The physics constants are only partly verified; the
  layout uses generous margins but real in-game testing is required. This is
  the single highest-value next step and needs a GD client.
- **Decoration density.** 2074 objects is modest; more atmosphere is possible
  once the layout is confirmed playable.
- **Boss interaction.** The boss currently animates independently; making its
  attacks react to player position (collision triggers) would deepen it.
- **Song whitelist.** Must be confirmed in-game (the GD API is blocked here).
