import logging

from .history import FEATURES, learn_profile
from .retriever import neighbor_genres, similar_artists


def recommend(songs, history, retriever=None, k=5):
    """Recommend unheard songs from listening history.

    With a retriever, notes on genres/artists are retrieved and used to boost
    neighbor genres and similar artists. Without one, this is the baseline.
    """
    if k < 1:
        raise ValueError("k must be at least 1")
    trace = []
    profile = learn_profile(history, songs)
    trace.append(f"Learned profile from {len(history)} history rows; "
                 f"weights={ {f: round(w, 2) for f, w in profile['weights'].items()} }")

    heard = {h["song_id"] for h in history}
    neighbors, similar, docs = set(), set(), []
    if retriever:
        top_genres = [g for g, _ in profile["genre_kept"].most_common(2)]
        query = " ".join(top_genres + profile["liked_artists"])
        docs = retriever.search(query)
        neighbors, similar = neighbor_genres(docs), similar_artists(docs)
        trace.append(f"Retrieved {len(docs)} notes; neighbor genres={sorted(neighbors)}; "
                     f"similar artists={sorted(similar)}")
    else:
        trace.append("Baseline mode: retrieval disabled")

    results = []
    for s in songs.values():
        if s["id"] in heard:
            continue
        why = []
        feature_score = sum(profile["weights"][f] * (1 - abs(s[f] - profile["target"][f]))
                            for f in FEATURES)
        score = feature_score
        sound = feature_score / sum(profile["weights"].values())
        why.append(f"sound match {sound:.0%} to what you keep playing")

        g = s["genre"]
        if g in profile["genre_kept"]:
            score += 3
            why.append(f"you often keep {g}")
        elif g in neighbors:
            score += 1.5
            why.append(f"{g} is a neighbor of genres you like (from notes)")
        if s["mood"] in profile["mood_kept"]:
            score += 1
            why.append(f"mood '{s['mood']}' matches songs you keep")
        if s["artist"].lower() in similar:
            score += 1.5
            why.append(f"{s['artist']} is similar to artists you replay (from notes)")
        n_kept, n_skip = profile["genre_kept"][g], profile["genre_skipped"][g]
        if n_skip and n_skip / (n_kept + n_skip) > 0.5:
            score -= 2
            why.append(f"you usually skip {g}")
        if retriever:
            note = retriever.artist_sound(s["artist"])
            if note:
                why.append(f"about {s['artist']}: {note}")
        results.append({**s, "score": round(score, 2), "why": why})

    if not results:
        raise ValueError("No unheard songs left to recommend.")
    results.sort(key=lambda r: -r["score"])
    top = results[:k]
    gap = (top[0]["score"] - top[-1]["score"]) / max(abs(top[0]["score"]), 1e-9)
    confidence = round(profile["confidence"] * min(1.0, 0.5 + gap), 2)
    trace.append(f"Scored {len(results)} unheard songs; confidence={confidence}")
    logging.info("Recommended %s", [r["title"] for r in top])
    return {"recommendations": top, "confidence": confidence,
            "retrieved": docs, "profile": profile, "trace": trace}
