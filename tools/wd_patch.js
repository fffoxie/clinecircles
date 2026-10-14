// Injected before any page script: capture the Phaser.Game instance so we can
// reach GameScene (which owns _startCreatedLevel / _openPlayMenu).
(function () {
  let _P;
  Object.defineProperty(window, "Phaser", {
    configurable: true,
    get() { return _P; },
    set(v) {
      _P = v;
      try {
        const Orig = v.Game;
        function Wrapped(...args) {
          const g = new Orig(...args);
          window.__game = g;
          return g;
        }
        Wrapped.prototype = Orig.prototype;
        Object.assign(Wrapped, Orig);
        v.Game = Wrapped;
      } catch (e) { window.__patchErr = String(e); }
    },
  });
})();
