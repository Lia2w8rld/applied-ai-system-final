import pytest

from src.history import load_songs_by_id, learn_profile
from src.pipeline import recommend
from src.retriever import Retriever

SONGS = load_songs_by_id()


def test_empty_history_raises():
    with pytest.raises(ValueError):
        learn_profile([], SONGS)


def test_skips_raise_weight_of_separating_features():
    hist = [{"song_id": 21, "action": "like"}, {"song_id": 41, "action": "skip"}]
    assert learn_profile(hist, SONGS)["weights"]["energy"] > 1.0


def test_recommendations_exclude_heard_songs():
    hist = [{"song_id": 21, "action": "like"}, {"song_id": 23, "action": "replay"}]
    out = recommend(SONGS, hist, Retriever())
    assert len(out["recommendations"]) == 5
    assert all(r["id"] not in {21, 23} for r in out["recommendations"])


def test_retrieval_changes_scores():
    hist = [{"song_id": 21, "action": "like"}, {"song_id": 23, "action": "replay"}]
    base = [(r["id"], r["score"]) for r in recommend(SONGS, hist, None)["recommendations"]]
    rag = [(r["id"], r["score"]) for r in recommend(SONGS, hist, Retriever())["recommendations"]]
    assert base != rag
