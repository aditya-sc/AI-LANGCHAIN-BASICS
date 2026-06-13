# 02-agents — LangGraph agents & MCP

Hand-built LangGraph agents and Model Context Protocol (MCP) servers. The
conceptual backbone for everything here is the repo-root
[`NOTES.md`](../NOTES.md) — start there.

## Notebooks (`1-BasicChatbot/`)

| Notebook                  | Topic                                                              | NOTES.md ref |
| ------------------------- | ----------------------------------------------------------------- | ------------ |
| `1-basicchatbot.ipynb`    | `StateGraph` basics → tool node + `tools_condition` loop → `MemorySaver` memory | §2, §3, §5 |
| `2-humanintheloop.ipynb`  | `interrupt()` + `Command(resume=...)` to pause for a human         | §4, §5       |

## MCP example (`*.py`)

`create_agent` driven over tools served by two MCP servers — one `stdio`, one
`streamable_http` (NOTES.md §10 explains the transport difference).

```bash
uv sync

# 1. The HTTP server must be started manually and kept running:
uv run python weatherserver.py        # serves http://localhost:8000/mcp

# 2. In another terminal, run the client. It launches mathserver.py itself
#    (stdio = client-spawned on demand) and connects to the weather server.
uv run python client.py
```

MCP tools are **async-only** — the client drives the agent with `await
agent.ainvoke(...)` (NOTES.md §10). Web search needs `TAVILY_API_KEY` in `.env`.
