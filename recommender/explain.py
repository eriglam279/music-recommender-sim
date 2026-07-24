"""Turns a song's per-feature score contributions into a plain-English reason."""

from .scoring import FEATURE_LABELS


def explain_song(song, contributions, top_n=2):
    """Build a short "why this was recommended" string from the top contributors.

    Only features that actually mattered (non-zero contribution) are eligible,
    so the explanation never claims credit for a feature the song didn't match.
    """
    ranked = sorted(contributions.items(), key=lambda kv: kv[1], reverse=True)
    ranked = [(feat, val) for feat, val in ranked if val > 0.0]

    if not ranked:
        return f"'{song['title']}' filled out the list but matched none of your stated preferences."

    reasons = []
    for feat, _ in ranked[:top_n]:
        if feat == "genre":
            reasons.append(f"{song['genre']} genre match")
        elif feat == "mood":
            reasons.append(f"{song['mood']} mood aligns with your taste")
        elif feat == "energy":
            reasons.append(f"energy level {song['energy']}/10 fits your target")
        elif feat == "tempo":
            reasons.append(f"tempo of {song['tempo']} BPM is close to your preference")
        elif feat == "era":
            reasons.append(f"{song['era']} era match")
        elif feat == "popularity":
            reasons.append(f"popularity ({song.get('popularity', 0)}/100) matches your mainstream/underground preference")
        elif feat == "danceability":
            reasons.append(f"danceability {song.get('danceability', 0)}/10 matches your preference")
        elif feat == "acousticness":
            reasons.append(f"acousticness {song.get('acousticness', 0)}/10 matches your preference")
        else:
            reasons.append(FEATURE_LABELS.get(feat, feat))

    return "Recommended for: " + " + ".join(reasons)
