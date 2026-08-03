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


# How I used AI
- to understand the RAG tinker lab again
- to evaluate my ideas for using RAG to enhance my music recommender system (selected 2/3 for req + stretch bc 1st wasn't RAG)
- to generate sample architecture for another RAG system (e.g. pet care, scheduler), then evaluate the architecture I came up with for music recommender specifically (revised/clairfied)
- to generate diagram based on the drafted one in my notes, also to update changes + ask follow-up questions to make diagram more accurate
    > Claude Code drew Knowledge Base arrows / flow wrong intially (song context vs song artist & background), also learned that I had left out songs.csv initially
- to draft an implementation plan and solidify design decisions for the RAG feature 
- generate song/artist background, revised song info to be more relevant to helping a user understand their ranking
    > I told it to apply changes to all 18 songs and it said it did, but it actually skipped the 17th one without telling me that -> had to call it out + correct it  
- Upgraded UI + also refined prompt sent to Gemini to sound more conversational instead of sounding like copy/paste from the docs

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

## 4. Reliability and Evaluation: How You Test and Improve Your AI
- Claims kept being off
-When I selected 4 twice, here's what I got:
Attempt 1: Evaluator rejected the explanation:
  - Inaccurate claim: Spacewalk Thoughts danceability=0.41 is 'medium', but claim said 'low'.

Attempt 2: Evaluator rejected the explanation:
  - Inaccurate claim: Spacewalk Thoughts danceability=0.41 is 'medium', but claim said 'high'.

Retries exhausted. Falling back to raw scores.

Had to update thresholds to be < / > not <= >= (non-inclusive, bc otherwise confusing agent)

- Fixed boundary cases
- Still failing in full prompt, but succesful in isolation
- Instead defined claims and thresholds, then fed into AI instead of letting it derive them 

- Surprising: that it was getting the thresholds wrong in full prompt, but correct on isolated tests
- Other testing + improvement: Had to revise prompt to not be generic, in two
different ways found through testing:

1) Generic tone - sounded like it was copy/pasting straight from the
song-background docs instead of talking like a person.

Before (copy/paste tone):
"This track received a match score of 5.91 due to a genre match and mood
match. It pairs rain-soaked field recordings with gentle Rhodes piano
chords."

After (conversational, in its own words):
"Paper Lanterns crafted this piece using real audio captured right outside
a university library window, layering it beneath gentle Rhodes piano chords
that never rise above a whisper. It hits a medium energy level alongside a
high acousticness rating, making it a natural fit for your chill session."

2) Generic content - described facts about the artist/song without ever
explaining why it matched my stated preferences.

Before (describes the artist/song, never says why it matches me):
"4. Spacewalk Thoughts - Orbit Bloom created this eight-minute meditation
using a single sustained drone on modular synthesizers that shifts almost
imperceptibly over time."

After (explicitly ties back to what I asked for):
"1. Gym Hero - I knew you would love this pop track by Max Pulse because it
hits every mark for an intense workout with its punchy drums, shouted gang
vocals, and relentless four-on-the-floor beat designed to keep pace with
your training."