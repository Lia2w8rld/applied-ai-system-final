import csv
import logging
from collections import Counter

FEATURES = ["energy", "valence", "danceability", "acousticness"]
ACTION_SCORE = {"like": 2.0, "replay": 1.5, "full_play": 1.0, "skip": -1.5}

logging.basicConfig(filename="vibefinder.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


def load_songs_by_id(path="data/songs.csv"):
    songs = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                s = dict(r)
                s["id"] = int(r["id"])
                for k in FEATURES + ["tempo_bpm"]:
                    s[k] = float(r[k])
                s["genre"] = r["genre"].strip().lower()
                s["mood"] = r["mood"].strip().lower()
            except (ValueError, KeyError, TypeError, AttributeError) as e:
                logging.warning("Skipping bad song row %r: %s", r, e)
                continue
            songs[s["id"]] = s
    if not songs:
        raise ValueError("No valid songs found in " + path)
    return songs


def load_history(path="data/listening_history.csv"):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            action = (r.get("action") or "").strip().lower()
            try:
                song_id = int(r.get("song_id"))
            except (TypeError, ValueError):
                logging.warning("Bad song_id in history row %r; skipped", r)
                continue
            if action not in ACTION_SCORE:
                logging.warning("Unknown action %r ignored", action)
                continue
            rows.append({"song_id": song_id, "action": action})
    return rows


def learn_profile(history, songs, lr=2.0):
    """Learn a taste profile + feature weights from listening history.

    Kept songs (like/replay/full_play) define the target sound. Features that
    separate kept songs from skipped songs get a higher weight.
    """
    if not history:
        raise ValueError("Listening history is empty - nothing to learn from.")
    kept, skipped = [], []
    for h in history:
        s = songs.get(h["song_id"])
        if s is None:
            logging.warning("History references unknown song id %s; ignored", h["song_id"])
            continue
        if h["action"] == "skip":
            skipped.append(s)
        else:
            kept.append((s, ACTION_SCORE[h["action"]]))
    if not kept:
        raise ValueError("Need at least one liked or played song to learn a profile "
                         "(only skips or unknown song ids were found).")

    total = sum(w for _, w in kept)
    target = {f: sum(s[f] * w for s, w in kept) / total for f in FEATURES}
    if skipped:
        skip_mean = {f: sum(s[f] for s in skipped) / len(skipped) for f in FEATURES}
    else:
        skip_mean = dict(target)
    weights = {f: 1.0 + lr * abs(target[f] - skip_mean[f]) for f in FEATURES}

    profile = {
        "target": target,
        "skip_mean": skip_mean,
        "weights": weights,
        "genre_kept": Counter(s["genre"] for s, _ in kept),
        "genre_skipped": Counter(s["genre"] for s in skipped),
        "mood_kept": Counter(s["mood"] for s, _ in kept),
        "liked_artists": sorted({s["artist"] for s, w in kept if w >= 1.5}),
        "confidence": min(1.0, (len(kept) + len(skipped)) / 20),
    }
    logging.info("Learned weights: %s", {k: round(v, 2) for k, v in weights.items()})
    return profile
