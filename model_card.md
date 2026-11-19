# Model Card: VibeFinder 2.0

**Base project:** VibeFinder: Music Recommender Simulation (Module 3). This card covers the extended Project 4 system. The original card is in `assets/model_card_module3.md`.

## Intended use
Classroom demonstration of a history-aware, explainable music recommender. Not intended for real listeners at scale or for any decision that affects people.

## How it works
1. Reads a listening history (like, replay, full_play, skip) and a 44-song catalog.
2. Learns a target sound from kept songs, and raises the weight of features that separate kept songs from skipped ones.
3. Optionally retrieves notes about genres and artists (TF-IDF over 28 hand-written notes) and uses them for similar-artist and neighbor-genre bonuses.
4. Scores only unheard songs, returns the top 5 with reasons, and reports a confidence score (history size x score gap).

## Data
- **Catalog:** 20 fictional starter songs from the course + 24 real songs by 12 artists. Audio features (energy, valence, danceability, acousticness) and tempos are rough estimates drafted with Claude's help, **not measured from audio**.
- **Listening history:** a 30-row hand-written sample, not real streaming data.
- **Knowledge notes:** short notes on 16 genres and 12 artists, subjective and drafted with AI assistance.

## Evaluation results
- `eval.py`: 8/8 cases passed (4 normal, 4 error cases); average confidence 0.23 on successful runs, low by design because several cases have very little history.
- `pytest`: 6/6 passed.
- Retrieval changed 1 of 5 recommendations vs. the baseline on the sample history (*Library Rain* became *Chain of Fools*).
- Learned weights on the sample history: acousticness 1.75, energy 1.50, danceability 1.37, valence 1.02, which matches the skip pattern in the data.

## Limitations and biases
- **Simulated data.** Audio features and history are not real measurements, so the output shows the method works, not that it predicts real taste.
- **Narrow catalog bias.** The real songs come from 12 artists, mostly r&b, neo soul, soul, and hip hop, so those genres dominate recommendations. Other genres, languages, and cultures are barely represented.
- **Filter bubble.** Genres the listener keeps get a bonus and there is no diversity step, so it recommends more of the same.
- **A skip is treated as dislike.** In reality people skip for many reasons (mood, context, already heard it today).
- **Neighbor-genre bonus is dormant.** On the sample history the retriever returned only artist notes, so genre-neighbor boosts never fired. This was visible in the trace, not in the tests.
- **Confidence is a heuristic, not calibrated.** It rises with more history and a bigger score gap, but it was never validated against real outcomes.
- **Keyword retrieval.** TF-IDF matches words, not meaning, and the notes are small.
- **Privacy.** Listening history is personal data. This system keeps it local and makes no network calls, but a real deployment would need consent and protection.

## AI collaboration
*(Draft based on the build session. Edit it so it is accurate to your experience.)*

**How I used AI.** I used Claude to map the assignment to a plan (RAG + learning from history + reliability harness), to write the code modules, to draft the catalog estimates, sample history, and knowledge notes, and to debug terminal errors (a missing GitHub repo, a pytest import path, and `python` vs `python3`). I chose the direction: extending my music recommender toward similar artists and learning from skips, and I picked the 12 artists.

**Suggestion I accepted.** Claude proposed an offline TF-IDF retriever and a transparent weight-learning rule instead of an LLM API or a trained model. I accepted it because anyone can run the repo without an API key and every learned weight can be printed and explained.

**Suggestions I revised or did not adopt.**
- Claude's new catalog rows used the genre label `r&b`, but my starter data already used `rnb`. A genre check exposed the mismatch, and I normalized everything to `r&b` so the two wouldn't count as different genres.
- Claude's first run commands used `python`, which doesn't exist on my Mac, so the first saved outputs were empty. I switched everything to `python3` and regenerated them.
- Claude suggested an optional agentic self-check loop. I did not build it because of the deadline, and the trace in the CLI output is a pipeline log, not an agent.

**How I checked the AI's work.** I ran `eval.py` and `pytest`, read the printed trace, and compared the baseline and retrieval outputs. The trace is how I learned the neighbor-genre path never fired.

**TODO: it did feel right as a user to me.

## Future improvements
- Retrieve genre notes with a separate query so neighbor-genre boosts actually fire.
- Replace estimated features and the sample history with real data (an audio-features API and an actual listening export).
- Add diversity re-ranking and an agentic self-check ("are all five picks the same genre? rerun with a penalty").
- Evaluate with a held-out history (precision@k) instead of only pass/fail cases.
