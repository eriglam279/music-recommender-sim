"""Weighted-score recommender core.

A song's relevance to a listener is modeled as a weighted sum of per-feature
similarity scores, each normalized to [0, 1]:

    total_score = sum(weight[feature] * feature_similarity(song, user_prefs))

The *weights* are what make this "modular": swapping a weight preset changes
which features dominate the ranking without touching the similarity math
itself. That is the Strategy pattern -- see RANKING_MODES below and
ai_interactions.md for how the modes were designed.
"""

# Each preset must sum to (approximately) 1.0 so scores stay comparable
# across ranking modes and land on a 0-100 scale after multiplying by 100.
RANKING_MODES = {
    "balanced": {
        "genre": 0.25,
        "mood": 0.20,
        "energy": 0.20,
        "tempo": 0.10,
        "era": 0.05,
        "popularity": 0.05,
        "danceability": 0.10,
        "acousticness": 0.05,
    },
    "genre_first": {
        "genre": 0.45,
        "mood": 0.15,
        "energy": 0.15,
        "tempo": 0.05,
        "era": 0.05,
        "popularity": 0.05,
        "danceability": 0.05,
        "acousticness": 0.05,
    },
    "mood_first": {
        "genre": 0.15,
        "mood": 0.45,
        "energy": 0.15,
        "tempo": 0.05,
        "era": 0.05,
        "popularity": 0.05,
        "danceability": 0.05,
        "acousticness": 0.05,
    },
    "energy_similarity": {
        "genre": 0.10,
        "mood": 0.10,
        "energy": 0.40,
        "tempo": 0.15,
        "era": 0.00,
        "popularity": 0.00,
        "danceability": 0.20,
        "acousticness": 0.05,
    },
}

# Human-readable phrasing for each feature, used by explain.py so
# explanations are generated from the same source of truth as scoring.
FEATURE_LABELS = {
    "genre": "genre match",
    "mood": "mood match",
    "energy": "energy fit",
    "tempo": "tempo fit",
    "era": "era match",
    "popularity": "popularity fit",
    "danceability": "danceability fit",
    "acousticness": "acousticness fit",
}


def _closeness(value, target, span):
    """1.0 when value == target, decaying linearly to 0.0 at `span` away."""
    if target is None:
        return 0.5
    return max(0.0, 1.0 - abs(value - target) / span)


def feature_similarities(user_prefs, song):
    """Return a dict of per-feature similarity scores in [0, 1] for one song."""
    sims = {}

    preferred_genres = user_prefs.get("preferred_genres") or []
    sims["genre"] = 1.0 if song["genre"] in preferred_genres else 0.0

    preferred_moods = set(user_prefs.get("preferred_moods") or [])
    if song["mood"] in preferred_moods:
        mood_sim = 1.0
    elif preferred_moods & set(song.get("mood_tags", [])):
        mood_sim = 0.6
    else:
        mood_sim = 0.0
    sims["mood"] = mood_sim

    sims["energy"] = _closeness(song["energy"], user_prefs.get("target_energy"), 10)
    sims["tempo"] = _closeness(song["tempo"], user_prefs.get("target_tempo"), 100)
    sims["danceability"] = _closeness(
        song.get("danceability", 5), user_prefs.get("target_danceability"), 10
    )
    sims["acousticness"] = _closeness(
        song.get("acousticness", 5), user_prefs.get("target_acousticness"), 10
    )

    preferred_eras = user_prefs.get("preferred_eras") or []
    sims["era"] = 1.0 if song["era"] in preferred_eras else 0.0

    pop_pref = user_prefs.get("popularity_preference")
    popularity = song.get("popularity", 50) / 100
    if pop_pref == "mainstream":
        sims["popularity"] = popularity
    elif pop_pref == "underground":
        sims["popularity"] = 1.0 - popularity
    else:
        sims["popularity"] = 0.5

    return sims


def score_song(user_prefs, song, mode="balanced"):
    """Return (total_score_0_to_100, per_feature_contributions) for one song.

    per_feature_contributions maps feature name -> weight * similarity, so
    the caller (explain.py) can see which features actually drove the score.
    """
    weights = RANKING_MODES.get(mode, RANKING_MODES["balanced"])
    sims = feature_similarities(user_prefs, song)

    contributions = {feat: weights.get(feat, 0.0) * sims[feat] for feat in sims}
    total = sum(contributions.values()) * 100
    return round(total, 2), contributions
