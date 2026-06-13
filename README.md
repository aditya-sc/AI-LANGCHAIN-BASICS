# AI · LangChain Basics

Personal learning repo for the **LangChain 1.0** and **LangGraph** ecosystems —
worked examples building up from a single model call to tool-calling agents,
structured output, middleware, human-in-the-loop, and MCP servers.

The conceptual write-up that ties everything together lives in
**[`NOTES.md`](./NOTES.md)** — a durable, concept-organized reference distilled
from working through this material (LangGraph mental model, agents vs. graphs,
checkpointers, message types, async/GIL, MCP transports, and more). The code
comments throughout both folders cross-reference its sections.

## Layout

| Path                        | What's inside                                                                                       |
| --------------------------- | --------------------------------------------------------------------------------------------------- |
| [`01-basics/`](./01-basics) | LangChain v1 fundamentals as notebooks: models, streaming/batch, messages, tools, structured output, middleware. |
| [`02-agents/`](./02-agents) | LangGraph agents: hand-built `StateGraph` chatbots, tool loops, checkpointer memory, human-in-the-loop, plus MCP servers + client. |
| [`NOTES.md`](./NOTES.md)    | The shared reference notes both folders point back to.                                              |

`01-basics` and `02-agents` are just topic folders — the whole repo is **one**
[`uv`](https://docs.astral.sh/uv/) project with a single `pyproject.toml`,
`uv.lock`, and `.venv` at the root.

## Setup

Models target a local [Ollama](https://ollama.com/) install (mostly `qwen3:8b`).
Tool examples that search the web use Tavily, which needs a `TAVILY_API_KEY`.

```bash
uv sync                    # one environment for the whole repo -> ./.venv
cp .env.example .env       # then add your TAVILY_API_KEY (.env is gitignored)
```

Open any notebook in `01-basics/notebooks/` or `02-agents/notebooks/` and select
the root `.venv` interpreter (see NOTES.md §1 if imports won't resolve). For the
MCP example, see [`02-agents/README.md`](./02-agents/README.md).
