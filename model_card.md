# 🎧 Model Card: PutMeOn 2.0 (RAG-Enhanced Music Recommender)


## Limitations and Biases
- The Recommender's scoring is a fixed weighted formula (genre 3.0, mood 1.5, energy 0.7, valence 0.5, danceability 0.3), not something learned from user feedback. Those weights are based on my own assumption that genre/mood matter more than numeric energy/valence/danceability fit.
- There's no credit for similar genres. For example, a favorite genre of "rap" gets 0 match points against a song tagged "hip hop" although both are similar (same limitation from PutMeOn 1.0)
- The Retriever only looks up artist/song background for the 5 songs the Recommender already picked, never the full catalog. Even though that keeps retrieval cheap, it also means RAG can only change how a song is explained, never which songs get chosen. Any bias from the scoring weights get passed into the LLM.
- The song/artist background data in `song_background.json` is something I wrote for 18 songs using AI assistance, not sourced or verified against anything real.
- The Agent's natural-language explanation depends on `GEMINI_API_KEY` and Gemini's availability. Without it, the app silently falls back to raw scores. That's a deliberate design choice, not a bug, but it means two users could get very differently-styled output (prose vs. bare numbers) for reasons that have nothing to do with their preferences.


## Potential for Misuse
- If the Evaluator guardrail were removed or bypassed, the Agent could state an inaccurate attribute claim (e.g. call a low-energy song "high energy") in a confident, conversational tone that makes it harder for a user to notice than a bare wrong number would be. The Evaluator exists specifically to catch this before anything unverified reaches the user, and a failed check falls back to raw scores rather than showing a disclaimer next to unverified text.
- Because the Recommender only ever scores against a user's stated preferences, repeated use could narrow someone's exposure over time rather than widen it. It optimizes for "matches what you already said you like," not for useful surprise when recommending songs.
- Overall misuse risk is low in its current form: it's a single-user, read-only CLI demo that doesn't persist personal data or take any action beyond printing text.

## Reliability Surprises
- I was surprised that the LLM struggled to properly classify the song's energy level as low/medium/high in the full prompt, but it correctly classified them when this was the only task given to the LLM. This is why I had to precompute the classifications instead of allowing the LLM to derive them.
- I was also surprised that at first, the generated explanations read like they'd been copy-pasted straight out of the background docs ("This track received a match score of 5.91 due to a genre match...") instead of sounding like an actual recommendation. I had to explicitly prompt for a conversational tone and require every item to tie back to the listener's stated preferences, not just describe the artist/song on its own.

## AI Collaboration
- **Helpful:** Before committing to my five-stage pipeline (Recommender -> Retriever -> Agent -> Evaluator), I asked Claude Code to sketch a sample architecture for a different RAG system (a pet-care scheduler) so I'd have something unfamiliar to refer to. Evaluating that unrelated example, then applying the same scrutiny back to my own design, is what helped me notice I'd left `songs.csv` out of my first architecture diagram entirely. I also used AI to evaluate my ideas for my initial RAG implementation plans, and that's how I narrowed it down to the song background sources.

- **Flawed:** I asked Claude Code to generate song/artist background entries for all 18 songs, and it reported back that it had done so. But it had actually skipped the 17th song without mentioning it. I only caught the gap because I checked the output file directly instead of taking the "done" summary at face value. That was a good reminder to verify coverage/count on any bulk-generation task instead of just trusting its completion claim.
