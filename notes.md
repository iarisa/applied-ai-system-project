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

## 4. Reliability and Evaluation: How You Test and Improve Your AI

- Surprising: that it was getting the thresholds wrong in full prompt, but correct on isolated tests
- Other testing + improvement: Had to revise prompt to not be generic, in 