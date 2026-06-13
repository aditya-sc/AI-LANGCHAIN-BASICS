# 02-agents — LangGraph agents & MCP

Hand-built LangGraph agents and Model Context Protocol (MCP) servers. The
conceptual backbone for everything here is the repo-root
[`NOTES.md`](../NOTES.md) — start there.

## Notebooks (`notebooks/`)

| Notebook                       | Topic                                                              | NOTES.md ref |
| ------------------------------ | ----------------------------------------------------------------- | ------------ |
| `01-basic-chatbot.ipynb`       | `StateGraph` basics → tool node + `tools_condition` loop → `MemorySaver` memory | §2, §3, §5 |
| `02-human-in-the-loop.ipynb`   | `interrupt()` + `Command(resume=...)` to pause for a human         | §4, §5       |

## MCP example (`mcp/`)

`create_agent` driven over tools served by two MCP servers — one `stdio`, one
`streamable_http` (NOTES.md §10 explains the transport difference).

```bash
# environment is shared at the repo root (uv sync there first)
cd 02-agents/mcp

# 1. The HTTP server must be started manually and kept running:
uv run python weather_server.py        # serves http://localhost:8000/mcp

# 2. In another terminal (also in 02-agents/mcp), run the client. It launches
#    math_server.py itself (stdio = client-spawned) and connects to the weather server.
uv run python client.py
```

MCP tools are **async-only** — the client drives the agent with `await
agent.ainvoke(...)` (NOTES.md §10). Web search needs `TAVILY_API_KEY` in the root `.env`.
