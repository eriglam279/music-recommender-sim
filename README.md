# Music Recommender Simulation

A modular, content-based song recommender built to simulate (in miniature) how
apps like Spotify or TikTok decide what to play you next. No machine learning
model is trained here -- this is a transparent, hand-written weighted-scoring
engine, which is the point: every recommendation can be traced back to exactly
which song attributes caused it.

## How real-world recommenders actually work

Real systems like Spotify's or TikTok's "For You" feed combine three distinct
layers, and it's easy to blur them together if you haven't built one yourself:

1. **Input data / features** -- objective or semi-objective properties of the
   content itself: a song's genre, tempo (BPM), estimated mood/valence,
   danceability, acousticness, release date, and aggregate popularity. None of
   this depends on any specific listener; it's computed once per song (via
   audio analysis and editorial/crowd tagging) and stored.
2. **User preferences / taste profile** -- a model of *this* listener, built
   from their history: which genres they replay, what energy level they skip
   past, what tempo range they linger on, whether they gravitate to
   mainstream hits or deep cuts. Real systems infer this implicitly from
   listens/skips/likes; this simulation makes it explicit as a `user_prefs`
   dict so the mechanism is visible.
3. **Ranking / selection** -- the step that actually decides what you see. The
   input features and the taste profile are combined (usually as a weighted
   score, sometimes via a learned model) into a relevance number *per song*,
   every candidate song gets one, and the top-N by score become the
   recommendation list. Crucially, ranking is a separate step from having the
   data -- two systems with identical song features can rank completely
   differently depending on which features they weight and how.

This project simulates exactly that three-layer split: [`recommender/songs.py`](recommender/songs.py)
is the input data, [`recommender/profiles.py`](recommender/profiles.py) is the taste profiles, and
[`recommender/scoring.py`](recommender/scoring.py) + [`recommender/recommend.py`](recommender/recommend.py) is the ranking
step. Real systems add collaborative filtering (what *similar users* liked)
and sequence models (what you just played), which this project intentionally
leaves out to keep the content-based mechanism legible -- see `model_card.md`
for the limitations that come with that simplification.

## Project layout

```
music-recommender-sim/
├── main.py                      # CLI demo: profiles x ranking modes x diversify
├── recommender/
│   ├── songs.py                 # the song dataset (20 songs, list of dicts)
│   ├── profiles.py              # 4 sample listener taste profiles
│   ├── scoring.py                # score_song() + the 4 ranking-mode weight presets
│   ├── explain.py                # turns score contributions into readable text
│   └── diversity.py              # artist/genre repetition penalty (fairness pass)
├── tests/test_recommender.py    # pytest suite
├── model_card.md
├── ai_interactions.md
└── requirements.txt
```

## Running it

```bash
pip install -r requirements.txt

python main.py                          # all 4 profiles, balanced mode, top 5
python main.py --profile edm_rager       # just one profile
python main.py --mode mood_first         # switch ranking strategy
python main.py --diversify               # apply the fairness/diversity re-rank
python main.py --list-profiles
python main.py --list-modes

python -m pytest tests/ -v
```

## Dataset

[`recommender/songs.py`](recommender/songs.py) has 20 synthetic songs across 5 genres (hip-hop, edm,
acoustic, indie-rock, pop), several of which intentionally repeat an artist so
the diversity feature (below) has something to correct. Each song has:

- Core attributes: `genre`, `mood`, `energy` (0-10), `tempo` (BPM), `era`
- Extra attributes added in a second pass (see `ai_interactions.md`):
  `popularity` (0-100), `release_decade`, `mood_tags` (list of finer-grained
  mood descriptors), `danceability` (0-10), `acousticness` (0-10)

## Scoring: how a song's relevance is calculated

`score_song(user_prefs, song, mode)` in `recommender/scoring.py` computes a
per-feature similarity in `[0, 1]` for genre, mood, energy, tempo, era,
popularity, danceability, and acousticness, then combines them as a weighted
sum:

```
total_score = sum(weight[feature] * similarity(song[feature], user_prefs[feature])) * 100
```

Genre and era use exact-match similarity (1.0 or 0.0); mood gives partial
credit (0.6) if the song's finer-grained `mood_tags` overlap the user's
preferred moods even when the primary `mood` doesn't match exactly; energy,
tempo, danceability, and acousticness use linear closeness (`1 - |diff| / span`).
The **weights** are what changes between ranking modes -- see below.

## Ranking modes (Strategy pattern)

Four interchangeable weight presets live in `RANKING_MODES` in `scoring.py`.
Swapping the mode swaps *which features drive the score* without touching the
similarity math -- this is the Strategy design pattern, documented further in
`ai_interactions.md`:

| Mode | Dominant features |
|---|---|
| `balanced` | genre 25%, mood 20%, energy 20%, danceability 10%, tempo 10%, rest split |
| `genre_first` | genre 45%, everything else secondary |
| `mood_first` | mood 45%, everything else secondary |
| `energy_similarity` | energy 40%, danceability 20%, tempo 15% -- ignores era/popularity entirely |

## Explanations

`explain.py` reads the same per-feature contributions the scorer produced and
surfaces the top 1-2 that actually drove the number -- it never states a
feature that scored 0. Three real examples pulled straight from the output
below:

- *"Corner Store Freestyle" (Hip-Hop Head profile)* → "Recommended for:
  hip-hop genre match + confident mood aligns with your taste" -- both the
  genre and the primary mood are exact matches to the profile.
- *"Porch Light" (Acoustic profile)* → "Recommended for: acoustic genre match
  + calm mood aligns with your taste" -- same pattern, different genre/mood
  pair, showing the explanation is generated from the actual song, not a
  template string.
- *"Voltage Church" (EDM profile, `energy_similarity` mode)* → "Recommended
  for: energy level 10/10 fits your target + danceability 9/10 matches your
  preference" -- note the *reason itself changes* when the ranking mode
  changes, because the mode changes which features dominate the score.

## Three (four) profiles compared

`recommender/profiles.py` defines four listener profiles. Running
`python main.py --top 3` (balanced mode) gives:

```
=== Hip-Hop Head (hiphop_head) | mode=balanced | diversify=False ===
|   # | Title                  | Artist     | Genre   |   Score | Why                                                                           |
|-----|------------------------|------------|---------|---------|-------------------------------------------------------------------------------|
|   1 | Corner Store Freestyle | Dre Larkin | hip-hop |   98.6  | Recommended for: hip-hop genre match + confident mood aligns with your taste  |
|   2 | Trap Door              | Lil Ember  | hip-hop |   91.9  | Recommended for: hip-hop genre match + aggressive mood aligns with your taste |
|   3 | Gold Rush Hour         | Basswell   | hip-hop |   88.55 | Recommended for: hip-hop genre match + confident mood aligns with your taste  |

=== Acoustic Low-Energy Listener (acoustic_chill) | mode=balanced | diversify=False ===
|   # | Title              | Artist     | Genre    |   Score | Why                                                                            |
|-----|--------------------|------------|----------|---------|--------------------------------------------------------------------------------|
|   1 | Porch Light        | Maren Holt | acoustic |   97.85 | Recommended for: acoustic genre match + calm mood aligns with your taste       |
|   2 | Quiet Hollow       | Sable Wren | acoustic |   96.15 | Recommended for: acoustic genre match + melancholy mood aligns with your taste |
|   3 | Kitchen Table Talk | Maren Holt | acoustic |   94.65 | Recommended for: acoustic genre match + tender mood aligns with your taste     |

=== High-Tempo EDM Listener (edm_rager) | mode=balanced | diversify=False ===
|   # | Title             | Artist       | Genre   |   Score | Why                                                                      |
|-----|-------------------|--------------|---------|---------|---------------------------------------------------------------------------|
|   1 | Midnight Bassline | Neon Circuit | edm     |    97.3 | Recommended for: edm genre match + euphoric mood aligns with your taste  |
|   2 | Voltage Church    | Neon Circuit | edm     |    93.5 | Recommended for: edm genre match + intense mood aligns with your taste   |
|   3 | Warehouse Lights  | Kito Waves   | edm     |    88.9 | Recommended for: edm genre match + energetic mood aligns with your taste |

=== Indie-Rock Wanderer (indie_wanderer) | mode=balanced | diversify=False ===
|   # | Title           | Artist         | Genre      |   Score | Why                                                                            |
|-----|-----------------|----------------|------------|---------|--------------------------------------------------------------------------------|
|   1 | Static Bloom    | The Aftertones | indie-rock |   96.75 | Recommended for: indie-rock genre match + hopeful mood aligns with your taste  |
|   2 | Midwest Emo Kid | Corvid Youth   | indie-rock |   94.9  | Recommended for: indie-rock genre match + yearning mood aligns with your taste |
|   3 | Rooftop Static  | The Aftertones | indie-rock |   93.6  | Recommended for: indie-rock genre match + wistful mood aligns with your taste  |
```

**Differences across profiles:** every profile's #1 recommendation is a
near-exact genre+mood match to its own preference set (scores 96.75-98.6),
which is expected since `preferred_genres` is a hard filter (score 0 if it
doesn't match) and dominates 25% of the balanced weight. The **EDM profile**
pulls almost exclusively high-energy (8-10/10), high-tempo (120-150 BPM)
tracks, while the **Acoustic profile**'s top picks all sit at energy 2-3/10
and tempo under 80 BPM -- the two lists share zero songs and would look
completely different playlists side by side, purely because `target_energy`
and `target_tempo` pull in opposite directions. The **Hip-Hop** and **Indie**
profiles land in the middle energy range (4-8/10) but separate cleanly on
genre and mood vocabulary (confident/aggressive vs. wistful/hopeful).

### Filter-bubble effect, and the fix

Run the Hip-Hop profile at `--top 4` without diversification and the #4 slot
is *still* Dre Larkin (the same artist as #1), because two of their songs
both match the genre filter:

```
--- no --diversify ---
|   4 | Rearview Mirror        | Dre Larkin | hip-hop |   61.4  | ...

--- with --diversify ---
|   4 | Chrome Heart           | Vela Sun   | pop     |   49.55 | ...
```

That's the filter bubble in miniature: a pure content-match system keeps
serving the same artist because nothing in the score function penalizes
repetition. `--diversify` swaps in a different artist (and genre) at #4 by
docking each song's effective score for every prior pick that shares its
artist/genre -- see `recommender/diversity.py` and `model_card.md` for details.

## Testing

`tests/test_recommender.py` covers dataset shape, score determinism, score
sensitivity to preferences, sorted top-N output across every profile x mode
combination, and that the diversify pass doesn't increase artist repetition.
Run with `python -m pytest tests/ -v`.

## Reflection

**What surprised me building this:** how much the *ranking weights* matter
more than the underlying similarity math. The same song can jump from #1 to
unranked just by moving 20 percentage points of weight from `genre` to
`mood` -- which is exactly why two real recommender products with access to
the same song metadata can feel completely different to use.

**Where this breaks down vs. a real system:** there's no collaborative
signal at all (no "users who liked X also liked Y"), no sequence/session
awareness (what you just skipped), and no learning over time -- every score
is recomputed from scratch from a static profile. See `model_card.md` for
the full limitations list.

**What I'd add next:** a feedback loop where skip/like events nudge
`target_energy`/`preferred_genres` incrementally, which is the actual
mechanism real systems use to build a taste profile instead of asking the
user to state one directly.

See [`model_card.md`](model_card.md) for the full model card and
[`ai_interactions.md`](ai_interactions.md) for the documented agentic AI
workflow used for the stretch features.
