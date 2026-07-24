"""Top-level recommendation function that ties scoring + explanations together."""

from .scoring import score_song
from .explain import explain_song
from .diversity import diversify


def recommend_songs(user_prefs, songs, mode="balanced", top_n=5, diversify_results=False):
    """Return the top_n songs for user_prefs as a list of result dicts:

        {"song": <song dict>, "score": <0-100 float>, "explanation": <str>}

    mode selects a ranking strategy (see scoring.RANKING_MODES).
    diversify_results=True applies an artist/genre repetition penalty
    (diversity.diversify) before truncating to top_n.
    """
    scored = []
    for song in songs:
        score, contributions = score_song(user_prefs, song, mode=mode)
        scored.append((song, score, contributions))

    if diversify_results:
        scored = diversify(scored)
    else:
        scored.sort(key=lambda triple: triple[1], reverse=True)

    results = []
    for song, score, contributions in scored[:top_n]:
        results.append(
            {
                "song": song,
                "score": score,
                "explanation": explain_song(song, contributions),
            }
        )
    return results
