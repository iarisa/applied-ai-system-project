"""
Command line runner for the Music Recommender + RAG explanation pipeline.

Pipeline: Recommender -> Retriever -> Agent (LLM) -> Evaluator, retrying the
Agent when the Evaluator rejects its output and falling back to raw scores
once retries are exhausted (or the Agent is unavailable with no
GEMINI_API_KEY), per diagrams/architecture.mmd.
"""

from dotenv import load_dotenv
load_dotenv()

from .recommender import load_songs, recommend_songs
from .retriever import load_song_background, Retriever
from .llm_client import GeminiClient
from .agent import Agent
from .evaluator import Evaluator
from .sample_profiles import USER_PROFILES
from .progress import spinner

# Initial attempt plus this many retries before falling back to raw scores.
MAX_AGENT_ATTEMPTS = 2


def try_create_agent():
    """
    Tries to create an Agent backed by Gemini.
    Returns (agent, has_llm: bool).
    """
    try:
        client = GeminiClient()
        return Agent(client), True
    except RuntimeError as exc:
        print("Warning: Agent explanations are disabled.")
        print(f"Reason: {exc}")
        print("Falling back to raw scores only.\n")
        return None, False


def print_raw_scores(recommendations) -> None:
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']} - Score: {score:.2f}")
        for reason in explanation.split(", "):
            print(f"     - {reason}")
        print()


def choose_user_profile(profile_names):
    """
    Prompts the user to pick a sample user preference profile by number.
    Returns the chosen profile name, or None if the user chooses to quit.
    """
    print("Choose a user preference profile:")
    for i, name in enumerate(profile_names, start=1):
        print(f"  {i}) {name}")
    print("  q) Quit")

    while True:
        choice = input("Enter choice: ").strip().lower()

        if choice == "q":
            return None

        if choice.isdigit() and 1 <= int(choice) <= len(profile_names):
            return profile_names[int(choice) - 1]

        print(f"Invalid choice. Please enter a number between 1 and {len(profile_names)}, or q to quit.\n")


def print_agent_explanation(explanation: str) -> None:
    """
    Prints the Agent's numbered explanation with a blank line between songs
    and without literal "**" markers, since a plain terminal won't render
    markdown bold.
    """
    for line in explanation.strip().split("\n"):
        line = line.strip()
        if line:
            print(line.replace("**", ""))
            print()


def get_evaluated_explanation(agent, evaluator, recommendations, background_by_id, profile):
    """
    Calls the Agent, checks its output with the Evaluator, and retries on
    failure up to MAX_AGENT_ATTEMPTS before giving up.

    Returns the accepted {"explanation", "claims"} payload, or None if every
    attempt failed (caller should fall back to raw scores).
    """
    for attempt in range(1, MAX_AGENT_ATTEMPTS + 1):
        with spinner(f"Generating explanation (attempt {attempt}/{MAX_AGENT_ATTEMPTS})..."):
            try:
                result = agent.generate_explanation(recommendations, background_by_id, profile)
            except ValueError as exc:
                print(f"Attempt {attempt}: Agent did not return valid JSON ({exc}).\n")
                continue

        evaluation = evaluator.evaluate(result, recommendations)
        if evaluation.passed:
            return result

        print(f"Attempt {attempt}: Evaluator rejected the explanation:")
        for reason in evaluation.reasons:
            print(f"  - {reason}")
        print()

    return None


def main() -> None:
    songs = load_songs("data/songs.csv")

    background = load_song_background("data/song_background.json")
    retriever = Retriever(background)
    agent, has_llm = try_create_agent()
    evaluator = Evaluator()

    profile_names = list(USER_PROFILES.keys())

    while True:
        profile_name = choose_user_profile(profile_names)
        if profile_name is None:
            print("\nGoodbye.")
            break

        profile = USER_PROFILES[profile_name]
        recommendations = recommend_songs(profile, songs, k=5)

        print(f"\n=== {profile_name} ===")
        print("\nTop recommendations:\n")

        if has_llm:
            song_ids = [song["id"] for song, _, _ in recommendations]
            background_by_id = retriever.get_background(song_ids)
            result = get_evaluated_explanation(
                agent, evaluator, recommendations, background_by_id, profile
            )
            if result is not None:
                print_agent_explanation(result["explanation"])
            else:
                print("Retries exhausted. Falling back to raw scores.\n")
                print_raw_scores(recommendations)
        else:
            print_raw_scores(recommendations)

        print()


if __name__ == "__main__":
    main()
