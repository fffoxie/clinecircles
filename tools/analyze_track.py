"""Offline music analysis: derive real tempo and section structure from audio.

This is used to *verify* the sync map for CLINE CIRCLES instead of guessing.
It decodes an audio file to PCM (via miniaudio) and computes:

* an onset-strength envelope and a tempo estimate (autocorrelation),
* a per-frame RMS energy curve in dB,
* coarse "section" boundaries from energy novelty.

It writes JSON only (no audio is stored in the repository).

Usage:
    python3 tools/analyze_track.py <audio-file> [--out out/music_analysis.json]
"""

from __future__ import annotations

import argparse
import json

import numpy as np


def load_audio(path: str) -> tuple[np.ndarray, int]:
    import miniaudio

    dec = miniaudio.decode_file(path, output_format=miniaudio.SampleFormat.SIGNED16)
    x = np.frombuffer(dec.samples, dtype=np.int16).astype(np.float32) / 32768.0
    if dec.nchannels > 1:
        x = x.reshape(-1, dec.nchannels).mean(axis=1)
    return x, dec.sample_rate


def stft(x: np.ndarray, n_fft: int = 2048, hop: int = 512) -> np.ndarray:
    win = np.hanning(n_fft).astype(np.float32)
    n = 1 + max(0, (len(x) - n_fft) // hop)
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n)[:, None]
    frames = x[idx] * win
    spec = np.fft.rfft(frames, axis=1)
    return np.abs(spec).astype(np.float32)


def onset_envelope(mag: np.ndarray) -> np.ndarray:
    ref = np.maximum(mag.mean(axis=0, keepdims=True), 1e-6)
    db = 20.0 * np.log10(np.maximum(mag, 1e-6) / ref)
    flux = np.maximum(0.0, np.diff(db, axis=0)).sum(axis=1)
    return flux


def estimate_bpm(onset: np.ndarray, frame_rate: float,
                 lo: float = 60.0, hi: float = 200.0) -> tuple[float, float]:
    o = onset - onset.mean()
    ac = np.correlate(o, o, mode="full")[len(o) - 1:]
    min_lag = int(frame_rate * 60.0 / hi)
    max_lag = int(frame_rate * 60.0 / lo)
    if max_lag <= min_lag:
        return 0.0, 0.0
    seg = ac[min_lag:max_lag]
    lag = int(np.argmax(seg)) + min_lag
    bpm = 60.0 * frame_rate / lag
    conf = float(seg.max() / (ac[0] + 1e-9))
    return float(bpm), conf


def rms_db(x: np.ndarray, sr: int, hop: int = 1024) -> tuple[np.ndarray, float]:
    n = len(x) // hop
    frames = x[: n * hop].reshape(n, hop)
    r = np.sqrt((frames ** 2).mean(axis=1))
    return 20.0 * np.log10(np.maximum(r, 1e-6)), sr / hop


def smooth(v: np.ndarray, k: int) -> np.ndarray:
    if k <= 1:
        return v
    ker = np.ones(k, dtype=np.float32) / k
    return np.convolve(v, ker, mode="same")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--out", default="out/music_analysis.json")
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--offset", type=float, default=0.0)
    args = ap.parse_args()

    x, sr = load_audio(args.audio)
    mag = stft(x)
    frame_rate = sr / 512.0
    onset = onset_envelope(mag)
    bpm, conf = estimate_bpm(onset, frame_rate)

    env_db, env_rate = rms_db(x, sr)
    env_s = smooth(env_db, int(env_rate * 0.25))

    # Section boundaries: where the smoothed energy changes sharply.
    d = np.diff(env_s)
    novelty = np.maximum(0.0, d)
    thr = novelty.mean() + 2.0 * novelty.std()
    peaks = np.where(novelty > thr)[0]
    bounds: list[float] = []
    for p in peaks:
        t = p / env_rate
        if not bounds or t - bounds[-1] > 1.5:
            bounds.append(round(float(t), 3))

    # 1-second energy table, useful for eyeballing the arrangement
    step = max(1, int(env_rate))
    table = [(round(i / env_rate, 2), round(float(env_s[i]), 2))
             for i in range(0, len(env_s), step)]

    result = {
        "source": args.audio,
        "duration_s": round(len(x) / sr, 3),
        "sample_rate": sr,
        "tempo": {
            "bpm_estimate": round(bpm, 3),
            "confidence": round(conf, 4),
            "bpm_override": args.bpm,
            "offset_s": args.offset,
        },
        "section_boundaries_s": bounds,
        "energy_db_1s": table,
    }
    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=1)

    print(f"duration {result['duration_s']}s  tempo~{bpm:.2f} BPM (conf {conf:.3f})")
    print(f"section boundaries: {bounds}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
