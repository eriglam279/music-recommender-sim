# AI Interactions Log

This project was built with Claude (Claude Code) as an agentic coding
assistant. This log documents the prompts that drove the stretch features,
what the agent generated, and how the output was manually verified.

## 1. Additional song attributes via agentic AI

**Prompt (paraphrased):** "Add 5+ additional meaningful attributes to the
song dataset beyond genre/mood/energy/tempo/era, and update the scoring
logic so they actually affect the score, not just sit unused in the data."

**What the agent generated:**

- Five new per-song fields: `popularity` (0-100), `release_decade` (int),
  `mood_tags` (list of finer-grained mood descriptors beyond the single
  primary `mood`), `danceability` (0-10), `acousticness` (0-10).
- New `user_prefs` keys to match: `popularity_preference`
  (`"mainstream"` / `"underground"` / `None`), `target_danceability`,
  `target_acousticness`.
- New similarity functions in `feature_similarities()`
  (`recommender/scoring.py`): linear closeness for danceability/acousticness
  (same shape as the existing energy/tempo closeness), and a
  preference-relative popularity score (rewards high popularity for
  "mainstream" listeners, low popularity for "underground" listeners).
- Extended `mood` scoring to check `mood_tags` for partial credit (0.6) when
  the primary `mood` string doesn't match exactly but a secondary tag does
  — this was the agent's own addition to make the extra `mood_tags` field
  functionally meaningful rather than decorative.
- Updated all four `RANKING_MODES` weight presets to include the new
  features so they sum to ~1.0 again.

**Manual verification:** ran `python main.py --top 5` before and after the
change and confirmed (a) every song still returns a numeric score with no
exceptions, (b) scores for `mainstream`-preference profiles favor
high-`popularity` songs and vice versa for `underground` profiles, and (c) the
`test_recommend_songs_works_for_every_profile_and_mode` test asserts every
score stays within `[0, 100]` across all profiles x modes with the new
weights included.

## 2. Multiple ranking modes / design pattern

**Prompt (paraphrased):** "Support at least two ranking strategies (e.g.
genre-first vs. mood-first) that a user can switch between, using a proper
design pattern rather than duplicating the scoring function."

**Design pattern chosen:** **Strategy pattern**, implemented as data rather
than subclasses — `RANKING_MODES` in `recommender/scoring.py` is a dict of
named weight presets, and `score_song(user_prefs, song, mode=...)` is the
single scoring algorithm parameterized by whichever preset is selected. A
class-based Strategy (one class per mode with a `.score()` method) was
considered, but a weight-dict-per-mode was simpler and easier to eyeball
correctness of (the weights are the entire behavior difference between
modes, visible at a glance, versus scattering logic across subclasses for
what is fundamentally a set of numbers). The agent proposed this simplified
data-driven Strategy variant directly.

**What was generated:** the `RANKING_MODES` dict with 4 presets
(`balanced`, `genre_first`, `mood_first`, `energy_similarity`), and a
`--mode` CLI flag in `main.py` that passes straight through to
`recommend_songs(..., mode=args.mode)`.

**Manual verification:** ran the same profile (`hiphop_head`) through all
four modes and confirmed the ranking and the printed explanation both change
in the direction implied by the mode's dominant weight — e.g. under
`mood_first` the explanation text reorders to name the mood match before the
genre match for the same song, confirming the weight change actually flows
through to both scoring and the explanation, not just a cosmetic label.

## 3. Diversity / fairness component

**Prompt (paraphrased):** "Add logic that penalizes repetition (e.g. an
artist penalty) so the recommender doesn't just repeat one artist across
every slot, and document how it improves fairness in the model card."

**What was generated:** `recommender/diversity.py`'s `diversify()` function
— a greedy re-ranking pass (conceptually similar to Maximal Marginal
Relevance) that tracks how many times each artist and genre has already been
selected and subtracts a proportional penalty from remaining candidates'
scores before picking the next slot.

**Manual verification:** confirmed via the dataset's two Dre Larkin hip-hop
songs — running the Hip-Hop Head profile at `--top 4` without `--diversify`
put a second Dre Larkin song in the #4 slot; with `--diversify` that slot
was replaced by a different artist/genre entirely (see README for the exact
before/after table). Also added
`test_diversify_reduces_repeated_artists_in_top_n` to pytest to make this a
regression-checked guarantee rather than a one-off manual check.

## 4. Visual output table

**Prompt (paraphrased):** "Use `tabulate` (or similarly readable formatting)
to present results with the generated reasons, instead of raw print
statements."

**What was generated:** `main.py` builds a list of rows (`#`, title, artist,
genre, score, why) and renders them with `tabulate(..., tablefmt="github")`,
which also makes the README output directly copy-pasteable as GitHub-flavored
markdown tables.

**Manual verification:** ran `python main.py` and visually confirmed column
alignment and that the `Why` column isn't truncated for the longest
explanation strings in the dataset.
