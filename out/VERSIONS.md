# CLINE CIRCLES - build versions

Layout is being built first; decoration comes later.

## v3 (current)
- Portals and orbs moved to the player's height. They were being passed in
  units where the builder expected blocks, so every portal sat 450 units too
  high and **no game mode or speed ever changed in game**.
- Speed portals added at every speed change (bar 12 -> 2x, 20 -> 1x,
  27 -> 2x, 40 -> 1x). Without them the timeline's section positions were
  fiction.
- Section extraction fixed: it was mutating the shared level objects, so every
  section after the first was tested against corrupted data.
- 655 objects, layout only.

## v2
- Removed the ground-level block rows. Playtesting showed a continuous row of
  y=15 blocks kills the player at x~21: the engine already supplies the ground,
  so those blocks are a wall, not a floor.
- Flight corridors no longer place a solid floor below the player.

## v1
- First full layout: 1021 objects, all 8 modes, synced to the verified music
  grid. Built on the wrong floor assumption - superseded by v2.
