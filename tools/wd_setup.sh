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
