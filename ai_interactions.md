# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->

---

# Project 4 log: VibeFinder 2.0

| Step | What I asked Claude | What came back | What I did |
|---|---|---|---|
| Plan | Extend my music recommender; I want similar artists and learning from skips | Plan: RAG over notes + learning from history + eval harness | Followed it; skipped the optional agent loop |
| Data | Add songs and notes for 12 artists | 24 songs, sample history, 28 notes | Committed; normalized `rnb` to `r&b` |
| Code | Write the modules | `history.py`, `retriever.py`, `pipeline.py`, `cli.py`, `eval.py`, tests | Ran all of them; 6/6 tests pass |
| Debug | `python: command not found`, empty output files | Use `python3`, regenerate outputs | Regenerated and recommitted |

## Saved pipeline trace (from `python3 -m src.cli`)

```
- Learned profile from 30 history rows; weights={'energy': 1.5, 'valence': 1.02, 'danceability': 1.37, 'acousticness': 1.75}
- Retrieved 6 notes; neighbor genres=[]; similar artists=[...]
- Scored 27 unheard songs; confidence=0.62
```

Observation: `neighbor genres=[]` showed the neighbor-genre path never fired on this history. Documented as a limitation. Full traces: `assets/sample_run_retrieval.txt`.
