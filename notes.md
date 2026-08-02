# Goal

# Plan

# Sample Design / Architecture
Input: User profile song preferences
(favorite genre, favorite mood, target energy, target valence, target danceability)
        |
        | user preferences
        V
Recommender:                         songs.csv:
scores each song based on   <-----   song attributes (genre, mood, energy,
user preferences                     tempo_bpm, valence, danceability, acousticness)
        |
        | top 5 ranked songs
        V
Retriever:                           Knowledge Base:
looks up background for     <-----   song-background-files (contains info
the top 5 songs only                 about each song, artist, etc.)
        |
        | top 5 songs + background
        V
Agent (LLM):
uses top 5 songs + retrieved background
to generate user-friendly explanation of the scores and each song/recommendation
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
- Sun 8/2:
    - Implement the RAG feature (branch: feature/song-background-rag)
        > Add additional files of song/artist background -> consult when making recommendations

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
- to generate diagram based on the drafted one in my notes, also to update changes + ask follow-up questions to make diagram more accurate
    > Claude Code drew Knowledge Base arrows / flow wrong intially (song context vs song artist & background), also learned that I had left out songs.csv initially
- to draft an implementation plan and solidify design decisions for the RAG feature 
- generate song/artist background, revised song info to be more relevant to helping a user understand their ranking
    > I told it to apply changes to all 18 songs and it said it did, but it actually skipped the 17th one without telling me that -> had to call it out + correct it  

# Deadline: Sun, Aug 10
## Sample Presentation Outline:
The Format: The "Engineer's Pitch"
The Problem: What did you solve?
The Logic: How does the AI think (RAG? Agentic loop?)
The Reliability: How do you know it works? (Testing and Guardrails)
The Reflection: What surprised you?

## From Email: 
- what you built and why
- how it works
- how you tested it
- the challenges you overcame
- what you're most proud of