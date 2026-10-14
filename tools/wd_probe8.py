import sys
sys.path.insert(0, "/workspace/tools"); sys.path.insert(0, "/workspace/src")
from wd_harness import WebDashers, OUT
from clinecircles import gamedata as gd
from clinecircles.level import Level
from clinecircles.model import LevelObject
from clinecircles.serialization import build_level_string, compress_level_string

def run(wd, name, cid, build):
    lv = Level(name=name, creator="Cline", song_id=0)
    build(lv)
    wd.install_level(name, compress_level_string(build_level_string(lv)), song_id=-1, created_id=cid)
    ok = wd.start_level(cid); wd.wait_ready(); wd.page.wait_for_timeout(600); wd.sample_start()
    wd.page.wait_for_timeout(5000)
    tr = wd.trace()
    deaths = []
    prev = 0
    for f in tr:
        if f["dead"] and not prev: deaths.append(round(f["x"],1))
        prev = f["dead"]
    maxx = max((f["x"] for f in tr), default=0)
    ys = [f["y"] for f in tr if not f["dead"]]
    print(f"{name:28s} start={ok} frames={len(tr):4d} maxcamX={maxx:8.1f} "
          f"deaths={deaths[:5]} y_rest={(min(ys) if ys else None)}")

with WebDashers() as wd:
    run(wd, "A floor only", 930001, lambda lv: [lv.add(LevelObject(1, 15+i*30, 15)) for i in range(120)])
    run(wd, "B empty + spike", 930002, lambda lv: lv.add(LevelObject(8, 1300, 15)))
    run(wd, "C floor + spike", 930003, lambda lv: ([lv.add(LevelObject(1, 15+i*30, 15)) for i in range(120)], lv.add(LevelObject(8, 1300, 15))))
    run(wd, "D float blocks", 930004, lambda lv: [lv.add(LevelObject(1, 400+i*30, 75)) for i in range(6)])
    wd.screenshot(f"{OUT}/wd_probe8.png")
