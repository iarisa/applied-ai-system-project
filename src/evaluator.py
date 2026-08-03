"""
Evaluator for the Agent's generated explanation, per the checks described in
notes.md / diagrams/architecture.mmd:
- the explanation mentions exactly the 5 expected songs
- every attribute claim is accurate (matches the song's real attribute value)
- basic format checks (exactly 5 items, valid attribute/level names, every
  song has at least one claim)

The Recommender -> Retriever -> Agent -> Evaluator flow uses this to decide
whether to accept the Agent's output, retry, or fall back to raw scores.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .agent import band_for_value

VALID_ATTRIBUTES = {"energy", "valence", "danceability", "acousticness"}
VALID_LEVELS = {"high", "medium", "low"}

_LIST_ITEM_RE = re.compile(r"^\s*\d+\.\s*(.+)$")


def extract_titles(explanation: str) -> List[str]:
    """
    Pulls the song title out of each numbered line of the explanation, e.g.
    "1. **Gym Hero** - ..." or "1. Gym Hero - ..." both yield "Gym Hero".
    """
    titles = []
    for line in explanation.strip().split("\n"):
        match = _LIST_ITEM_RE.match(line.strip())
        if not match:
            continue
        title_part = match.group(1).split(" - ", 1)[0]
        titles.append(title_part.strip().strip("*").strip())
    return titles


@dataclass
class EvaluationResult:
    passed: bool
    reasons: List[str] = field(default_factory=list)


class Evaluator:
    """
    Checks an Agent-generated {"explanation", "claims"} payload against the
    Recommender's actual top-k output.
    """

    def evaluate(
        self,
        result: Dict,
        recommendations: List[Tuple[Dict, float, str]],
    ) -> EvaluationResult:
        reasons = []

        songs_by_title = {song["title"]: song for song, _, _ in recommendations}
        expected_titles = set(songs_by_title.keys())

        explanation = result.get("explanation", "")
        claims = result.get("claims", [])

        # 1. The explanation must contain exactly the 5 expected songs.
        found_titles = extract_titles(explanation)
        if len(found_titles) != 5:
            reasons.append(f"Expected exactly 5 numbered items, found {len(found_titles)}.")

        found_set = set(found_titles)
        if found_set != expected_titles:
            missing = expected_titles - found_set
            extra = found_set - expected_titles
            detail = []
            if missing:
                detail.append(f"missing {sorted(missing)}")
            if extra:
                detail.append(f"unexpected {sorted(extra)}")
            reasons.append(f"Song titles did not match expected set: {'; '.join(detail)}.")

        # 2. Format + accuracy checks on the structured claims.
        if not claims:
            reasons.append("No attribute claims were provided.")

        claimed_songs = set()
        for claim in claims:
            song_title = claim.get("song")
            attribute = claim.get("attribute")
            level = claim.get("level")

            if song_title not in songs_by_title:
                reasons.append(f"Claim references unknown song: {claim!r}.")
                continue
            claimed_songs.add(song_title)

            if attribute not in VALID_ATTRIBUTES:
                reasons.append(f"Claim has invalid attribute: {claim!r}.")
                continue

            if level not in VALID_LEVELS:
                reasons.append(f"Claim has invalid level: {claim!r}.")
                continue

            actual_value = songs_by_title[song_title][attribute]
            expected_level = band_for_value(actual_value)
            if level != expected_level:
                reasons.append(
                    f"Inaccurate claim: {song_title} {attribute}={actual_value:.2f} "
                    f"is '{expected_level}', but claim said '{level}'."
                )

        missing_claims = expected_titles - claimed_songs
        if missing_claims:
            reasons.append(f"No claims were made for: {sorted(missing_claims)}.")

        return EvaluationResult(passed=not reasons, reasons=reasons)
