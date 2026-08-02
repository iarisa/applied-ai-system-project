# Goal

# Plan

# Sample Design / Architecture
Input: User profile song preferences 
(favorite genre, favorite mood, target energy, target valence, target danceability)
        |
        | user preferences
        V
Retriever (Recommender):             Knowledge Base:
scores each song based on 
user preferences                <-----  song-background-files (contains info about each song, artist, etc.)
        |
        | top 5 recommended songs
        V
Agent (LLM):
uses 5 recommended songs + song-background-files 
to generate user-friendly explaination of the scores and each song/recommendation
        |
        |
        V
    Evaluator:
automated tests to verify:
- explanation contains the 5 expected songs exactly
- accurate attribute claims (e.g. if mentions high energy, ensure it's actually high)
- basic format checks (if needed)
        |
        |
        V
        fails? -> attempt to regenerate, or just show raw scores
        |
        |
        V
    Final response -> back to user



# Notes
Evaluation:

Overall: Have the Agent return both the natural-language explanation and a small structured JSON (song list + attribute claims) in the same response. It turns your hardest two checks into trivial data comparisons.


- explanation contains the 5 expected songs exactly
Constrain the Agent's output format in the prompt so each song is introduced identifiably, e.g. a numbered list with the exact title from your data (1. **Song Title** — ...).

The Evaluator then just does a straight set comparison: extract the 5 titles from that structured position in the text (or from the claims list below if you go structured), and check set(extracted) == set(expected_top_5).

- accurate attribute claims (e.g. if mentions high energy, ensure it's actually high)

Have the Agent have structured claims like this, so Evaluator just does dict comparison:
{
  "explanation": "Song X is a great pick because it's high-energy...",
  "claims": [{"song": "Song X", "attribute": "energy", "level": "high"}, ...]
}

# Schedule
- Sat 8/1: 
    - Define how to add RAG to project 
    (branch: feature/song-background-rag)
        > Add additional files of song/artist background -> consult when making recommendations
        
    - Define design and architecture for project
        Show how your project is organized by creating a short system diagram. Your diagram should include:

        The main components (like retriever, agent, evaluator, or tester).
        How data flows through the system (input → process → output).
        Where humans or testing are involved in checking AI results.

- Sun 8/2:
    - Setup the design/architecture for project

    - Implement the RAG feature 

    - Implement Stretch Feature 
    (branch: feature/genre-overlap-rag-enhancement)
        > Add data file that describes overlapping genres -> add as explanation
        > Document before and after (across branches)

    - (Optional) Implement Stretch Feature 2
        > Test Harness or Evaluation Script
        Build a script that runs your system on a set of predefined inputs and prints a summary (pass/fail scores, confidence ratings, or similar).

# How I used AI
- to understand the RAG tinker lab again
- to evaluate my ideas for using RAG to enhance my music recommender system (selected 2/3 for req + stretch bc 1st wasn't RAG)
- to generate sample architecture for another RAG system (e.g. pet care, scheduler), then evaluate the architecture I came up with for music recommender specifically (revised/clairfied)

# Deadline: Sun, Aug 10
Sample Presentation Outline:
The Format: The "Engineer's Pitch"
The Problem:What did you solve?
The Logic:How does the AI think (RAG? Agentic loop?)
The Reliability:How do you know it works? (Testing and Guardrails)
The Reflection:What surprised you?
