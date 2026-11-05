# 🎵 VibeFinder: Music Recommender

A content-based recommender that ranks songs for a listener's taste profile and explains why each song made the list. Built in Python for CodePath AI110 (AI-Assisted Software Engineering), starting from course starter code.

## What I built

The starter code only returned the first songs in the catalog. I added:

- **CSV loading and cleaning** for a 20-song catalog (I expanded it from the starter dataset)
- **A weighted scoring function** over 7 features (genre, mood, energy, tempo, valence, danceability, acousticness)
- **Ranked top-5 recommendations** with a plain-language explanation for every score
- **Three test profiles** (High-Energy Pop, Chill Lofi, Deep Intense Rock) and weight experiments
- **A [model card](model_card.md)** documenting intended use, data, strengths, and limitations

## How it works

```
User profile → load songs from CSV → score each song → sort by score → top 5 + explanations
```

| Signal | Points |
|---|---|
| Genre match | +4 |
| Mood match | +1 |
| Energy, valence, danceability, acousticness | up to +1 each (1 − difference from target) |
| Tempo | up to +1 (difference normalized, since BPM uses a different scale) |

## Sample output

```
<!-- Run `python -m src.main` and paste the real output here -->
```

## Experiments

- **Different profiles get different results:** pop ranked *Sunrise City* first, lofi ranked *Library Rain*, and rock ranked *Wildfire Run*.
- **Doubling the genre bonus (+2 → +4):** genre-matching songs gained 2 points, but the top-5 rankings didn't change for any profile. A weight can make a preference more influential without changing the final order, which is a reminder to check rankings, not just scores.

## Limitations

- 20 simulated songs with hand-assigned attributes, not real listening data
- Genre and mood labels oversimplify music; it ignores lyrics, language, culture, and memories
- It doesn't learn from feedback (skips, replays, likes), which real recommenders like Spotify's and Netflix's rely on
- The weights are design choices, not learned from data

## How I used AI

I designed the system and used Claude to help implement it. The ideas were mine: which features to score, how much each should be worth, the three listener profiles to test, and the experiment of doubling the genre bonus. I then had Claude help turn those decisions into working Python.

I checked the results myself by running each profile and confirming the top songs made sense for that listener (for example, *Library Rain* topping the Chill Lofi list). When I doubled the genre weight, I compared both the scores and the rankings before drawing a conclusion, which is how I noticed the scores changed but the order didn't.

## Run it

```bash
pip install -r requirements.txt
python -m src.main     # print recommendations for the three profiles
pytest                 # run the tests
```

