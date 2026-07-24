# Model Card: Music Recommender Simulation

## Overview

This is a **content-based, weighted-score recommender** for a synthetic song
catalog. It is a simulation built for an educational project, not a
production system -- there is no real user data, no trained model, and no
personalization beyond the static `user_prefs` dict passed in at call time.

## Dataset

- 20 songs, defined in `recommender/songs.py` as a list of dicts.
- 5 genres: hip-hop, edm, acoustic, indie-rock, pop (3-5 songs each).
- 10 distinct artists; several artists have 2-3 songs deliberately, so the
  diversity/fairness feature has repetition to correct.
- Attributes per song:
  - **Core**: `title`, `artist`, `genre`, `mood`, `energy` (0-10), `tempo`
    (BPM), `era` (decade label)
  - **Extended** (added in a second pass, see `ai_interactions.md`):
    `popularity` (0-100), `release_decade` (int), `mood_tags` (list of
    finer-grained mood descriptors), `danceability` (0-10), `acousticness`
    (0-10)
- All values are hand-authored/synthetic, not derived from real streaming
  data or real audio analysis.

## Intended use

Educational demonstration of how content-based recommendation works: how
input features + a taste profile combine into a ranked, explainable output.
**Not** intended for use with real listener data, real songs, or any
production recommendation surface.

## Algorithmic approach (plain language)

For each song, every attribute is turned into a 0-1 "how well does this match
what the user asked for" number:

- Genre and era: exact match = 1.0, no match = 0.0 (categorical).
- Mood: 1.0 if the song's primary mood is in the user's preferred moods, 0.6
  if only a secondary `mood_tags` entry overlaps, else 0.0 (partial credit
  for related-but-not-exact moods).
- Energy, tempo, danceability, acousticness: linear closeness -- the further
  the song's value is from the user's target, the lower the score, reaching
  0 at a fixed maximum distance.
- Popularity: scored relative to the user's stated mainstream/underground
  preference (or a neutral 0.5 if the user has no preference).

Those eight 0-1 numbers are combined into one score via a **weighted sum**
(weights sum to ~1.0, final score scaled to 0-100). Which weights are used
depends on the selected **ranking mode** (`balanced`, `genre_first`,
`mood_first`, `energy_similarity` -- see README) -- this is a Strategy
pattern: the similarity math never changes, only which features the weights
emphasize. Songs are sorted by score descending and the top N are returned,
each with a generated explanation naming the 1-2 features that contributed
the most to its score.

An optional **diversity pass** (`recommender/diversity.py`) can be applied
before truncating to top N: it greedily re-ranks by docking a song's
effective score every time its artist or genre has already appeared earlier
in the picked list, which spreads recommendations across more artists/genres
instead of letting one strong genre match monopolize every slot.

## Limitations and biases

- **No collaborative signal.** Real recommenders lean heavily on "users like
  you also liked this" -- this system only ever looks at content features and
  one user's stated preferences, so it can never surprise a listener with
  something outside their stated taste, and it can't benefit from the wisdom
  of other listeners.
- **Small, synthetic, imbalanced dataset.** 20 songs across 5 genres (3-5
  each) is orders of magnitude smaller than a real catalog, and genre
  representation is roughly even here only because it was hand-designed that
  way -- a real dataset scraped from a real service is rarely this balanced,
  and genre imbalance in the input data directly biases which genres tend to
  score well overall.
- **Popularity bias risk.** The `popularity_preference` feature, if set to
  "mainstream," directly rewards already-popular songs, which is exactly the
  feedback loop that causes real platforms to concentrate plays on a small
  set of already-famous artists ("rich get richer").
- **Filter-bubble risk without diversification.** Because genre is a hard
  0/1 match worth up to 25-45% of the score depending on mode, a user with
  one strongly-weighted genre preference will see their list dominated by
  that genre and, within it, by whichever artist happens to have the most
  catalog matches -- demonstrated in the README's Hip-Hop Head example, where
  the same artist appears twice in the unfiltered top 4. The `--diversify`
  flag mitigates but does not eliminate this (it re-ranks by penalty, it
  doesn't guarantee a fixed diversity quota).
- **Static preferences, no learning.** `user_prefs` is authored once and
  never updated from behavior (skips, replays, likes) -- real systems infer
  and continuously update taste profiles; this one requires the user (or
  the profile author) to state preferences explicitly and correctly.
- **Categorical matching is brittle.** Genre and era use exact string match,
  so a song tagged `"hip-hop"` scores 0 against a user who typed
  `"hiphop"` or `"rap"` -- there is no synonym/ontology layer.

## Improvement ideas

1. Replace exact-match genre scoring with a genre-similarity graph (e.g.
   hip-hop and R&B partially overlap) instead of binary 0/1.
2. Add a lightweight collaborative-filtering signal (co-occurrence of songs
   across many synthetic "listening histories") to complement the pure
   content-based score.
3. Let `--diversify` accept a target quota (e.g. "no more than 2 songs per
   artist in the top 10") instead of only a soft penalty, for a stronger
   fairness guarantee.
4. Log which explanation-features actually got clicked/skipped, and use that
   to auto-tune the ranking-mode weights per user instead of requiring a
   fixed preset.

## Stretch features implemented

- **Extra attributes** (`popularity`, `release_decade`, `mood_tags`,
  `danceability`, `acousticness`) -- see `ai_interactions.md`.
- **Diversity/fairness component** -- `recommender/diversity.py`, described
  above and demonstrated in the README.
- **Multiple ranking modes** -- `balanced`, `genre_first`, `mood_first`,
  `energy_similarity` in `recommender/scoring.py`, switchable via
  `python main.py --mode <name>`.
- **Visual output** -- `main.py` renders results as a `tabulate` table
  (title, artist, genre, score, explanation) instead of raw prints.
