"""CLI demo for the music recommender simulation.

Usage:
    python main.py                          # every profile, balanced mode
    python main.py --profile edm_rager       # one profile, balanced mode
    python main.py --mode mood_first         # every profile, one ranking mode
    python main.py --diversify               # apply the artist/genre fairness penalty
    python main.py --list-profiles
    python main.py --list-modes
"""

import argparse

from tabulate import tabulate

from recommender.songs import load_songs
from recommender.profiles import USER_PROFILES
from recommender.recommend import recommend_songs
from recommender.scoring import RANKING_MODES


def print_recommendations(profile_key, profile, songs, mode, diversify_results, top_n):
    print(f"\n=== {profile['label']} ({profile_key}) | mode={mode} | diversify={diversify_results} ===")
    results = recommend_songs(
        profile, songs, mode=mode, top_n=top_n, diversify_results=diversify_results
    )
    rows = [
        [
            i + 1,
            r["song"]["title"],
            r["song"]["artist"],
            r["song"]["genre"],
            r["score"],
            r["explanation"],
        ]
        for i, r in enumerate(results)
    ]
    print(
        tabulate(
            rows,
            headers=["#", "Title", "Artist", "Genre", "Score", "Why"],
            tablefmt="github",
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Music recommender simulation")
    parser.add_argument("--profile", choices=list(USER_PROFILES), help="run a single profile")
    parser.add_argument(
        "--mode", choices=list(RANKING_MODES), default="balanced", help="ranking strategy"
    )
    parser.add_argument(
        "--diversify", action="store_true", help="apply artist/genre fairness penalty"
    )
    parser.add_argument("--top", type=int, default=5, help="how many songs to show")
    parser.add_argument("--list-profiles", action="store_true")
    parser.add_argument("--list-modes", action="store_true")
    args = parser.parse_args()

    if args.list_profiles:
        for key, profile in USER_PROFILES.items():
            print(f"{key}: {profile['label']}")
        return

    if args.list_modes:
        for key in RANKING_MODES:
            print(key)
        return

    songs = load_songs()
    profiles = (
        {args.profile: USER_PROFILES[args.profile]} if args.profile else USER_PROFILES
    )

    for key, profile in profiles.items():
        print_recommendations(key, profile, songs, args.mode, args.diversify, args.top)


if __name__ == "__main__":
    main()
