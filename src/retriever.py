import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    def __init__(self, folder="data/knowledge"):
        self.docs = []
        for p in sorted(Path(folder).glob("*.md")):
            for chunk in p.read_text(encoding="utf-8").split("\n\n"):
                if chunk.strip():
                    self.docs.append({"source": p.name, "text": chunk.strip()})
        if not self.docs:
            raise FileNotFoundError(f"No knowledge notes found in {folder}")
        self.vec = TfidfVectorizer(stop_words="english")
        self.matrix = self.vec.fit_transform([d["text"] for d in self.docs])

    def search(self, query, k=6, min_score=0.05):
        sims = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        ranked = sorted(zip(sims, self.docs), key=lambda x: -x[0])[:k]
        return [{**d, "score": float(s)} for s, d in ranked if s >= min_score]

    def artist_sound(self, artist):
        prefix = f"artist: {artist.lower()}."
        for d in self.docs:
            if d["text"].lower().startswith(prefix):
                m = re.search(r"Sound:\s*(.+)$", d["text"])
                return m.group(1).rstrip(".") if m else None
        return None


def _parse(docs, label):
    out = set()
    for d in docs:
        m = re.search(label + r":\s*([^.\n]+)", d["text"])
        if m:
            out.update(x.strip().lower() for x in m.group(1).split(","))
    return out


def neighbor_genres(docs):
    return _parse(docs, "Neighbor genres")


def similar_artists(docs):
    return _parse(docs, "Similar artists")
