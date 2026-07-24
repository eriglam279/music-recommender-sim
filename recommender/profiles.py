"""Example listener "taste profiles" used to demonstrate the recommender.

A profile is just the user_prefs dict that score_song/recommend_songs expect.
Nothing here is required by the library -- these are sample data for main.py
and the README/model card write-ups.
"""

USER_PROFILES = {
    "hiphop_head": {
        "label": "Hip-Hop Head",
        "preferred_genres": ["hip-hop"],
        "preferred_moods": ["confident", "aggressive", "gritty"],
        "target_energy": 7,
        "target_tempo": 100,
        "preferred_eras": ["2020s"],
        "popularity_preference": "mainstream",
        "target_danceability": 7,
        "target_acousticness": 2,
    },
    "acoustic_chill": {
        "label": "Acoustic Low-Energy Listener",
        "preferred_genres": ["acoustic"],
        "preferred_moods": ["calm", "tender", "melancholy"],
        "target_energy": 2,
        "target_tempo": 75,
        "preferred_eras": ["2020s", "2010s"],
        "popularity_preference": "underground",
        "target_danceability": 2,
        "target_acousticness": 9,
    },
    "edm_rager": {
        "label": "High-Tempo EDM Listener",
        "preferred_genres": ["edm"],
        "preferred_moods": ["euphoric", "energetic", "intense"],
        "target_energy": 9,
        "target_tempo": 130,
        "preferred_eras": ["2020s"],
        "popularity_preference": None,
        "target_danceability": 9,
        "target_acousticness": 1,
    },
    "indie_wanderer": {
        "label": "Indie-Rock Wanderer",
        "preferred_genres": ["indie-rock"],
        "preferred_moods": ["wistful", "hopeful", "yearning"],
        "target_energy": 6,
        "target_tempo": 120,
        "preferred_eras": ["2010s", "2020s"],
        "popularity_preference": "underground",
        "target_danceability": 5,
        "target_acousticness": 4,
    },
}
