#!/usr/bin/env bash
# Prepare the Web Dashers playtest environment.
#
# Chromium (installed by `python -m playwright install chromium`) needs shared
# libraries that are not present in this image and cannot be apt-installed
# (no root). We fetch the Debian packages, extract them into /tmp/wdroot and
# point LD_LIBRARY_PATH at them.
#
# Everything here lands in /tmp (ephemeral). Re-run this script after a
# sandbox reset; it is idempotent.
set -euo pipefail

ROOT=/tmp/wdroot
DEBS=/tmp/apt/cache/archives
LIBS="libglib2.0-0 libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
libatspi2.0-0 libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
libxrandr2 libxcb1 libxkbcommon0 libgbm1 libasound2"

if [ ! -d "$ROOT/usr/lib/x86_64-linux-gnu" ]; then
  echo "== fetching browser libraries =="
  mkdir -p /tmp/apt/lists/partial "$DEBS/partial" /tmp/apt/state/lists/partial
  apt-get -o Dir::State::Lists=/tmp/apt/lists -o Dir::Cache=/tmp/apt/cache \
    -o Acquire::https::Verify-Peer=false -o Acquire::https::Verify-Host=false \
    update >/dev/null 2>&1 || true
  apt-get -o Dir::State::Lists=/tmp/apt/lists -o Dir::State=/tmp/apt/state \
    -o Dir::Cache=/tmp/apt/cache -o APT::Get::Download-Only=true \
    -o Debug::NoLocking=true -y install $LIBS >/dev/null 2>&1 || true
  mkdir -p "$ROOT"
  for d in "$DEBS"/*.deb; do dpkg-deb -x "$d" "$ROOT" 2>/dev/null || true; done
  echo "   extracted $(ls "$DEBS"/*.deb 2>/dev/null | wc -l) packages"
else
  echo "== browser libraries already present =="
fi

# Verify chromium has no missing libraries.
CH=$(ls -d /home/node/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1)
if [ -n "$CH" ]; then
  MISSING=$(LD_LIBRARY_PATH="$ROOT/usr/lib/x86_64-linux-gnu:$ROOT/lib/x86_64-linux-gnu" \
            ldd "$CH" 2>/dev/null | grep -c 'not found' || true)
  echo "== chromium missing libraries: $MISSING =="
fi

# Fetch the Web Dashers source for offline inspection.
if [ ! -d /tmp/wd ]; then
  echo "== fetching web dashers source =="
  mkdir -p /tmp/wd
  for f in core/level core/level-editor core/triggers core/player core/main \
           core/game-scene utils/config game/allObjects game/allLevels; do
    n=$(echo "$f" | tr / _)
    curl -sL --max-time 30 \
      "https://web-dashers.github.io/assets/scripts/$f.js?latest" \
      -o "/tmp/wd/$n.js" || true
  done
  curl -sL --max-time 30 "https://web-dashers.github.io/assets/levels/1.txt" \
    -o /tmp/wd/lvl1.txt || true
  echo "   $(ls /tmp/wd | wc -l) files"
fi

echo "== ready =="
echo "   export LD_LIBRARY_PATH=$ROOT/usr/lib/x86_64-linux-gnu:$ROOT/lib/x86_64-linux-gnu"

# ---- sprite atlases (for tools/gd_visualize.py) ----
SHEETDIR=/tmp/sheets
if [ ! -f "$SHEETDIR/GJ_GameSheet.png" ]; then
  echo "== fetching GD sprite atlases =="
  mkdir -p "$SHEETDIR"
  for s in GJ_GameSheet GJ_GameSheet02 GJ_GameSheet03 GJ_GameSheet04 \
           GJ_WebSheet GJ_ParticleSheet GJ_GameSheetEditor GJ_GameSheetGlow; do
    for e in png json; do
      curl -sL --max-time 60 \
        "https://web-dashers.github.io/assets/sheets/$s.$e" \
        -o "$SHEETDIR/$s.$e" || true
    done
  done
  echo "   $(ls "$SHEETDIR" | wc -l) files"
else
  echo "== sprite atlases already present =="
fi

# ---- engine object definitions (sprite frame per object id) ----
if [ ! -f /tmp/wd/engine_defs.json ]; then
  echo "== dumping engine object definitions =="
  cat > /tmp/wd/dump.js <<'JSEOF'
global.window = {};
const fs = require('fs');
eval(fs.readFileSync('/tmp/wd/game_allObjects.js', 'utf8'));
fs.writeFileSync('/tmp/wd/engine_defs.json', JSON.stringify(window.allobjects()));
console.log('   dumped', Object.keys(window.allobjects()).length, 'definitions');
JSEOF
  node /tmp/wd/dump.js || true
fi

# ---- curl the level files too, if missing ----
if [ ! -f /tmp/wd/loading-screen.js ]; then
  curl -sL --max-time 30 \
    "https://web-dashers.github.io/assets/scripts/core/loading-screen.js" \
    -o /tmp/wd/loading-screen.js || true
fi

echo "== visualizer ready: python3 tools/gd_visualize.py <file.gmd> =="
