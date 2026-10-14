# Progress

## Done

- **Verification** (`docs/VERIFICATION.md`) — level string, `.gmd` container and
  gzip/base64 encoding confirmed against real GD files; object ids, property
  keys, hitboxes and colour channels taken from the game's own tables; GD
  physics constants recorded with VERIFIED/ESTIMATED markers.
- **Music** — *Nine Circles* (NIGHTkilla/Rukkus, NG 533927) analysed from the
  actual audio: 174.00 BPM, real drops at bars 12 and 27.
- **Export pipeline** — level string + `.gmd` writer/parser, proven by
  reparsing with a completely independent library (gmdkit).
- **Phase A layout** — 9 sections, 703 blocks, ~61 s, all 8 modes, synced to
  bars. Rebuilt after playtesting (see below).
- **Phase B triggers** — 17 verified trigger types.
- **Phase C decoration** — palette from the supplied style sheet; giant eyes,
  jagged teeth/maws, spirals, impossible lattices, glitch strips; the CLINE
  mascot rebuilt to match the supplied model sheet.
- **Phase D/E effects + endscreen** — 5 transitions using real 2.2 GPU shader
  triggers (lens circle, bulge, pinch, glitch, chromatic glitch, shockwave)
  and a Text-object endscreen.
- **Phase F optimization** — cell dedupe plus a conservative post-pass.
- **Playtesting** — Web Dashers driven headlessly (`tools/wd_harness.py`,
  `tools/wd_play.py`); a real playtest finding forced a layout rebuild.

## Open

- **Later sections are unplayed.** The harness can't currently confine runs to
  a section, so only the intro was genuinely navigated.
- **Native GD test.** Never opened in the real game — the file is structurally
  valid and independently parseable, but that is not the same thing.
- **Boss interaction.** The boss animates independently; making attacks react
  to the player (collision triggers) would deepen it.
- **Decoration density.** 1951 objects is modest; the reference style is much
  richer. Safe to push once the layout is confirmed in-game.
