"""
Command line runner for the Music Recommender + RAG explanation pipeline.

Pipeline: Recommender -> Retriever -> Agent (LLM), falling back to raw
scores when the Agent is unavailable (no GEMINI_API_KEY) or fails to
produce a valid response. This fallback is a placeholder for the
Evaluator-driven pass/fail/retry logic described in notes.md, which isn't
implemented yet.
"""

from dotenv import load_dotenv
load_dotenv()

from .recommender import load_songs, recommend_songs
from .retriever import load_song_background, Retriever
from .llm_client import GeminiClient
from .agent import Agent
from .sample_profiles import USER_PROFILES


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
        print(f"{rank}. {song['title']} by {song['artist']} — Score: {score:.2f}")
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


def main() -> None:
    songs = load_songs("data/songs.csv")

    background = load_song_background("data/song_background.json")
    retriever = Retriever(background)
    agent, has_llm = try_create_agent()

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
            try:
                result = agent.generate_explanation(recommendations, background_by_id, profile)
                print_agent_explanation(result["explanation"])
            except ValueError as exc:
                print(f"Agent failed to produce a valid explanation ({exc}).")
                print("Falling back to raw scores.\n")
                print_raw_scores(recommendations)
        else:
            print_raw_scores(recommendations)

        print()


if __name__ == "__main__":
    main()
