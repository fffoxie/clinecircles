"""Build data/objects.json - a complete catalogue of Geometry Dash editor objects.

Merges three sources:

1. data/object_table.csv   - the game's own object list (id, class, official name,
                             editor tab + position)
2. data/hitbox_table.csv   - real collision sizes
3. Web Dashers' allObjects.js - the *engine behaviour* of each object as
                             implemented by a GD-compatible engine: engine type
                             (solid / soliddeco / hazard / portal / trigger /
                             pad / ring / speed / deco / particle / pixel /
                             coin), grid size, sprite frame, colour behaviour.

...plus curated, human-written descriptions for the objects that matter, and
results from objects actually tested in Web Dashers.
"""

from __future__ import annotations

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data")
ENGINE_DEFS = "/tmp/wd/engine_defs.json"
TESTED = os.path.join(DATA, "objects_tested.json")

# Engine type -> (role, plain description, how it behaves)
TYPE_INFO = {
    "solid": (
        "gameplay",
        "A SOLID collidable block.",
        "The player collides with it. Landing on its top surface is safe; "
        "touching its side or underside kills. These are platforms, floors, "
        "walls, ceilings and stairs. A continuous row at ground level is a "
        "WALL, not a floor - the engine already supplies the ground."),
    "soliddeco": (
        "decoration",
        "Looks like a solid block but has NO collision.",
        "Purely visual. Safe to overlap the player and other objects. Useful "
        "for building solid-looking scenery and ground art without making the "
        "level unfair."),
    "hazard": (
        "gameplay",
        "A LETHAL object.",
        "Kills the player on any overlap. Spikes, saws, thorns, landmines. "
        "The player must jump over, fly around or time past them."),
    "portal": (
        "gameplay",
        "A game-mode / gravity / size PORTAL.",
        "Triggers when the player's body overlaps it, changing mode, gravity, "
        "size, mirroring or dual state. IMPORTANT (tested): the portal must "
        "overlap the player's body vertically - a portal centred at y=15 "
        "(spanning the player's 0..30 band) fires; one placed at y=75 does "
        "not, and the level silently plays as cube."),
    "trigger": (
        "trigger",
        "An invisible LOGIC object.",
        "Fires when the player's x passes the trigger's position. Drives "
        "colour, movement, rotation, opacity, pulses, spawning, camera work, "
        "shaders and the endscreen. No collision of its own."),
    "pad": (
        "gameplay",
        "A jump PAD.",
        "Automatically launches the player when touched - no click needed. "
        "Yellow/pink push up, red pushes much harder, blue flips gravity."),
    "ring": (
        "gameplay",
        "A jump ORB.",
        "The player must CLICK while overlapping it to be launched. Yellow = "
        "jump, pink = small jump, red = big jump, blue/green flip gravity, "
        "black drops the player, dash orbs launch along an angle."),
    "speed": (
        "gameplay",
        "A SPEED portal.",
        "Changes the player's horizontal speed when touched. 0.5x / 1x / 2x "
        "/ 3x / 4x. Placing one changes how long every later section lasts, "
        "so music sync depends on it."),
    "deco": (
        "decoration",
        "A decoration object.",
        "No collision and no gameplay effect. Used for scenery, backgrounds "
        "and detail. Can be coloured and put on any editor layer."),
    "particle": (
        "decoration",
        "An animated particle decoration.",
        "No collision. Plays a looping animated effect (fire, smoke, sparks). "
        "Overuse is a common cause of lag."),
    "pixel": (
        "decoration",
        "A pixel-art block.",
        "No collision. 1x1 pixel-art tiles used to draw pictures. Thousands "
        "of them are usually replaced by a single large decoration."),
    "coin": (
        "gameplay",
        "A collectible coin.",
        "Optional collectible. Touching it collects it; it never kills."),
}

# Curated notes for objects this project actually uses or tested.
CURATED = {
    1: ("The classic solid block. Used for floating platforms and scenery.",
        "Build floors and platforms from these, but let the engine's own "
        "ground carry the player along the bottom of the level."),
    8: ("The classic ground spike. One block wide, kills on contact.",
        "The workhorse hazard. A single spike is cleared by one cube jump; "
        "two or three in a row need an earlier jump."),
    39: ("Half-height spike.", "Smaller hazard, useful for tight timing."),
    144: ("INVISIBLE spike - kills but cannot be seen.",
         "Avoid: it is unfair unless the player has been taught the pattern."),
    10: ("Blue gravity portal - sets gravity to normal (falling down).",
         "Used to return to normal gravity after a ceiling section."),
    11: ("Yellow gravity portal - inverts gravity (falling up).",
         "Sends the player to the ceiling; remember ceilings need geometry."),
    12: ("Cube portal - returns the player to cube form.",
         "The default mode; used to end a flight section."),
    13: ("Ship portal - the player flies, hold to rise, release to dive.",
         "Needs a corridor at least ~5-6 blocks tall to be fair."),
    47: ("Ball portal - click to flip gravity, must touch a surface.",
         "Works best over pits and between two surfaces."),
    111: ("UFO portal - click for short hops, gravity always pulls down.",
         "Openings should be ~3 blocks or more to be readable."),
    660: ("Wave portal - flies at a 45 degree angle; vertical speed equals "
          "horizontal speed.",
          "The tightest mode. Openings below ~2.5 blocks get very hard fast."),
    745: ("Robot portal - hold to jump higher, release for a short hop.",
          "Great for variable-height jumps over rising hazards."),
    1331: ("Spider portal - click to teleport to the next surface and flip "
           "gravity.",
           "Needs surfaces above and below; pits with spikes force a teleport."),
    1933: ("Swing portal (2.2) - a continuously flipping flight mode.",
           "NOTE: not implemented by the Web Dashers test engine, so it "
           "could only be validated structurally here."),
    200: ("Speed portal: SLOW (0.5x).", "Eases timing for precise sections."),
    201: ("Speed portal: NORMAL (1x).",
          "The reference speed; all jump distances in this project are "
          "quoted against it."),
    202: ("Speed portal: FAST (2x).",
          "Halves the time between obstacles; the same pattern becomes much "
          "harder."),
    203: ("Speed portal: VERY FAST (3x).", "For short, high-energy bursts."),
    1334: ("Speed portal: SUPER FAST (4x).",
           "Extreme; only fair in open flight sections."),
    36: ("Yellow jump orb - click while touching to jump again in midair.",
         "The main tool for chaining jumps across wide gaps."),
    84: ("Blue gravity orb - flips gravity and boosts.",
         "Used to cross a pit and land on the ceiling."),
    1333: ("Red jump orb - a much bigger jump than yellow.",
           "Covers large gaps where a yellow orb would fall short."),
    141: ("Pink jump orb - a smaller jump than yellow.",
          "Good for fine-tuning height."),
    35: ("Yellow jump pad - launches automatically without a click.",
         "Useful when the player is already busy."),
    1332: ("Red jump pad - the strongest launch.",
           "Clears very large obstacles."),
    899: ("Colour trigger - fades one colour channel to a new RGB value.",
          "The backbone of the level's palette changes between sections."),
    901: ("Move trigger - moves a target group over a duration.",
          "Animates platforms, backgrounds and the robot mascot."),
    1006: ("Pulse trigger - flashes a colour channel or group.",
           "Rhythm flashing; tie to the beat, not to every frame."),
    1007: ("Alpha trigger - fades a target group's opacity.",
           "Used for blinks, fades and reveal transitions."),
    1049: ("Toggle trigger - turns a group on or off.",
           "Spawns/despawns decoration and changes states."),
    1268: ("Spawn trigger - fires another trigger after a delay.",
           "The main way to sequence effects in time."),
    1346: ("Rotate trigger - spins a target group.",
           "Used for rotating architecture and the giant eye motifs."),
    1520: ("Shake trigger - shakes the screen.",
           "Emphasises impacts; keep it short or it becomes unreadable."),
    1913: ("Zoom camera trigger - changes the camera zoom.",
           "Creates the feeling of diving in or pulling back."),
    2909: ("Glitch shader - real screen-space glitch distortion.",
           "Digital-artefact transitions; strong but can hurt readability."),
    2913: ("Lens circle shader - magnifies around a centre.",
           "Used for the 'dive through the pupil' transition."),
    2917: ("Pinch shader - warps the screen inward.",
           "Used for the collapse-to-a-point transition."),
}


def load_object_table() -> dict[int, dict]:
    out: dict[int, dict] = {}
    with open(os.path.join(DATA, "object_table.csv"), newline="",
              encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                oid = int(row["object id"])
            except (KeyError, ValueError):
                continue
            out[oid] = {
                "name": (row.get("community alias") or "").strip(),
                "gmdkit_alias": (row.get("gmdkit alias") or "").strip(),
                "gd_class": (row.get("gd class") or "").strip(),
                "editor_tab": row.get("editor tab") or "",
                "editor_tab_index": row.get("tab index") or "",
            }
    return out


def load_hitboxes() -> dict[int, tuple[float, float]]:
    out: dict[int, tuple[float, float]] = {}
    with open(os.path.join(DATA, "hitbox_table.csv"), newline="",
              encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                out[int(row["ID"])] = (float(row["Width"]), float(row["Height"]))
            except (KeyError, ValueError):
                continue
    return out


def load_engine() -> dict[str, dict]:
    if not os.path.exists(ENGINE_DEFS):
        return {}
    with open(ENGINE_DEFS) as fh:
        return json.load(fh)


def main() -> int:
    table = load_object_table()
    hit = load_hitboxes()
    engine = load_engine()
    tested = {}
    if os.path.exists(TESTED):
        with open(TESTED) as fh:
            tested = {int(k): v for k, v in json.load(fh).items()}

    objects: dict[str, dict] = {}
    all_ids = sorted(set(table) | {int(k) for k in engine if k.isdigit()})
    counts: dict[str, int] = {}

    for oid in all_ids:
        info = table.get(oid, {})
        eng = engine.get(str(oid), {})
        etype = eng.get("type", "unknown")
        counts[etype] = counts.get(etype, 0) + 1
        role, short, how = TYPE_INFO.get(
            etype, ("unknown", "Role not determined.", ""))
        name = info.get("name") or eng.get("frame") or f"object {oid}"

        entry: dict[str, object] = {
            "id": oid,
            "name": name,
            "role": role,
            "engine_type": etype,
            "summary": short,
            "how_it_works": how,
        }
        if info.get("gd_class"):
            entry["gd_class"] = info["gd_class"]
        if info.get("editor_tab"):
            entry["editor_tab"] = int(info["editor_tab"])
            entry["editor_tab_index"] = int(info.get("editor_tab_index") or 0)
        if eng:
            size = [eng.get("gridW"), eng.get("gridH")]
            entry["size_blocks"] = size
            entry["colorable"] = bool(eng.get("can_color"))
            if eng.get("sub"):
                entry["sub"] = eng["sub"]
            if eng.get("frame"):
                entry["sprite"] = {"sheet": eng.get("spritesheet"),
                                   "frame": eng.get("frame")}
            if eng.get("hitbox_radius"):
                entry["hitbox_radius"] = eng["hitbox_radius"]
        if oid in hit:
            entry["hitbox_units"] = list(hit[oid])
        if oid in CURATED:
            entry["summary"], entry["how_it_works"] = CURATED[oid]
            entry["curated"] = True
        if oid in tested:
            t = dict(tested[oid])
            # Confidence depends on HOW the result was measured.
            #   * state flags (isFlying/isUfo/...) are read straight from the
            #     engine, so a portal result is trustworthy.
            #   * collision verdicts rely on the player's world x lining up with
            #     the object's level x. That frame could not be confirmed in the
            #     test engine, so those are recorded but NOT trusted.
            if t.get("flags"):
                t["confidence"] = "verified (engine state flags)"
            else:
                t["confidence"] = ("LOW - collision x-frame unconfirmed; "
                                   "treat as unverified")
            entry["tested"] = t
        objects[str(oid)] = entry

    # which objects does this project actually use?
    used: list[int] = []
    try:
        sys.path.insert(0, os.path.join(ROOT, "src"))
        from clinecircles import gamedata  # noqa: E402
        used = sorted({int(o) for o in gamedata.Obj})
    except Exception as exc:  # pragma: no cover
        print("note: could not list used objects:", exc)
    for u in used:
        if str(u) in objects:
            objects[str(u)]["used_by_cline_circles"] = True

    doc = {
        "meta": {
            "description": ("Catalogue of Geometry Dash editor objects: official "
                            "name, engine behaviour, collision, and how each one "
                            "is used."),
            "sources": [
                "data/object_table.csv (game object list)",
                "data/hitbox_table.csv (collision sizes)",
                "Web Dashers allObjects.js (engine behaviour: type, grid size, "
                "sprite, colour rules)",
                "first-hand tests in Web Dashers (data/objects_tested.json)",
            ],
            "total_objects": len(objects),
            "counts_by_engine_type": dict(sorted(counts.items(),
                                                 key=lambda kv: -kv[1])),
            "roles": {
                "gameplay": "affects the player directly",
                "decoration": "visual only, no collision",
                "trigger": "logic only, no collision",
                "unknown": "not present in the engine object list",
            },
            "legend_engine_types": {k: v[1] for k, v in TYPE_INFO.items()},
        },
        "objects": objects,
    }
    out = os.path.join(DATA, "objects.json")
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=1)
    print(f"wrote {out}")
    print(f"  {len(objects)} objects")
    for k, v in doc["meta"]["counts_by_engine_type"].items():
        print(f"    {k:12s} {v:5d}")
    print(f"  curated: {sum(1 for o in objects.values() if o.get('curated'))}")
    print(f"  tested:  {sum(1 for o in objects.values() if o.get('tested'))}")
    print(f"  used by CLINE CIRCLES: {len(used)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
