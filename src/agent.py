"""
Agent responsible for generating a user-friendly explanation of the top-5
song recommendations, grounded in the Retriever's song/artist background.

Returns a structured JSON payload (explanation + per-song attribute claims)
so a future Evaluator can check both "are all 5 songs mentioned" and
"are the attribute claims actually accurate" as simple data comparisons,
rather than parsing free text.
"""

import json
import re
from typing import Dict, List, Optional, Tuple

# Attributes are 0-1 scores in songs.csv. These bands let the Agent describe
# them consistently ("high"/"medium"/"low") so claims stay checkable against
# the real numbers rather than the model inventing its own thresholds.
LEVEL_BANDS = "high (>= 0.7), medium (0.35-0.7), low (<= 0.35)"

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _strip_code_fences(text: str) -> str:
    return _JSON_FENCE_RE.sub("", text.strip()).strip()


def _format_song_block(
    song: Dict, score: float, reasons: str, background: Optional[Dict[str, str]]
) -> str:
    lines = [
        f"Song: {song['title']}",
        f"Artist: {song['artist']}",
        f"Genre: {song['genre']} | Mood: {song['mood']}",
        f"Attributes: energy={song['energy']:.2f}, tempo_bpm={song['tempo_bpm']:.0f}, "
        f"valence={song['valence']:.2f}, danceability={song['danceability']:.2f}, "
        f"acousticness={song['acousticness']:.2f}",
        f"Match score: {score:.2f} ({reasons})",
    ]
    if background:
        lines.append(f"Artist background: {background.get('artist_bio', '')}")
        lines.append(f"Song background: {background.get('song_notes', '')}")
    else:
        lines.append("Artist/song background: not available")
    return "\n".join(lines)


def _format_preferences_block(user_prefs: Dict) -> str:
    return "\n".join(
        [
            f"Favorite genre: {user_prefs.get('favorite_genre', 'n/a')}",
            f"Favorite mood: {user_prefs.get('favorite_mood', 'n/a')}",
            f"Target energy: {user_prefs.get('target_energy', 'n/a')}",
            f"Target valence: {user_prefs.get('target_valence', 'n/a')}",
            f"Target danceability: {user_prefs.get('target_danceability', 'n/a')}",
        ]
    )


def build_prompt(
    recommendations: List[Tuple[Dict, float, str]],
    background_by_id: Dict[int, Optional[Dict[str, str]]],
    user_prefs: Dict,
) -> str:
    song_blocks = [
        _format_song_block(song, score, reasons, background_by_id.get(song["id"]))
        for song, score, reasons in recommendations
    ]
    songs_text = "\n\n".join(song_blocks)
    expected_titles = ", ".join(song["title"] for song, _, _ in recommendations)
    preferences_text = _format_preferences_block(user_prefs)

    return f"""You are a warm, well-listened music curator - the kind of friend who
always has a good story about a song. Talk to the listener directly, in a
friendly, conversational voice, about why each of the following 5 songs was
picked for them.

Listener's stated preferences:
{preferences_text}

{songs_text}

Attribute level bands (use these, don't invent your own): {LEVEL_BANDS}

Respond with ONLY valid JSON (no markdown fences, no extra text) in this exact shape:
{{
  "explanation": "1. **<exact song title>** - <1-2 sentence explanation>\\n2. ...",
  "claims": [
    {{"song": "<exact song title>", "attribute": "energy|valence|danceability|acousticness", "level": "high|medium|low"}}
  ]
}}

The most important rule: explain the WHY, not just the WHAT. Every item must
explicitly connect the song back to the listener's stated preferences above
(their favorite genre/mood, or their target energy/valence/danceability) -
not just describe facts about the artist or song in isolation. Background
trivia should support that connection, not replace it.

Good example (ties the song directly to what the listener asked for):
"1. Gym Hero - I knew you would love this pop track by Max Pulse because it
hits every mark for an intense workout with its punchy drums, shouted gang
vocals, and relentless four-on-the-floor beat designed to keep pace with
your training."

Bad example (only describes the artist/song, never says why it matches the
listener):
"4. Spacewalk Thoughts - Orbit Bloom created this eight-minute meditation
using a single sustained drone on modular synthesizers that shifts almost
imperceptibly over time."

Rules:
- The explanation must be a numbered list of exactly 5 items, one per song, each
  starting with the song's exact title from the data above in bold.
- Include at least one claim per song, and every claim's level must match the
  attribute bands given above based on the actual attribute value provided.
- Do not recommend or mention any song not in the list above.
- Ground everything you say in the attributes, match reasons, and background
  info given above - never invent a fact that isn't in that data. Within that
  constraint, use your own words: do not copy sentences or phrases straight
  out of the artist/song background text. Treat it as trivia you already
  know and weave it naturally into the explanation, rather than quoting it.
- Vary your sentence openings and structure across the 5 items so they don't
  read like a templated report (e.g. don't start every entry with "This
  track received a match score of..."). Each one should feel like its own
  personal recommendation.
- You do not need to state the literal numeric match score. Describe the fit
  qualitatively (mood, energy, vibe) in plain language, and only reference a
  number if it makes the sentence read more naturally.
- Use plain ASCII punctuation only, throughout the entire explanation
  (hyphens, commas, periods). Do not use em dashes, en dashes, or any other
  special characters, anywhere in the text.
- Do not recompute, restate, or second-guess a score or attribute value
  within the explanation.
- Expected songs (exact titles, order not required): {expected_titles}
"""


class Agent:
    """
    Generates the natural-language + structured-claims explanation for the
    Recommender's top-k output, using the Retriever's background info.
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate_explanation(
        self,
        recommendations: List[Tuple[Dict, float, str]],
        background_by_id: Dict[int, Optional[Dict[str, str]]],
        user_prefs: Dict,
    ) -> Dict:
        """
        recommendations: list of (song_dict, score, reasons_str), as returned
                          by recommender.recommend_songs
        background_by_id: dict of {song_id: background_dict_or_None}, as
                           returned by Retriever.get_background
        user_prefs: the listener's preference dict (favorite_genre,
                    favorite_mood, target_energy, target_valence,
                    target_danceability), so the Agent can explain *why* a
                    song fits instead of just describing it

        Returns {"explanation": str, "claims": list[dict]}.
        Raises ValueError if the LLM response isn't valid JSON in the expected shape.
        """
        prompt = build_prompt(recommendations, background_by_id, user_prefs)
        raw = self.llm_client.generate(prompt)

        try:
            payload = json.loads(_strip_code_fences(raw))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Agent response was not valid JSON: {raw!r}") from exc

        if "explanation" not in payload or "claims" not in payload:
            raise ValueError(f"Agent response missing required keys: {payload!r}")

        return payload
