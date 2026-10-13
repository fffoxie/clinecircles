"""Headless playtest harness for Web Dashers.

Web Dashers (https://web-dashers.github.io/) is a separate browser
reimplementation of Geometry Dash. Its `parseLevel()` accepts exactly the
level-string format this project emits (base64url + inflate, `;`-separated
objects, same numeric property keys), so a generated level can be loaded into
it for real gameplay testing.

Capabilities: install a level in `localStorage.created_levels`, launch it with
the game's own `_startCreatedLevel()`, send real keyboard input (SPACE/UP/W),
sample the game's own state every animation frame, screenshot the canvas.

This is NOT Geometry Dash. Results here are *simulator validation*; only a
native GD client can establish *native compatibility*.

Verified interface facts (from the live site's source):
  * scenes are [BootScene, GameScene]; GameScene owns _startCreatedLevel
  * the Phaser.Game instance is captured by tools/wd_patch.js as window.__game
  * horizontal position is scene._playerWorldX (PlayerState has no `x`)
  * vertical position is scene._state.y; velocity scene._state.yVelocity
  * mode flags: _state.isShip / isUfo / isBall / isWave / isRobot / isSpider
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from playwright.sync_api import sync_playwright

URL = "https://web-dashers.github.io/"
OUT = "/workspace/out"
LD_LIB = "/tmp/wdroot/usr/lib/x86_64-linux-gnu:/tmp/wdroot/lib/x86_64-linux-gnu"
HERE = os.path.dirname(os.path.abspath(__file__))

SAMPLER_JS = r"""
window.__wd = (function () {
  const trace = [];
  let running = false;
  let cached = null;
  function gs() {
    const g = window.__game;
    if (!g || !g.scene || !g.scene.scenes) return null;
    if (cached && cached.sys && cached.sys.isActive && cached.sys.isActive()) return cached;
    cached = g.scene.scenes.find(function (s) {
      return s.sys && s.sys.settings && s.sys.settings.key === 'GameScene';
    }) || null;
    return cached;
  }
  function modeOf(s) {
    return s.isShip ? 'ship' : s.isUfo ? 'ufo' : s.isBall ? 'ball'
      : s.isWave ? 'wave' : s.isRobot ? 'robot' : s.isSpider ? 'spider'
      : s.isSwing ? 'swing' : 'cube';
  }
  function frame() {
    const sc = gs();
    const s = sc && sc._state;
    if (s) {
      trace.push({ t: performance.now(), x: sc._playerWorldX, y: s.y,
                   vy: s.yVelocity, g: s.onGround ? 1 : 0,
                   dead: s.isDead ? 1 : 0, mode: modeOf(s),
                   grav: s.gravityFlipped ? 1 : 0 });
      if (trace.length > 80000) running = false;
    }
    if (running) requestAnimationFrame(frame);
  }
  return {
    gs: gs,
    start: function () { trace.length = 0; if (!running) { running = true; requestAnimationFrame(frame); } },
    stop: function () { running = false; },
    trace: function () { return trace; },
    last: function () { return trace[trace.length - 1] || null; },
    total: function () { return window.__wdTotal || 0; },
    setTotal: function (v) { window.__wdTotal = v; }
  };
})();
"""


@dataclass
class Sample:
    t: float
    x: float
    y: float
    vy: float
    g: int
    dead: int
    mode: str
    grav: int


class WebDashers:
    """A controllable Web Dashers session."""

    def __init__(self, headless: bool = True,
                 viewport: tuple[int, int] = (1138, 640)):
        self.headless = headless
        self.viewport = viewport
        self._pw = None
        self.browser = None
        self.page = None
        self.console: list[str] = []
        self.errors: list[str] = []
        self.created_id = 900000
        self.level_name = "CLINE CIRCLES"

    def __enter__(self) -> "WebDashers":
        os.environ["LD_LIBRARY_PATH"] = LD_LIB
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(
            headless=self.headless,
            args=["--use-gl=angle", "--use-angle=swiftshader",
                  "--enable-unsafe-swiftshader", "--no-sandbox",
                  "--disable-gpu-sandbox", "--mute-audio"],
        )
        self.page = self.browser.new_page(
            viewport={"width": self.viewport[0], "height": self.viewport[1]})
        self.page.on("console",
                     lambda m: self.console.append(f"{m.type}: {m.text}"))
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        with open(os.path.join(HERE, "wd_patch.js")) as fh:
            self.page.add_init_script(fh.read())
        self.page.goto(URL, wait_until="load", timeout=90000)
        self.page.wait_for_timeout(7000)
        self.page.evaluate(SAMPLER_JS)
        return self

    def __exit__(self, *exc: Any) -> None:
        try:
            if self.browser:
                self.browser.close()
        finally:
            if self._pw:
                self._pw.stop()

    # ------------------------------------------------------------------
    def install_level(self, name: str, level_string: str,
                      song_id: int = -1, description: str = "CLINE CIRCLES",
                      created_id: int = 900000) -> None:
        """Write a level into Web Dashers' local level store."""
        entry = {
            "levelName": name, "song": "Local", "songId": song_id,
            "levelId": created_id, "levelString": level_string,
            "levelLength": 4, "normalBest": 0, "practiceBest": 0,
            "description": description, "version": 1,
            "status": "Unverified", "createdId": created_id,
        }
        self.page.evaluate(
            "(entry) => { const raw = localStorage.getItem('created_levels');"
            " const list = raw ? JSON.parse(raw) : [];"
            " const f = list.filter(l => l.createdId !== entry.createdId);"
            " f.push(entry);"
            " localStorage.setItem('created_levels', JSON.stringify(f)); }",
            entry)
        self.created_id = created_id
        self.level_name = name

    def start_level(self, created_id: int | None = None) -> bool:
        cid = created_id if created_id is not None else self.created_id
        return bool(self.page.evaluate(
            "(cid) => { const raw = localStorage.getItem('created_levels');"
            " const list = raw ? JSON.parse(raw) : [];"
            " const lvl = list.find(l => l.createdId === cid);"
            " if (!lvl) return false;"
            " const sc = window.__wd.gs(); if (!sc) return false;"
            " sc._startCreatedLevel(lvl, false); return true; }", cid))

    def wait_ready(self, timeout_ms: int = 25000) -> bool:
        waited = 0
        while waited < timeout_ms:
            ok = self.page.evaluate(
                "() => { const sc = window.__wd.gs();"
                " return !!(sc && sc._state && Number.isFinite(sc._playerWorldX)); }")
            if ok:
                self.page.wait_for_timeout(500)
                return True
            self.page.wait_for_timeout(250)
            waited += 250
        return False

    def set_total(self, total: float) -> None:
        self.page.evaluate("(v) => window.__wd.setTotal(v)", total)

    def sample_start(self) -> None:
        self.page.evaluate("() => window.__wd.start()")

    def trace(self) -> list[dict]:
        return self.page.evaluate("() => window.__wd.trace()")

    def state(self) -> dict | None:
        return self.page.evaluate("() => window.__wd.last()")

    def x(self) -> float:
        return float(self.page.evaluate(
            "() => { const sc = window.__wd.gs(); return sc ? sc._playerWorldX : -1; }"))

    def deaths(self) -> int:
        return int(self.page.evaluate(
            "() => { const sc = window.__wd.gs(); return sc ? (sc._totalDeaths||0) : 0; }"))

    def attempts(self) -> int:
        return int(self.page.evaluate(
            "() => { const sc = window.__wd.gs(); return sc ? (sc._levelAttempts||0) : 0; }"))

    def percent(self) -> float:
        return float(self.page.evaluate(
            "() => { const sc = window.__wd.gs(); if (!sc) return 0;"
            " const tot = window.__wdTotal || 0;"
            " if (tot > 0) return Math.max(0, Math.min(100, sc._playerWorldX / tot * 100));"
            " return 0; }"))

    # ------------------------------------------------------------------
    def hold(self) -> None:
        self.page.keyboard.down("Space")

    def release(self) -> None:
        self.page.keyboard.up("Space")

    def tap(self, ms: int = 90) -> None:
        self.page.keyboard.down("Space")
        self.page.wait_for_timeout(ms)
        self.page.keyboard.up("Space")

    def restart(self) -> None:
        self.page.evaluate(
            "() => { const sc = window.__wd.gs();"
            " if (sc && sc._restartLevel) sc._restartLevel(); }")

    def teleport(self, x: float, y: float | None = None) -> bool:
        """Move the player to reach a section quickly (testing aid only)."""
        return bool(self.page.evaluate(
            "(a) => { const sc = window.__wd.gs();"
            " if (!sc || !sc._state) return false;"
            " sc._playerWorldX = a.x;"
            " if (Number.isFinite(sc._cameraX)) sc._cameraX = a.x;"
            " if (a.y !== null) sc._state.y = a.y;"
            " return true; }", {"x": x, "y": y}))

    def screenshot(self, path: str) -> None:
        self.page.screenshot(path=path)
