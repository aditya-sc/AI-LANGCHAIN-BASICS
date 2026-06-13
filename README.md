# AI · LangChain Basics

Personal learning repo for the **LangChain 1.0** and **LangGraph** ecosystems —
worked examples building up from a single model call to tool-calling agents,
structured output, middleware, human-in-the-loop, and MCP servers.

The conceptual write-up that ties everything together lives in
**[`NOTES.md`](./NOTES.md)** — a durable, concept-organized reference distilled
from working through this material (LangGraph mental model, agents vs. graphs,
checkpointers, message types, async/GIL, MCP transports, and more). The code
comments throughout both sub-projects cross-reference its sections.

## Layout

| Folder                                | What's inside                                                                                       |
| ------------------------------------- | --------------------------------------------------------------------------------------------------- |
| [`01-basics/`](./01-basics)           | LangChain v1 fundamentals as notebooks: models, streaming/batch, messages, tools, structured output, middleware. |
| [`02-agents/`](./02-agents)           | LangGraph agents: hand-built `StateGraph` chatbots, tool loops, checkpointer memory, human-in-the-loop, and MCP servers + client. |
| [`NOTES.md`](./NOTES.md)              | The shared reference notes both projects point back to.                                             |

Each sub-project is an independent [`uv`](https://docs.astral.sh/uv/) project
with its own `pyproject.toml` / `uv.lock` and `.venv`.

## Running

Models target a local [Ollama](https://ollama.com/) install (mostly
`qwen3:8b`). Tool examples that search the web use Tavily, which needs a
`TAVILY_API_KEY` in a local `.env` (never committed — see `.gitignore`).

```bash
# pick a sub-project, then:
cd 01-basics          # or: cd 02-agents
uv sync               # install deps into .venv from the lockfile
```

Open the notebooks in `01-basics/learning/` or `02-agents/1-BasicChatbot/`
and select the project's `.venv` interpreter (see NOTES.md §1 if imports won't
resolve). For the MCP example, see [`02-agents/README.md`](./02-agents/README.md).
