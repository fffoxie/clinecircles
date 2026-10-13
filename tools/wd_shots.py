"""Load the full CLINE CIRCLES level in Web Dashers and capture screenshots."""
from __future__ import annotations
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
from clinecircles.layout import build_level
from clinecircles.decoration import decorate
from clinecircles.effects import apply_effects
from clinecircles.serialization import build_level_string, compress_level_string
from wd_harness import OUT, WebDashers

res = build_level()
decorate(res)
apply_effects(res)
packed = compress_level_string(build_level_string(res.level))
print(f"full level: {len(res.level.objects)} objects")

with WebDashers() as wd:
    wd.install_level("CLINE CIRCLES", packed, song_id=-1, created_id=960000)
    print("start ->", wd.start_level(960000))
    print("ready ->", wd.wait_ready())
    wd.set_total(res.length_units)
    # run with a simple hold so the level is visibly alive
    for i, hold_ms in enumerate((0, 700, 900, 1200)):
        if hold_ms:
            wd.hold(); time.sleep(hold_ms/1000); wd.release()
        time.sleep(0.6)
        st = wd.state() or {}
        px = (st.get("x") or 0) - 419.0
        wd.screenshot(f"{OUT}/cline_{i}_x{int(px)}.png")
        print(f"  shot {i}: x={px:.0f} y={st.get('y')} mode={st.get('mode')} dead={st.get('dead')}")
    print("errors:", wd.errors[-3:])
