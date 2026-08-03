# PutMeOn 2.0

## Summary

**PutMeOn 2.0** is a RAG-enhanced version of the original content-based music recommender [PutMeOn 1.0](https://github.com/iarisa/ai110-module3show-musicrecommendersimulation-starter) from Module 3.

PutMeOn 1.0 recommended songs that match your taste (favorite genre and mood, energy, positivity, and danceability) by scoring the songs in the catalog and giving you the top 5 songs you should listen to next. It's a content-based recommender, using a fixed weighted point system across those five features to rank the catalog.

PutMeOn 2.0 pairs that scoring engine with RAG: instead of handing you a bare number, an LLM agent digs into real song/artist background and tells you *why* each track is a match, in its own words. It's not just making that up, either - an Evaluator holds the explanation to the actual data (right songs, accurate attribute claims) before you ever see it, retrying the Agent or falling back to raw scores if it can't back up its claims. That's the RAG upgrade: recommendations you don't just get, but actually understand and can trust!

## Architecture Overview

PutMeOn 2.0 runs as a five-stage pipeline (see `diagrams/architecture.mmd`). Your stated preferences and `songs.csv`'s song attributes feed the **Recommender**, which scores every song and returns the top 5. The **Retriever** looks up artist/song background for just those 5 from the knowledge base, then the **Agent** (LLM) uses that background to generate a natural-language explanation of the picks. The **Evaluator** checks that explanation for song-match accuracy, attribute accuracy, and format before it's shown - a failure sends it back to the Agent for a retry, and exhausting retries falls back to raw scores rather than showing an unverified explanation. Either way, that final response (explanation or raw scores) is what reaches the user.

## Setup Instructions

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your Gemini API key so the Agent can generate explanations (without it, the app still runs and falls back to raw scores):

   ```bash
   cp .env.example .env
   # then edit .env and set GEMINI_API_KEY=your_api_key_here
   ```

4. Run the app:

   ```bash
   python -m src.main
   ```

5. Run the unit tests:

   ```bash
   pytest
   ```

6. (Optional) Run the test harness to evaluate the full Recommender -> Retriever -> Agent -> Evaluator pipeline across all sample profiles. This calls the real Gemini API (up to 2 requests per profile), so only run it with a valid `GEMINI_API_KEY` in place:

   ```bash
   python -m tests.test_harness
   ```

## Sample Interactions

### Example 1: Chill Lofi (end-to-end run with RAG explanation)

```
$ python -m src.main
Choose a user preference profile:
  1) Chill Lofi
  2) High-Energy Pop
  3) Mellow Acoustic
  4) Dance Party
  5) High-Energy Lofi
  6) Melancholy Metalhead
  7) Furious Opera Fan
  q) Quit
Enter choice: 1

=== Chill Lofi ===

Top recommendations:

1. Library Rain - I picked this Paper Lanterns piece because it nails your go-to lofi genre and chill mood, matching your desired low energy and upbeat valence by blending actual university library rainfall with a gentle, unhurried Rhodes piano progression that stays right around a whisper.

2. Midnight Coding - Since you are after that classic chill lofi vibe, I had to include this bedroom-producer track from LoRoom, which hits your sweet spot for energy and danceability by pairing a loping mid-tempo drum loop with dusty piano chords and cozy tape hiss.

3. Focus Flow - Even though it leans toward a focused rather than strictly chill mood, this LoRoom track fits your target energy and danceability so well with its steady beat and mellow acoustic textures that it will effortlessly slip into your background listening.

4. Spacewalk Thoughts - I chose this Orbit Bloom piece because its ultra-slow ambient soundscape captures that peaceful chill mood you love, hitting your low energy preference almost perfectly with a single sustained synthesizer drone that shifts imperceptibly over eight minutes.

5. Coffee Shop Stories - Although it steps outside your usual lofi genre into jazz, this Slow Stereo track shares the relaxed mood you enjoy and hits your exact target valence and energy through intimate brushed drums and loose, conversational piano runs.

Enter choice: q

Goodbye.
```

### Example 2: Mellow Acoustic (different input, same pipeline)

```
$ python -m src.main
Choose a user preference profile:
  ...
Enter choice: 3

=== Mellow Acoustic ===

Top recommendations:

1. Moonlight Fragments - Elena Voss crafted this sparse, minor-key piano piece specifically to match your love for classical music and melancholy moods, leaning into a gentle energy of 0.22 and a calm valence of 0.30 by using a single repeating motif that stays entirely still rather than building momentum.

2. Spacewalk Thoughts - Even though it comes from an ambient background, Orbit Bloom created this piece with a low energy level of 0.28 and a very slow tempo that easily aligns with your desire for a quiet, low-danceability vibe as a single sustained drone shifts imperceptibly over eight minutes.

3. Wildflower Roads - Callum Hart brings a warm, acoustic folk storytelling style that fits your low-energy and low-danceability targets through a loose and unhurried strum that never pushes toward a beat you would want to dance to.

4. Library Rain - Paper Lanterns pairs rain-soaked field recordings with a slow and unhurried piano progression that stays right around your preferred low energy and low danceability mark by never rising above a whisper.

5. Focus Flow - LoRoom designed this bedroom-producer track to gently fade into the background rather than demand your attention, offering a mellow and unhurried texture that suits your target energy and low movement preferences.

Enter choice: q

Goodbye.
```

### Example 3: Reliability check via the test harness (Evaluator guardrail in action)

```
$ python -m tests.test_harness
======================================================================
TEST HARNESS: Recommender -> Retriever -> Agent -> Evaluator
======================================================================

>>> [1/7] Testing profile: Chill Lofi
[PASS] Chill Lofi
    Pipeline (Recommender/Retriever): PASS
    Agent/Evaluator: PASS (attempts used: 2/2, confidence: medium (needed a retry))

>>> [2/7] Testing profile: High-Energy Pop
[PASS] High-Energy Pop
    Pipeline (Recommender/Retriever): PASS
    Agent/Evaluator: PASS (attempts used: 1/2, confidence: high (passed on 1st try))

>>> [3/7] Testing profile: Mellow Acoustic
[PASS] Mellow Acoustic
    Pipeline (Recommender/Retriever): PASS
    Agent/Evaluator: PASS (attempts used: 1/2, confidence: high (passed on 1st try))

... (4 more profiles, same pattern)

----------------------------------------------------------------------
Pipeline checks:        7/7 passed
Agent/Evaluator checks: 7/7 passed
----------------------------------------------------------------------
```

Notice "Chill Lofi" needed a retry (attempt 2/2) before its explanation passed - the Evaluator rejected the Agent's first attempt (an inaccurate attribute claim) and the retry loop caught it, so what reaches the user is always checked against the real data rather than trusted on the first try.

## Design Decisions

I stored each song's artist/background info in a single JSON file, keyed by song, rather than cramming it into a long text field on the existing `songs.csv`. Claude Code suggested a separate file per song (18 files total), but I went with one file holding all 18 entries. It's easier to load as one file, but it requires more scrolling.

I kept the deterministic weighted-scoring Recommender from PutMeOn 1.0 in charge of picking the actual top 5 songs, and only layered the LLM Agent on top to explain those picks. I could have had the LLM pick songs directly, but that would make the ranking harder to reason about and could lead to hallucinating a song into the list that doesn't actually fit. Since the scoring process is deterministic, all the LLM has to do is generate user-friendly explanations.

The Retriever only looks up artist/song background for the 5 songs the Recommender already picked, not the whole 18-song catalog. This keeps retrieval cheap and fast, but it means the knowledge base can never influence which songs get chosen, only how they get explained.

For the Evaluator, I capped retries at 2 attempts before falling back to raw scores. More retries would reduce how often users see a bare score list, but each retry is another Gemini API call, so I picked 2 as a balance between giving the Agent a fair second try and not burning API calls chasing a passing explanation. And when both attempts fail, I chose to fall back to raw scores rather than show an unverified explanation with a disclaimer.

Finally, the app treats `GEMINI_API_KEY` as optional: without it, the app still runs and just skips straight to raw scores instead of crashing. I wanted "no LLM available" to be a defined, graceful behavior rather than an edge case I hadn't thought about.

## Testing Summary

### Failed LLM Claim Checks
When I was testing, I found a boundary bug in the Evaluator's claim-checking. It was using overlapping ranges since the "medium" range included the threshold value for "low" and "high." For example, even though Library Rain's energy value is 0.35 which is exactly the same as the low-end threshold, the LLM would classify its energy as "medium". So I made "medium" strictly between the thresholds (`low_threshold < value < high_threshold`), and let "low"/"high" absorb the exact boundary values (`value <= low_threshold` is low, `value >= high_threshold` is high) to remove the overlap.

However, there were still errors in the LLM explanation because the Evaluator flagged Spacewalk Thoughts' danceability (0.41) as a mismatch (instead of "medium," it was "low" on attempt 1 and "high" on attempt 2). I tested the LLM's scoring logic without the additional prompt requirements and it scored it accurately as "medium." So I decided to pre-compute the "low"/"medium"/"high" label instead of relying on the LLM to derive the values from the song attributes.

### Evaluating LLM Explanations
I also tested the LLM's explanations based on the information it was retrieving from the `song_background` JSON. At first, the explanations sounded like they were copy-pasted straight from the song background docs (e.g. "This track received a match score of 5.91 due to a genre match...") instead of sounding like a real person. I revised the prompt to make it sound more conversational instead of having a rigid structure. Even then, the explanations were still describing the artist/song without really explaining why it matched the user's stated preferences. So I had to pass in the user preferences and explicitly update the prompt to tie the explanations back to them. This had better output like "I knew you would love this because it hits every mark for an intense workout..." instead of a plain artist bio.

### Lessons Learned
I learned that it's important to resolve any ambiguity in the prompt that an LLM receives (such as overlapping boundaries for thresholds) and to provide all the necessary information needed to generate better results (e.g. user preferences). I also learned how to separate predefined definitions (e.g. low/medium/high classifications) from data that should be generated (e.g. user-friendly explanations).

## Reflection

This project taught me about the power of using AI to collaborate instead of allowing it to do every task for me. I learned to present my drafted ideas and seek Claude Code's input so I could decide which revisions to implement or discard. I also learned how to use AI to debug different errors while also calling out inconsistencies that I noticed in the code or text it generates. Overall, it was a very fruitful and engaging experience since I learned about AI's strengths (fast code generation, precise revisions) as well as my own (design decisions, judgment calls, drafting ideas).
