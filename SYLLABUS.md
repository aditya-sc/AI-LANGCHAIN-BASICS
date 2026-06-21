# AI Engineer — Syllabus & Progress Tracker

The full width-and-breadth map of what an **AI Engineer** needs (not an ML
researcher). Organized in 7 layers, bottom (how models work) → top (production).
This is the single source of truth for *"am I interview-ready yet?"*

> **Scope-setting rule:** AI Engineer ≠ ML Researcher. You build *on top of* models.
> You do **not** need backprop math, CUDA, or training from scratch. Know the
> transformer *conceptually*, not mathematically. Anything marked ⚪ Aware is a trap
> to over-invest in.

---

## How to use this tracker

**Depth needed** (the target — not all topics deserve equal effort):
- 🔵 **Deep** — must explain mechanism + trade-offs + failure modes, no notes
- 🟢 **Working** — must be able to *build* it
- ⚪ **Aware** — know what it is + when it matters; can't be blindsided

**Your status** (edit the checkbox + status as you go):
- `[ ]` ⬜ Not started
- `[ ]` 🟡 Learning
- `[x]` ✅ Solid — passes the **4-beat test** below

**The 4-beat test** (the bar for "Solid" / `[x]`): can you, out loud and without
notes — **Define → Why it exists → Practical consequence → Name the mechanism**?
If not, it's not Solid yet, no matter how many times you've read it.

**The second-question test:** for every topic, the interviewer's follow-up is
almost always *"what are the failure modes?"* and *"how would you measure it?"*.
A topic isn't Solid until you can answer the follow-up too.

> Pre-filled marks below are inferred from this repo's notebooks/notes — **re-audit
> them honestly against the 4-beat test**, don't trust the pre-fill.

---

## Progress summary (update as you go)

| Layer | Theme | Target | Self-rating |
| ----- | ----- | ------ | ----------- |
| 0 | How LLMs work | mixed | 🟡 partial — embeddings solid, generation loop a gap |
| 1 | Prompting & interaction | mostly 🟢/🔵 | 🟡 partial |
| 2 | Retrieval / RAG | mostly 🔵 | ✅ strongest area |
| 3 | Agents & orchestration | mostly 🔵/🟢 | 🟡 framework-yes, from-scratch-no |
| 4 | Evaluation & observability | mostly 🔵/🟢 | ⬜ biggest opportunity |
| 5 | Safety & guardrails | mostly 🟢 | 🟡 partial |
| 6 | Production / LLMOps | mostly 🟢/🔵 | 🟡 your software-dev edge |
| 7 | Adjacent (fine-tuning etc.) | ⚪ only | ⬜ awareness only |

**Headline:** Layer 2 strong. Real gaps = Layer 0 (generation/sampling), Layer 3
(build-from-scratch), Layer 4 (evals). You're closer than it feels.

---

## Layer 0 — How LLMs actually work

- [ ] 🔵 **Tokenization** — subword/BPE; ~1 token ≈ 4 chars ≈ 0.75 words; whitespace is part of the token; non-English/code tokenize less efficiently; explains bad arithmetic & letter-counting
- [x] 🔵 **Embeddings** — text → meaning vector; cosine similarity *(repo: 03-traditional-rag)*
- [ ] 🔵 **Autoregressive generation** — logits → softmax → sample one token → repeat; latency scales with output tokens
- [ ] 🔵 **Context window** — the token budget; what happens when you exceed it
- [ ] ⚪ **Transformer & attention** — *conceptually*: tokens attending to each other. No math.
- [ ] 🔵 **Sampling controls** — temperature, top-p, top-k; greedy vs. sampling
- [x] ⚪ **Parameters vs. tokens** — weights vs. runtime text units *(repo: NOTES.md)*
- [ ] ⚪ **Training stages** — pretraining → instruction-tuning → RLHF; base vs. instruct/chat models
- [ ] ⚪ **Hallucination — why** — predicting plausible tokens, not retrieving facts
- [ ] ⚪ **Quantization** — what 4-bit means; quality/speed trade (relevant: your local qwen)

## Layer 1 — Prompting & model interaction

- [x] 🟢 **Message roles** — system / user / assistant *(repo: 05-messages)*
- [ ] 🔵 **Prompt engineering** — few-shot, role, delimiters, output format as a deliberate discipline
- [x] 🔵 **Structured output** — JSON mode, schemas, Pydantic/TypedDict *(repo: 06/07/08-structured-output)*
- [ ] 🟢 **Chain-of-thought / reasoning** prompting
- [x] 🟢 **Streaming** — token-by-token output *(repo: 03-streaming-and-batch)*
- [ ] ⚪ **Prompt caching** — cut cost/latency on repeated prefixes
- [ ] ⚪ **Prompt injection (intro)** — see Layer 5

## Layer 2 — Retrieval & data (RAG)

- [x] 🔵 **Chunking** — RecursiveCharacterTextSplitter, size/overlap, precision/context trade *(repo: NOTES §2)*
- [x] 🔵 **Embeddings & cosine similarity** — direction = meaning *(repo: NOTES §3–6)*
- [x] 🟢 **Vector DBs** — store/query vectors *(repo: ChromaDB; upgrade to Qdrant/pgvector)*
- [ ] 🔵 **Hybrid search** — BM25 (keyword) + dense (semantic) fused
- [ ] 🔵 **Reranking** — cross-encoder re-scores top-k for precision
- [ ] 🟢 **Query rewriting / expansion** — fix vague/ambiguous queries before retrieval
- [ ] 🟢 **Metadata filtering** — narrow by source/date/type
- [ ] ⚪ **Advanced chunking** — semantic, hierarchical, parent-document
- [ ] ⚪ **Vectorless / agentic retrieval** — LLM-driven lookup without a vector index
- [ ] 🔵 **Why RAG fails** — bad chunks, lost-in-the-middle, retrieval ≠ correct answer

## Layer 3 — Agents & orchestration

- [ ] 🔵 **The agent loop (ReAct)** — thought → action → observation → repeat; **build from scratch, no framework**
- [x] 🔵 **Tool / function calling** *(repo: 04-tools)*
- [ ] 🟢 **Multi-step planning** — decompose a goal into steps
- [ ] 🟢 **Memory** — short-term (state) vs. long-term (persisted)
- [ ] 🟢 **Multi-agent patterns** — planner / critic / writer / reviewer
- [x] 🟢 **Graphs / state machines** — LangGraph nodes, edges, conditional routing *(repo: 02-agents)*
- [ ] 🔵 **Context management** — what goes in the window, summarization, overflow handling
- [x] ⚪ **Human-in-the-loop** *(repo: 02/10-human-in-the-loop)*
- [x] ⚪ **MCP** — tool/server protocol *(repo: 02-agents MCP)*

## Layer 4 — Evaluation & observability  ⭐ highest interview signal

- [ ] 🔵 **Why eval is hard** — no single right answer; can't unit-test prose
- [ ] 🔵 **LLM-as-judge** — using a model to grade outputs; its biases/limits
- [ ] 🟢 **Golden datasets** — curated input/expected pairs
- [ ] 🟢 **RAG metrics** — faithfulness, context precision/recall, answer relevance (Ragas)
- [ ] 🟢 **Regression testing** — catch quality drops across prompt/model changes
- [ ] 🟢 **Tracing** — see every step/token/tool call (Langfuse)
- [ ] 🟢 **Cost & latency tracking** — per request, per step
- [ ] ⚪ **Offline vs. online eval**, A/B testing

## Layer 5 — Safety & guardrails

- [ ] 🟢 **Input/output guardrails** — validate before and after the model
- [ ] 🔵 **Prompt injection & jailbreaks** — and mitigations
- [ ] 🟢 **PII detection / redaction**
- [ ] 🟢 **Hallucination mitigation** — grounding, citations, "I don't know"
- [ ] ⚪ **Content moderation, toxicity/bias**

## Layer 6 — Production / LLMOps  (your software-dev edge)

- [ ] 🟢 **Serving** — wrap an LLM app in FastAPI
- [ ] 🔵 **Cost optimization** — model routing, caching, smaller models where possible
- [ ] 🔵 **Latency optimization** — streaming, time-to-first-token, parallel calls
- [ ] 🟢 **LLM gateway / provider abstraction** — one `get_model()`, swap Ollama/Groq/Gemini
- [ ] ⚪ **Rate limits, retries, fallbacks**
- [ ] ⚪ **Deployment** — Docker, env/secrets
- [ ] ⚪ **Versioning** prompts & models
- [ ] ⚪ **Scaling / load** considerations

## Layer 7 — Adjacent (⚪ awareness only — do NOT over-invest)

- [ ] ⚪ **Fine-tuning vs. RAG vs. prompting** — *when* to choose each (classic interview Q)
- [ ] ⚪ **LoRA / PEFT** — what it is, not how to derive
- [ ] ⚪ **Embedding model training / distillation** — vocabulary only

---

## Interview-readiness gates

You're ready to interview when you can clear these, not when the boxes are all
checked:

- [ ] Can give the **4-beat answer** for every 🔵 topic, cold.
- [ ] Can answer the **second question** (failure modes + how to measure) for Layers 2, 3, 4.
- [ ] Have **shipped** ≥3 of the 4 projects in `PROJECTS.md`, each with an eval story.
- [ ] Can whiteboard a **system design**: "design a customer-support RAG bot" end to end.
- [ ] Can explain **when NOT to use** an LLM / RAG / an agent (knowing the limits signals seniority).

---

*Companion file: [`PROJECTS.md`](./PROJECTS.md) — the portfolio that proves this syllabus.*
