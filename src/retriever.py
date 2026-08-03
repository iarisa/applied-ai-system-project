import json
from typing import Dict, List, Optional


def load_song_background(json_path: str) -> Dict[int, Dict[str, str]]:
    """Reads the song background knowledge base into a dict keyed by song id (int)."""
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)
    return {int(song_id): background for song_id, background in raw.items()}


class Retriever:
    """
    Looks up background info for a known set of song ids (the Recommender's
    top-k output). No scoring/ranking is needed here since the Recommender
    already narrowed the candidates down.
    """
    def __init__(self, background: Dict[int, Dict[str, str]]):
        self.background = background

    def get_background(self, song_ids: List[int]) -> Dict[int, Optional[Dict[str, str]]]:
        """
        Returns background info for each requested song id.
        Missing ids map to None rather than raising, so a single KB gap
        doesn't block the Agent from explaining the rest of the set.
        """
        return {song_id: self.background.get(song_id) for song_id in song_ids}
