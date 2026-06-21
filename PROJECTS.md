# AI Engineer — Project Portfolio (Portable Goal Reference)

> **Carry this file into each project repo.** It's the self-contained "north star"
> for what each project must prove. Build 4, not 11 — these are chosen to cover the
> full interview skill matrix with minimum overlap, maximum signal.

**Ground rules**
- **Write the code yourself.** Use an AI assistant as a tutor/reviewer/debugger, not
  autocomplete. From-scratch projects must be 100% hand-written.
- **Stay free / local-first.** Dev on `qwen3:8b` (Ollama). Put every model behind a
  provider-agnostic `get_model()` so you can swap in free hosted tiers (Groq, Gemini
  free, OpenRouter free) for demos that need a stronger brain.
- **Every project ships with an eval story.** "How do you know it got better?" is the
  #1 question juniors fail. Don't skip it.

**Status legend:** ⬜ Not started · 🟡 In progress · ✅ Shipped (deployed/demo-able)

| # | Project | Status | Target window |
| - | ------- | ------ | ------------- |
| 0 | ReAct from scratch | ⬜ | 1–2 days |
| 1 | Production RAG | ⬜ | 2–3 weeks |
| 2 | Deep Research Agent | ⬜ | 2–3 weeks |
| 3 | Market Data Research Agent | ⬜ | 2 weeks |

Recommended order is 0 → 1 → 2 → 3. Project 0 makes everything after it stop feeling
like magic.

---

## Project 0 — ReAct Agent From Scratch  ⬜

**Goal:** Build the agent loop with **zero frameworks** (raw model API only) so you
understand exactly what LangChain/LangGraph do under the hood.

**Build**
- Thought → Action → Observation loop, hand-written
- Your own tool registry (function name → callable + description)
- Prompt that instructs the model to emit a tool call, parse it, execute, feed the
  observation back, repeat until a final answer
- A stop condition + max-iterations guard (so it can't loop forever)

**Proves (interview skills):** agent loops, tool orchestration, context management,
parsing/control flow, "can you do it without a framework?"

**Done when**
- [ ] Solves a 2–3 step task (e.g. "what's the weather in the capital of France?"
      → lookup-capital tool → weather tool → answer)
- [ ] Handles a tool error without crashing
- [ ] You can explain every line cold

**Stack:** raw model API via `get_model()`, Python stdlib. No LangChain.

---

## Project 1 — Production RAG System  ⬜  ⭐ flagship

**Goal:** A RAG system that is *not* a toy PDF chatbot — it's measured, tuned, and
served. Extend the `03-traditional-rag` work from your learning repo.

**Build**
- Ingestion: load → chunk → embed → store (move to **Qdrant** or **pgvector**)
- **Hybrid search** — BM25 + dense, fused
- **Reranking** — cross-encoder over top-k
- **Query rewriting** — clean vague queries before retrieval
- **Metadata filtering** — by source/date/type
- **Eval suite (Ragas)** — faithfulness, context precision/recall, answer relevance
  on a golden dataset → this absorbs the "eval platform" idea; don't build it separately
- Serve via **FastAPI**; trace with **Langfuse**

**Proves:** retrieval quality, embeddings, search systems, **evaluation** (the big
differentiator), serving, observability.

**Done when**
- [ ] Eval suite runs on a golden set and prints metrics
- [ ] You can show a before/after where a change *measurably* improved retrieval
- [ ] Hybrid + rerank beats naive vector search on your metrics
- [ ] Exposed as a FastAPI endpoint with traced requests

**Stack:** sentence-transformers, Qdrant/pgvector, BM25, cross-encoder reranker,
Ragas, FastAPI, Langfuse, `get_model()`.

---

## Project 2 — Deep Research Agent  ⬜

**Goal:** Like Perplexity / ChatGPT Deep Research — multi-step research that plans,
searches, verifies, and writes a cited report. Naturally multi-agent.

**Build**
- Planner → Searcher → Verifier → Writer (LangGraph nodes)
- Web search tool · multi-step planning · source verification
- Citation generation · report synthesis · follow-up questions
- Memory/state across steps; context management as reports grow

**Proves:** agents, planning, tool calling, memory, multi-agent workflow design,
state management, context management.

**Done when**
- [ ] Takes a research question → returns a structured, **cited** report
- [ ] Plans and executes ≥3 sub-steps visibly (traced)
- [ ] Verifies/grounds claims against sources, not just model memory
- [ ] Degrades gracefully when a search returns nothing

**Stack:** LangGraph, a free web-search tool (e.g. Tavily free tier / DuckDuckGo),
`get_model()`, Langfuse.

---

## Project 3 — Market Data Research Agent  ⬜  (your differentiator)

**Goal:** Natural-language analytics over market data — your edge as an ex-software
dev. Most candidates don't have a data-engineering + agents combo.

**Build**
- Pipeline: download NSE/BSE bhavcopy → store in **PostgreSQL**
- Expose DB query tools to an agent (safe, parameterized)
- Ask in natural language → agent plans → queries → analyzes → answers
  - "Which sectors outperformed this month?"
  - "Find stocks with unusual volume."

**Proves:** data engineering, tool calling, agents, analytics, turning NL → safe SQL,
combining structured data with LLMs.

**Done when**
- [ ] End-to-end: ingest real bhavcopy → answer ≥3 distinct NL analytics questions
- [ ] Agent uses tools to query, doesn't hallucinate numbers
- [ ] Guardrail against unsafe/destructive queries
- [ ] Returns answers grounded in actual rows (cite the data)

**Stack:** PostgreSQL, a data-ingestion script, tool-calling agent (LangGraph or your
Project 0 loop), `get_model()`.

---

## Explicitly skipped (low ROI for "interview-ready ASAP")

- **Own agent framework** (#7) — fun, huge, low marginal signal vs. Project 0.
- **Autonomous browser agent** (#10) — brittle, time-sink, little AI signal.
- **Visual workflow builder** (#11) — months of UI, not AI-engineering signal.
- **Coding agent** (#2) — cool, but lower marginal learning since you already use one.
- **Mini-LangGraph** (#6) — only if you finish early and want orchestration depth.

---

## The portfolio polish checklist (do before interviewing)

- [ ] Each repo has a README: problem, architecture diagram, key decisions, eval results
- [ ] At least one project **deployed publicly** (even a free tier)
- [ ] A short write-up per project on *trade-offs* you made (this is what seniors probe)
- [ ] You can demo each live and explain any line on request

*Companion file: [`SYLLABUS.md`](./SYLLABUS.md) — the knowledge map these projects prove.*
