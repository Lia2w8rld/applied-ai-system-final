"""Evaluation harness: runs predefined histories and prints a pass/fail summary."""
from src.history import load_songs_by_id, load_history
from src.pipeline import recommend
from src.retriever import Retriever

songs = load_songs_by_id()
retriever = Retriever()


def H(*pairs):
    return [{"song_id": i, "action": a} for i, a in pairs]


# (name, history, expected outcome, max allowed confidence or None)
CASES = [
    ("sample history file", load_history(), "ok", None),
    ("all likes (r&b/neo soul)", H((21, "like"), (23, "like"), (35, "like")), "ok", None),
    ("mostly skips", H((21, "like"), (26, "skip"), (39, "skip"), (40, "skip"), (41, "skip")), "ok", None),
    ("single listen (low conf)", H((21, "like")), "ok", 0.3),
    ("empty history", [], "error", None),
    ("only skips", H((26, "skip"), (39, "skip")), "error", None),
    ("unknown song ids", H((999, "like"), (998, "like")), "error", None),
    ("every song already heard", [{"song_id": i, "action": "full_play"} for i in songs], "error", None),
]

passed, confs = 0, []
for name, hist, expect, max_conf in CASES:
    try:
        out = recommend(songs, hist, retriever)
        heard = {h["song_id"] for h in hist}
        recs = out["recommendations"]
        ok = (expect == "ok" and len(recs) == 5
              and not any(r["id"] in heard for r in recs)
              and 0.0 <= out["confidence"] <= 1.0
              and (max_conf is None or out["confidence"] <= max_conf))
        detail = f"top pick={recs[0]['title']!r} confidence={out['confidence']}"
        confs.append(out["confidence"])
    except ValueError as e:
        ok = expect == "error"
        detail = f"handled error: {e}"
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'}  {name:28s} {detail}")

print(f"\nSUMMARY: {passed}/{len(CASES)} passed; "
      f"average confidence on successful runs = {sum(confs)/len(confs):.2f}")

base = recommend(songs, load_history(), None)["recommendations"]
rag = recommend(songs, load_history(), retriever)["recommendations"]
changed = len({r["id"] for r in rag} - {r["id"] for r in base})
print(f"\nINFO retrieval changed {changed} of 5 picks on the sample history")
print("  baseline :", [r["title"] for r in base])
print("  retrieval:", [r["title"] for r in rag])
