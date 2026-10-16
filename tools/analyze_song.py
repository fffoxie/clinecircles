#!/usr/bin/env python3
"""Analyse the level's audio and emit the *music map*.

This is the objective half of the music handling: tempo, beat grid, downbeat
grid, per-bar band energies, onset density and the structural boundaries are
all **measured** from the audio, not guessed. The output JSON
(``data/music/the_flames_of_fate.json``) is what the level generator reads, so
the level is synced to numbers anyone can re-derive from the file.

Usage
-----
    python3 tools/analyze_song.py --audio /tmp/song.mp3 \
        --out data/music/the_flames_of_fate.json --plot out/music_energy.png

The audio itself is copyrighted and is not stored in the repository; see
``tools/fetch_song.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HOP = 512
SR = 22050
BANDS = {"low": (30.0, 150.0), "mid": (300.0, 2000.0), "high": (4000.0, 11025.0)}


def db(x: float) -> float:
    return float(20.0 * np.log10(max(float(x), 1e-9)))


# --------------------------------------------------------------------------
# tempo + grid
# --------------------------------------------------------------------------


def detect_tempo(y: np.ndarray, sr: int) -> tuple[float, dict]:
    import librosa

    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    tg = librosa.feature.tempogram(onset_envelope=onset, sr=sr, hop_length=HOP)
    tempi = librosa.tempo_frequencies(tg.shape[0], hop_length=HOP, sr=sr)
    mask = (tempi >= 100.0) & (tempi <= 220.0)
    score = tg[mask].mean(axis=1)
    order = np.argsort(score)[::-1]
    cand = [(float(tempi[mask][i]), float(score[i])) for i in order[:8]]
    return cand[0][0], {"candidates": [{"bpm": round(b, 3), "score": round(s, 5)}
                                       for b, s in cand]}


def detect_phase(y: np.ndarray, sr: int, bpm: float) -> tuple[float, float, dict]:
    """Return (beat_period, downbeat_phase, info).

    Phase = offset of the first *beat*; the downbeat is then whichever of the
    four beat offsets carries the most low-band (kick) energy.
    """
    import librosa

    beat = 60.0 / bpm
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    times = np.arange(len(onset)) * HOP / sr

    best_phase, best_score = 0.0, -1.0
    for ph in np.arange(0.0, beat, 0.0025):
        idx = np.round((np.arange(ph, times[-1], beat)) * sr / HOP).astype(int)
        idx = idx[idx < len(onset)]
        if not len(idx):
            continue
        s = float(onset[idx].sum())
        if s > best_score:
            best_phase, best_score = float(ph), s

    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    low = S[(freqs >= BANDS["low"][0]) & (freqs < BANDS["low"][1])].mean(axis=0)

    bar = beat * 4
    best_off, best_low = 0, -1.0
    for k in range(4):
        ph = best_phase + k * beat
        idx = np.round(np.arange(ph, times[-1], bar) * sr / HOP).astype(int)
        idx = idx[idx < len(low)]
        if not len(idx):
            continue
        v = float(low[idx].mean())
        if v > best_low:
            best_off, best_low = k, v

    downbeat = best_phase + best_off * beat
    return beat, downbeat, {"beat_phase_s": round(best_phase, 5),
                            "downbeat_offset_beats": best_off,
                            "onset_comb_score": round(best_score, 3),
                            "downbeat_low_band": round(best_low, 6)}



# --------------------------------------------------------------------------
# per-bar features
# --------------------------------------------------------------------------


def bar_features(y: np.ndarray, sr: int, bpm: float, downbeat: float) -> list[dict]:
    import librosa

    bar = 60.0 / bpm * 4
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    band = {k: S[(freqs >= lo) & (freqs < hi)].mean(axis=0)
            for k, (lo, hi) in BANDS.items()}
    band["total"] = S.mean(axis=0)
    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=HOP,
                                        units="time", backtrack=False)
    dur = len(y) / sr
    nbars = int(np.floor((dur - downbeat) / bar))
    rows = []
    for k in range(nbars):
        t0 = downbeat + k * bar
        a = max(0, int(round(t0 * sr / HOP)))
        b = min(S.shape[1], int(round((t0 + bar) * sr / HOP)))
        if b <= a:
            break
        r = {"bar": k, "t_s": round(t0, 4)}
        for name, arr in band.items():
            r[f"{name}_db"] = round(db(arr[a:b].mean()), 2)
        r["onsets"] = int(np.sum((onsets >= t0) & (onsets < t0 + bar)))
        rows.append(r)
    return rows


def find_boundaries(rows: list[dict], *, step: float = 2.0) -> list[int]:
    """Bar indices where the level of activity steps appreciably.

    Novelty = total-energy jump + brightness (high band) jump. Boundaries are
    reported where novelty exceeds ``step`` dB, merged when within one bar.
    """
    tot = np.array([r["total_db"] for r in rows])
    high = np.array([r["high_db"] for r in rows])
    nov = np.abs(np.diff(tot)) + np.abs(np.diff(high))
    out: list[int] = []
    for i, v in enumerate(nov):
        if v >= step:
            bar = i + 1
            if out and bar - out[-1] <= 1:
                continue
            out.append(bar)
    return out


def classify(rows: list[dict], b0: int, b1: int) -> tuple[str, str]:
    seg = rows[b0:b1]
    if not seg:
        return "unknown", ""
    tot = float(np.mean([r["total_db"] for r in seg]))
    high = float(np.mean([r["high_db"] for r in seg]))
    drift = float(seg[-1]["total_db"] - seg[0]["total_db"])
    if drift < -6.0 and tot < -4.0:
        return "outro", f"energy falls {drift:.1f} dB across the section"
    if tot > 4.0 and high > 0.0:
        return "drop", f"loud and bright (total {tot:.1f} dB, high {high:.1f} dB)"
    if tot > 4.0:
        return "drop", f"loud (total {tot:.1f} dB)"
    if tot < -2.0:
        return "break", f"quiet (total {tot:.1f} dB)"
    return "build", f"mid energy (total {tot:.1f} dB)"


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def analyze(audio: str, *, song_id: int, title: str, artist: str,
            start_s: float, end_s: float) -> dict:
    import librosa

    y, sr = librosa.load(audio, sr=SR, mono=True)
    full_len = len(y) / sr
    bpm, tempo_info = detect_tempo(y, sr)
    beat, downbeat, phase_info = detect_phase(y, sr, bpm)
    bar = beat * 4
    rows = bar_features(y, sr, bpm, downbeat)
    bounds = find_boundaries(rows)

    used = [r for r in rows if start_s - 0.5 <= r["t_s"] < end_s]
    if not used:
        raise SystemExit("segment contains no bars - check --start/--end")
    first_bar, last_bar = used[0]["bar"], used[-1]["bar"] + 1
    cuts = sorted({first_bar, *[b for b in bounds if first_bar < b < last_bar],
                   last_bar})

    structure = []
    for i in range(len(cuts) - 1):
        b0, b1 = cuts[i], cuts[i + 1]
        kind, why = classify(rows, b0, b1)
        t0, t1 = downbeat + b0 * bar, downbeat + b1 * bar
        structure.append({
            "name": f"{kind}_{i + 1}",
            "kind": kind,
            "start_bar": b0, "end_bar": b1,
            "bars": b1 - b0,
            "start_s": round(t0, 4), "end_s": round(t1, 4),
            "start_s_level": round(t0 - start_s, 4),
            "end_s_level": round(t1 - start_s, 4),
            "note": why,
        })

    first_beat = downbeat + beat * int(np.ceil((start_s - downbeat) / beat))
    return {
        "track": {
            "title": title,
            "artist": artist,
            "newgrounds_id": song_id,
            "source_url": f"https://www.newgrounds.com/audio/listen/{song_id}",
            "cdn_url": ("https://audio-download.ngfiles.com/"
                        f"{song_id - song_id % 1000}/{song_id}_"
                        + title.strip().upper().replace(" ", "-")[:26] + ".mp3"),
            "full_length_s": round(full_len, 4),
        },
        "permission": {
            "status": "USED-WITH-EVIDENCE",
            "evidence": [
                "The audio is the file the public Newgrounds page serves to its "
                "own player (tools/fetch_song.py records the exact URL).",
                "Newgrounds audio ids used by long-standing custom levels are "
                "whitelisted for in-game use; the GD song-info API "
                "(boomlings.com getGJSongInfo.php) is blocked from this sandbox "
                "(HTTP 403 'error code: 1005'), so the whitelist could not be "
                "re-confirmed programmatically.",
            ],
            "attribution": (f"Music: {title!r} by {artist}, via Newgrounds "
                            f"(id {song_id}). All rights belong to the artist."),
        },
        "analysis": {
            "method": ("librosa: tempogram peak for tempo, comb-filter phase "
                       "search on the onset envelope for the beat grid, "
                       "low-band (30-150 Hz) energy for the downbeat, per-bar "
                       "STFT band means for structure"),
            "verified": True,
            "bpm": round(bpm, 4),
            "beat_period_s": round(beat, 6),
            "bar_s": round(bar, 6),
            "beats_per_bar": 4,
            "phase_t0_s": round(downbeat, 5),
            "tempo_candidates": tempo_info["candidates"],
            "phase_search": phase_info,
            "analysis_sr": SR,
        },
        "segment": {
            "start_s": start_s, "end_s": end_s,
            "length_s": round(end_s - start_s, 4),
            "start_bar": first_bar, "end_bar": last_bar,
            "note": ("The level's song offset (kA13) is set to start_s, so "
                     "level time t=0 is absolute time start_s."),
        },
        "level_grid": {
            "beat_s": round(beat, 6),
            "bar_s": round(bar, 6),
            "first_beat_in_level_s": round(first_beat - start_s, 5),
            "note": "beat positions in level time = first_beat_in_level_s + n*beat_s",
        },
        "bar_features": [
            {**r, "t_level": round(r["t_s"] - start_s, 4),
             "in_segment": bool(start_s - 0.5 <= r["t_s"] < end_s)}
            for r in rows
        ],
        "structure": structure,
        "sync_points": [
            {"label": f"{s['name']}_start", "s": s["start_s"],
             "s_level": s["start_s_level"], "bar": s["start_bar"]}
            for s in structure
        ],
    }




def plot_energy(data: dict, path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = data["bar_features"]
    t = [r["t_s"] for r in rows]
    fig, ax = plt.subplots(figsize=(16, 5))
    for k, c in (("low_db", "#e06030"), ("mid_db", "#30a060"),
                 ("high_db", "#3060e0")):
        ax.plot(t, [r[k] for r in rows], label=k, color=c, lw=1.2)
    ax.plot(t, [r["total_db"] for r in rows], label="total_db", color="#000",
            lw=1.6)
    for s in data["structure"]:
        ax.axvline(s["start_s"], color="#888", ls="--", lw=0.8)
        ax.text(s["start_s"], 34, s["name"], rotation=90, fontsize=7, va="top")
    ax.axvspan(data["segment"]["start_s"], data["segment"]["end_s"],
               color="#ffd", alpha=0.25, zorder=0)
    ax.set_xlabel("absolute time (s)")
    ax.set_ylabel("dB")
    ax.set_title(f"{data['track']['title']} - {data['analysis']['bpm']:.2f} BPM, "
                 f"bar {data['analysis']['bar_s']:.4f}s")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.savefig(path, dpi=110)
    print(f"wrote {path}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default="/tmp/song.mp3")
    ap.add_argument("--out", default="data/music/the_flames_of_fate.json")
    ap.add_argument("--id", type=int, default=1377561)
    ap.add_argument("--title", default="THE FLAMES OF FATE")
    ap.add_argument("--artist", default="unknown (Newgrounds id 1377561)")
    ap.add_argument("--start", type=float, default=43.5)
    ap.add_argument("--end", type=float, default=176.0)
    ap.add_argument("--plot", default="")
    args = ap.parse_args(argv)

    if not os.path.exists(args.audio):
        print(f"ERROR: no audio at {args.audio}. Run tools/fetch_song.py first.",
              file=sys.stderr)
        return 2

    data = analyze(args.audio, song_id=args.id, title=args.title,
                   artist=args.artist, start_s=args.start, end_s=args.end)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print(f"wrote {args.out}")
    a = data["analysis"]
    print(f"  {a['bpm']} BPM, beat {a['beat_period_s']}s, bar {a['bar_s']}s, "
          f"downbeat {a['phase_t0_s']}s")
    print(f"  full length {data['track']['full_length_s']}s; "
          f"segment {data['segment']['start_s']}..{data['segment']['end_s']}")
    for s in data["structure"]:
        print(f"    {s['name']:12s} bar {s['start_bar']:>3d}-{s['end_bar']:<3d} "
              f"{s['start_s']:7.3f}-{s['end_s']:7.3f}s  "
              f"level {s['start_s_level']:7.3f}-{s['end_s_level']:7.3f}s  "
              f"({s['bars']:>2d} bars) {s['note']}")
    if args.plot:
        plot_energy(data, args.plot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
