# 01-basics — LangChain v1 fundamentals

Notebook-by-notebook walk through the core LangChain 1.0 building blocks. Models
target a local Ollama install (`qwen3:8b` / `qwen2.5:7b`). Concepts here are
explained in depth in the repo-root [`NOTES.md`](../NOTES.md).

## Notebooks (`notebooks/`)

| Notebook                                  | Topic                                                              | NOTES.md ref |
| ----------------------------------------- | ----------------------------------------------------------------- | ------------ |
| `01-create-agent.ipynb`                   | `create_agent` — the standard ReAct loop in one call              | §6           |
| `02-chat-models.ipynb`                    | `init_chat_model` vs. `ChatOllama`; `.invoke`                     | §11          |
| `03-streaming-and-batch.ipynb`            | `.stream` (token-by-token) and `.batch`                           | §11, §12     |
| `04-tools.ipynb`                          | `@tool`, `bind_tools`, the manual tool-execution loop            | §3, §8       |
| `05-messages.ipynb`                       | System / Human / AI / Tool message types                         | §8           |
| `06-structured-output-pydantic.ipynb`     | `with_structured_output` via a Pydantic model                    | §9           |
| `07-structured-output-typeddict.ipynb`    | `with_structured_output` via a TypedDict                         | §9           |
| `08-structured-output-agent.ipynb`        | `response_format` on `create_agent` (Pydantic / TypedDict / dataclass) | §6, §9 |
| `09-middleware-summarization.ipynb`       | `SummarizationMiddleware`                                         | §7           |
| `10-middleware-human-in-the-loop.ipynb`   | `HumanInTheLoopMiddleware`                                        | §4, §7       |

## Setup

Environment is shared at the repo root — see the [root README](../README.md).
After `uv sync`, open `notebooks/*.ipynb` and select the root `.venv` kernel.
Tool/search examples need a `TAVILY_API_KEY` in the root `.env`.
