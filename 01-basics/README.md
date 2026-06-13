# 01-basics — LangChain v1 fundamentals

Notebook-by-notebook walk through the core LangChain 1.0 building blocks. Models
target a local Ollama install (`qwen3:8b` / `qwen2.5:7b`). Concepts here are
explained in depth in the repo-root [`NOTES.md`](../NOTES.md).

## Notebooks (`learning/`)

| Notebook                      | Topic                          | NOTES.md ref |
| ----------------------------- | ------------------------------ | ------------ |
| `1-intro.ipynb`               | `create_agent` — the standard ReAct loop in one call | §6 |
| `2-integrate-models.ipynb`    | `init_chat_model` vs. `ChatOllama`; `.invoke` | §11 |
| `3-message-struct.ipynb`      | `.stream` (token-by-token) and `.batch` | §11 |
| `4-tools.ipynb`               | `@tool`, `bind_tools`, the manual tool-execution loop | §3, §8 |
| `5-messages.ipynb`            | System / Human / AI / Tool message types | §8 |
| `6,7,8-structured-output.ipynb` | `with_structured_output` & `response_format` via Pydantic / TypedDict / dataclass | §9 |
| `9,10-middleware.ipynb`       | `SummarizationMiddleware`, `HumanInTheLoopMiddleware` | §7 |

## Setup

```bash
uv sync
# then open learning/*.ipynb and select .venv as the kernel
```

Tool/search examples need a `TAVILY_API_KEY` in a local `.env`.
