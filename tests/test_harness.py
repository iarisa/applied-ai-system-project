"""
Test harness / evaluation script for the full Recommender -> Retriever ->
Agent -> Evaluator pipeline (see notes.md, diagrams/architecture.mmd).

Runs every sample profile in sample_profiles.USER_PROFILES through:
  1. Pipeline checks (Recommender + Retriever) - deterministic, no LLM needed.
  2. Agent + Evaluator checks - calls the real Gemini API and mirrors the
     retry-then-fallback loop in src.main, so this makes up to
     MAX_AGENT_ATTEMPTS live API calls per profile.

Prints a pass/fail summary per profile plus an overall total, and exits with
a non-zero status if anything failed (so it can be used as a CI-style gate).

Run from the project root:
    python -m tests.test_harness
"""

import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.recommender import load_songs, recommend_songs
from src.retriever import load_song_background, Retriever
from src.evaluator import Evaluator
from src.sample_profiles import USER_PROFILES
from src.main import try_create_agent, MAX_AGENT_ATTEMPTS
from src.progress import spinner

SONGS_PATH = "data/songs.csv"
BACKGROUND_PATH = "data/song_background.json"


@dataclass
class ProfileResult:
    name: str
    pipeline_ok: bool
    pipeline_reasons: List[str]
    agent_passed: Optional[bool] = None  # None when the Agent/LLM was unavailable
    attempts_used: int = 0
    agent_reasons: List[str] = field(default_factory=list)


def check_pipeline(profile: Dict, songs: List[Dict], background: Dict) -> Tuple[bool, List[str]]:
    """Deterministic checks on the Recommender + Retriever that don't need an LLM."""
    reasons = []
    recommendations = recommend_songs(profile, songs, k=5)

    if len(recommendations) != 5:
        reasons.append(f"Expected 5 recommendations, got {len(recommendations)}.")

    titles = [song["title"] for song, _, _ in recommendations]
    if len(set(titles)) != len(titles):
        reasons.append(f"Duplicate songs recommended: {titles}.")

    scores = [score for _, score, _ in recommendations]
    if scores != sorted(scores, reverse=True):
        reasons.append(f"Recommendations are not sorted by score descending: {scores}.")

    song_ids = [song["id"] for song, _, _ in recommendations]
    background_by_id = Retriever(background).get_background(song_ids)
    if set(background_by_id.keys()) != set(song_ids):
        reasons.append("Retriever did not return an entry for every requested song id.")

    return not reasons, reasons


def check_agent(agent, evaluator: Evaluator, profile: Dict, songs: List[Dict], background: Dict) -> Tuple[bool, int, List[str]]:
    """
    Runs the Agent + Evaluator retry loop (mirrors get_evaluated_explanation in
    src.main) and reports whether it passed, how many attempts it took, and
    the Evaluator's rejection reasons on the final attempt if it didn't.
    """
    recommendations = recommend_songs(profile, songs, k=5)
    song_ids = [song["id"] for song, _, _ in recommendations]
    background_by_id = Retriever(background).get_background(song_ids)

    last_reasons = []
    for attempt in range(1, MAX_AGENT_ATTEMPTS + 1):
        with spinner(f"  Calling Agent (attempt {attempt}/{MAX_AGENT_ATTEMPTS})..."):
            try:
                result = agent.generate_explanation(recommendations, background_by_id, profile)
            except ValueError as exc:
                last_reasons = [f"Agent did not return valid JSON ({exc})."]
                continue

            evaluation = evaluator.evaluate(result, recommendations)
        if evaluation.passed:
            return True, attempt, []
        last_reasons = evaluation.reasons

    return False, MAX_AGENT_ATTEMPTS, last_reasons


def confidence_label(passed: Optional[bool], attempts_used: int) -> str:
    if passed is None:
        return "n/a (no LLM)"
    if not passed:
        return "low (fell back to raw scores)"
    return "high (passed on 1st try)" if attempts_used == 1 else "medium (needed a retry)"


def print_header(has_llm: bool) -> None:
    print("=" * 70)
    print("TEST HARNESS: Recommender -> Retriever -> Agent -> Evaluator")
    print("=" * 70)
    if not has_llm:
        print("(No GEMINI_API_KEY - Agent/Evaluator checks skipped, shown as n/a.)")


def print_profile_result(r: ProfileResult) -> None:
    pipeline_status = "PASS" if r.pipeline_ok else "FAIL"
    print(f"\n[{pipeline_status}] {r.name}")
    print(f"    Pipeline (Recommender/Retriever): {pipeline_status}")
    for reason in r.pipeline_reasons:
        print(f"      - {reason}")

    if r.agent_passed is None:
        print("    Agent/Evaluator: n/a (no LLM)")
    else:
        agent_status = "PASS" if r.agent_passed else "FAIL"
        print(
            f"    Agent/Evaluator: {agent_status} "
            f"(attempts used: {r.attempts_used}/{MAX_AGENT_ATTEMPTS}, "
            f"confidence: {confidence_label(r.agent_passed, r.attempts_used)})"
        )
        for reason in r.agent_reasons:
            print(f"      - {reason}")


def print_totals(results: List[ProfileResult], has_llm: bool) -> None:
    total = len(results)
    pipeline_passed = sum(r.pipeline_ok for r in results)
    print("\n" + "-" * 70)
    print(f"Pipeline checks:        {pipeline_passed}/{total} passed")
    if has_llm:
        agent_passed_count = sum(1 for r in results if r.agent_passed)
        print(f"Agent/Evaluator checks: {agent_passed_count}/{total} passed")
    print("-" * 70)


def run() -> int:
    songs = load_songs(SONGS_PATH)
    background = load_song_background(BACKGROUND_PATH)
    agent, has_llm = try_create_agent()
    evaluator = Evaluator()

    print_header(has_llm)

    profile_names = list(USER_PROFILES.items())
    results: List[ProfileResult] = []
    for i, (name, profile) in enumerate(profile_names, start=1):
        print(f"\n>>> [{i}/{len(profile_names)}] Testing profile: {name}", flush=True)

        pipeline_ok, pipeline_reasons = check_pipeline(profile, songs, background)

        agent_passed, attempts_used, agent_reasons = None, 0, []
        if has_llm:
            agent_passed, attempts_used, agent_reasons = check_agent(
                agent, evaluator, profile, songs, background
            )

        result = ProfileResult(
            name=name,
            pipeline_ok=pipeline_ok,
            pipeline_reasons=pipeline_reasons,
            agent_passed=agent_passed,
            attempts_used=attempts_used,
            agent_reasons=agent_reasons,
        )
        results.append(result)
        print_profile_result(result)

    print_totals(results, has_llm)

    all_ok = all(r.pipeline_ok and r.agent_passed is not False for r in results)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(run())
