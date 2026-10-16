#!/usr/bin/env python3
"""Acquire the level's audio track from Newgrounds (public page -> mp3).

Why this is a script and not a `curl`:

  * `https://www.newgrounds.com/audio/listen/<id>` is behind **NG Guard**, a
    JavaScript proof-of-work challenge. A plain HTTP client gets HTTP 403 with a
    ~660 byte "NG Guard" page, and so does any server-side fetch (r.jina.ai,
    allorigins, ...).
  * The audio itself lives on a public CDN with a *deterministic* filename:

        https://audio-download.ngfiles.com/{id - id % 1000}/{id}_{NAME}.mp3

    where ``NAME`` is the song title, spaces -> ``-``, some punctuation
    url-encoded, truncated to 26 characters. (Pattern documented by
    d4n3436/gddownloader.) The CDN answers 404 for a wrong NAME, so the title
    has to be known first.

So: render the public page in a real (headless) browser, let NG Guard's JS
challenge run, read the title / the ``audio.ngfiles.com`` URL the built-in
player requests, then download from the CDN.

The audio is **copyrighted** and is deliberately NOT committed to the repo:
it is written next to the script's --out path, which lives in ``/tmp`` or in a
gitignored folder.

Usage
-----
    python3 tools/fetch_song.py --id 1377561 --out /tmp/song.mp3

Requires: playwright + chromium (`python3 -m playwright install chromium`),
the shared libraries from ``tools/wd_setup.sh``, and a fontconfig file (see
``tools/wd_setup.sh --fonts``) -- without fonts Chromium aborts with
``FATAL:SkFontMgr_FontConfigInterface.cpp Not implemented`` on pages that draw
text into a canvas, which is exactly what NG Guard does.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

LISTEN_URL = "https://www.newgrounds.com/audio/listen/{id}"
CDN_URL = "https://audio-download.ngfiles.com/{bucket}/{id}_{name}.mp3"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def cdn_name(title: str) -> str:
    """Newgrounds' CDN filename for a title: spaces -> '-', 26 char limit."""
    name = title.strip().upper()
    name = name.replace("'", "039").replace("&", "-").replace("(", "")
    name = name.replace(")", "").replace(",", "").replace(".", "")
    name = re.sub(r"[^A-Za-z0-9_\-]", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name[:26]


def probe(title: str, song_id: int) -> str:
    bucket = song_id - (song_id % 1000)
    return CDN_URL.format(bucket=bucket, id=song_id, name=cdn_name(title))


def fetch_with_browser(song_id: int, *, wait_s: int = 60) -> tuple[str, list[str]]:
    """Render the public page, pass NG Guard, return (title, audio urls)."""
    from playwright.sync_api import sync_playwright

    urls: list[str] = []
    title = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,
                                    args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = browser.new_context(user_agent=UA, locale="en-US",
                                  viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.on("response",
                lambda r: urls.append(r.url) if ".mp3" in r.url else None)
        page.goto(LISTEN_URL.format(id=song_id), wait_until="domcontentloaded",
                  timeout=60000)
        for _ in range(wait_s * 2):
            page.wait_for_timeout(500)
            try:
                title = page.title()
                html = page.content()
            except Exception:
                continue
            if len(html) > 5000 and "NG Guard" not in title:
                break
        try:
            for m in re.findall(r'audio-download\.ngfiles\.com/\d+/\d+_[^"\'\\ ]+\.mp3',
                                html):
                urls.append("https://" + m)
        except Exception:
            pass
        browser.close()
    return title, urls


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, default=1377561)
    ap.add_argument("--out", default="/tmp/song.mp3")
    ap.add_argument("--title", default="",
                    help="skip the browser and use this title for the CDN name")
    args = ap.parse_args(argv)

    title = args.title
    if not title:
        print(f"== rendering {LISTEN_URL.format(id=args.id)} (NG Guard)")
        title, urls = fetch_with_browser(args.id)
        print(f"   page title: {title!r}")
        for u in sorted(set(urls)):
            print(f"   audio url : {u}")

    if not title:
        print("ERROR: could not obtain the page title (NG Guard did not clear).",
              file=sys.stderr)
        return 1

    import urllib.request
    url = probe(title, args.id)
    print(f"== downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    with open(args.out, "wb") as fh:
        fh.write(data)
    print(f"   wrote {args.out} ({len(data)} bytes)  title={title!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
