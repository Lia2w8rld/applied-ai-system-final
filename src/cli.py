import argparse
import logging
import sys

from .history import load_songs_by_id, load_history
from .pipeline import recommend
from .retriever import Retriever


def show(result, title):
    print(f"\n=== {title} (confidence {result['confidence']}) ===")
    for i, r in enumerate(result["recommendations"], 1):
        print(f"{i}. {r['title']} - {r['artist']} [{r['genre']}, {r['mood']}] score {r['score']}")
        for line in r["why"]:
            print(f"     - {line}")


def main(argv=None):
    p = argparse.ArgumentParser(description="VibeFinder 2.0: history-aware music recommender")
    p.add_argument("--songs", default="data/songs.csv")
    p.add_argument("--history", default="data/listening_history.csv")
    p.add_argument("--baseline", action="store_true", help="disable retrieval (RAG)")
    args = p.parse_args(argv)
    try:
        songs = load_songs_by_id(args.songs)
        history = load_history(args.history)
        retriever = None if args.baseline else Retriever()
        result = recommend(songs, history, retriever)
    except (ValueError, FileNotFoundError) as e:
        logging.error("Run failed: %s", e)
        print(f"Error: {e}")
        return 1

    print("Learned feature weights (higher = better predicts what you keep vs skip):")
    for f, w in result["profile"]["weights"].items():
        print(f"  {f}: {w:.2f}")
    if result["retrieved"]:
        print("\nRetrieved notes:")
        for d in result["retrieved"]:
            print(f"  [{d['score']:.2f}] {d['text'][:80]}...")
    show(result, "Baseline (no retrieval)" if args.baseline else "VibeFinder 2.0 (with retrieval)")
    print("\nTrace:")
    for step in result["trace"]:
        print(f"  - {step}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
