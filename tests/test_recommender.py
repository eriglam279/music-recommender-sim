import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from recommender.songs import load_songs
from recommender.profiles import USER_PROFILES
from recommender.scoring import score_song, RANKING_MODES
from recommender.recommend import recommend_songs
from recommender.diversity import diversify


def test_dataset_size_and_shape():
    songs = load_songs()
    assert len(songs) >= 15
    required_keys = {"title", "artist", "genre", "mood", "energy", "tempo", "era"}
    for song in songs:
        assert required_keys.issubset(song.keys())


def test_score_song_is_numeric_and_deterministic():
    songs = load_songs()
    profile = USER_PROFILES["hiphop_head"]
    song = songs[0]
    score1, _ = score_song(profile, song)
    score2, _ = score_song(profile, song)
    assert isinstance(score1, float)
    assert score1 == score2


def test_score_song_rewards_matching_energy_preference():
    songs = load_songs()
    high_energy_profile = {"target_energy": 10, "target_tempo": None, "preferred_genres": []}
    low_energy_profile = {"target_energy": 0, "target_tempo": None, "preferred_genres": []}
    loud_song = next(s for s in songs if s["title"] == "Voltage Church")  # energy 10

    high_score, _ = score_song(high_energy_profile, loud_song, mode="energy_similarity")
    low_score, _ = score_song(low_energy_profile, loud_song, mode="energy_similarity")
    assert high_score > low_score


def test_recommend_songs_returns_sorted_top_n():
    songs = load_songs()
    profile = USER_PROFILES["edm_rager"]
    results = recommend_songs(profile, songs, top_n=3)
    assert len(results) == 3
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_songs_works_for_every_profile_and_mode():
    songs = load_songs()
    for profile in USER_PROFILES.values():
        for mode in RANKING_MODES:
            results = recommend_songs(profile, songs, mode=mode, top_n=5)
            assert len(results) == 5
            for r in results:
                assert 0 <= r["score"] <= 100
                assert r["explanation"]


def test_diversify_reduces_repeated_artists_in_top_n():
    songs = load_songs()
    profile = USER_PROFILES["hiphop_head"]  # Dre Larkin has 2 hip-hop songs in the set
    plain = recommend_songs(profile, songs, top_n=4, diversify_results=False)
    diversified = recommend_songs(profile, songs, top_n=4, diversify_results=True)

    def artist_repeats(results):
        artists = [r["song"]["artist"] for r in results]
        return len(artists) - len(set(artists))

    assert artist_repeats(diversified) <= artist_repeats(plain)


def test_explanations_reference_actual_song_attributes():
    songs = load_songs()
    profile = USER_PROFILES["acoustic_chill"]
    results = recommend_songs(profile, songs, top_n=3)
    for r in results:
        assert "Recommended for:" in r["explanation"]
        assert r["song"]["genre"] in r["explanation"] or r["song"]["mood"] in r["explanation"]
