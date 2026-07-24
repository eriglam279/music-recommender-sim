"""Fairness/diversity re-ranking.

A pure content-based recommender tends to pile a listener's favorite artist
or genre into every top slot ("filter bubble" -- a single strong match on
genre/mood repeats across that artist's whole catalog). diversify() applies
a greedy penalty, similar in spirit to Maximal Marginal Relevance: every
time an artist or genre has already been picked, later songs from that same
artist/genre get their effective score docked before the next pick is made.
"""


def diversify(scored_songs, artist_penalty=0.15, genre_penalty=0.07):
    """Re-rank (song, score, contributions) tuples to reduce repetition.

    Greedy selection: at each step, pick the remaining song with the highest
    *effective* score (raw score minus penalties for artists/genres already
    chosen), then update the counts. Returns a new list in the same tuple
    shape, reordered.
    """
    remaining = list(scored_songs)
    picked = []
    artist_counts = {}
    genre_counts = {}

    while remaining:
        best_idx, best_effective = None, None
        for idx, (song, score, contributions) in enumerate(remaining):
            penalty = (
                artist_penalty * artist_counts.get(song["artist"], 0)
                + genre_penalty * genre_counts.get(song["genre"], 0)
            )
            effective = score - penalty * 100
            if best_effective is None or effective > best_effective:
                best_idx, best_effective = idx, effective

        song, score, contributions = remaining.pop(best_idx)
        picked.append((song, score, contributions))
        artist_counts[song["artist"]] = artist_counts.get(song["artist"], 0) + 1
        genre_counts[song["genre"]] = genre_counts.get(song["genre"], 0) + 1

    return picked
