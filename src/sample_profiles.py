"""
Sample user preference profiles for exercising the Recommender + RAG pipeline.
"""

CHILL_LOFI = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.3,
    "target_valence": 0.7,
    "target_danceability": 0.6,
}

HIGH_ENERGY_POP = {
    "favorite_genre": "pop",
    "favorite_mood": "intense",
    "target_energy": 0.9,
    "target_valence": 0.8,
    "target_danceability": 0.85,
}

MELLOW_ACOUSTIC = {
    "favorite_genre": "classical",
    "favorite_mood": "melancholy",
    "target_energy": 0.2,
    "target_valence": 0.3,
    "target_danceability": 0.2,
}

DANCE_PARTY = {
    "favorite_genre": "edm",
    "favorite_mood": "euphoric",
    "target_energy": 0.95,
    "target_valence": 0.9,
    "target_danceability": 0.9,
}

HIGH_ENERGY_LOFI = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.9,
    "target_valence": 0.7,
    "target_danceability": 0.6,
}

MELANCHOLY_METALHEAD = {
    "favorite_genre": "metal",
    "favorite_mood": "melancholy",
    "target_energy": 0.9,
    "target_valence": 0.1,
    "target_danceability": 0.4,
}

FURIOUS_OPERA_FAN = {
    "favorite_genre": "opera",
    "favorite_mood": "furious",
    "target_energy": 0.5,
    "target_valence": 0.5,
    "target_danceability": 0.5,
}

USER_PROFILES = {
    "Chill Lofi": CHILL_LOFI,
    "High-Energy Pop": HIGH_ENERGY_POP,
    "Mellow Acoustic": MELLOW_ACOUSTIC,
    "Dance Party": DANCE_PARTY,
    "High-Energy Lofi": HIGH_ENERGY_LOFI,
    "Melancholy Metalhead": MELANCHOLY_METALHEAD,
    "Furious Opera Fan": FURIOUS_OPERA_FAN,
}
