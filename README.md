# ANTICLINE CIRCLES

An unofficial, AI-assisted **Geometry Dash level generator** that produces a
real, importable `.gmd` level file — not a browser imitation.

> Made for research purposes only. Do not rate this level.

## What this is

- A **level generator/serializer** that writes genuine Geometry Dash level data
  (`.gmd` / GDShare format), verified against the real format.
- A **phased build pipeline**: gameplay layout → triggers → decoration →
  advanced effects → endscreen → optimization.
- A **validator** that round-trips the output through an independent library.

## Delivery workflow

```
python -m clinecircles build      # generates out/CLINE CIRCLES.gmd
# then, in Geometry Dash (with the GDShare mod / Geode):
#   GDShare -> Import -> out/CLINE CIRCLES.gmd
```

See `docs/VERIFICATION.md` for exactly what is verified vs. assumed, and
`docs/ARCHITECTURE.md` for the internal design.

