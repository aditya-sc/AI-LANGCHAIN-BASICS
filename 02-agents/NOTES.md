# Agentic / LangGraph / Python Concurrency — Durable Reference

A personal reference distilled from working through LangGraph agents, MCP, Python
environments, async, the GIL, and Go concurrency. Organized by concept, not by
conversation order. Revisit to quickly regain the mental models.

---

## 1. Python environments & imports

**Insight that fixed a real bug:** Being listed in `requirements.txt` does **not**
mean a package is installed. `requirements.txt` only _declares_ dependencies —
nothing is installed until you run an install step.

- `Import "X" could not be resolved` almost always = **the IDE/Pylance is pointed
  at the wrong Python interpreter**, not a missing package.
- A package can be installed in the project `.venv` but absent from the global
  Python the editor defaults to. Symptom: _every_ third-party import is flagged,
  not just one.

**Rule of thumb:** When imports won't resolve →

1. Check which interpreter is selected (VS Code: `Python: Select Interpreter` →
   pick `.\.venv\Scripts\python.exe`).
2. Confirm the package actually imports in _that_ interpreter:
   `& .venv\Scripts\python.exe -c "import X; print(X.__file__)"`.

- This is a `uv` project (`uv.lock` present). Prefer `uv sync` over
  `pip install -r requirements.txt` to keep `.venv` in sync.

---

## 2. LangGraph core mental model

**A graph IS an agent.** You pass a single **state** object from node to node.

### State

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

- `TypedDict` = a plain dict with a declared shape. At runtime it's just a dict
  (`state["messages"]`); the type is for tooling + LangGraph.
- `Annotated[type, metadata]` attaches metadata to a field. LangGraph reads the
  metadata as a **reducer**.
- **Reducer** answers: "when a node returns a new value for this field, how do I
  merge it with the old one?"
  - No reducer → **overwrite** (you'd lose history every turn).
  - `add_messages` → **append** (this is what makes conversation accumulate).

### Nodes

A node is just a function `state -> partial update`:

```python
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
```

Return only what you want to change; the reducer merges it in.

### Building → compiling

```python
builder = StateGraph(State)        # blank flowchart tied to State
builder.add_node("chatbot", fn)    # a box
builder.add_edge(START, "chatbot") # arrow from entry
builder.add_edge("chatbot", END)   # arrow to exit
graph = builder.compile()          # runnable object
```

`START`/`END` are special entry/exit markers. `compile()` turns the drawn graph
into something you can `.invoke()`/`.astream()`.

---

## 3. Chatbot vs ReAct agent — the defining difference

|         | Plain chatbot                                      | ReAct agent                                          |
| ------- | -------------------------------------------------- | ---------------------------------------------------- |
| Tools   | none                                               | has tools                                            |
| Shape   | `START → chatbot → END` (straight line, runs once) | `START → model → (tool? → model)* → END` (**loops**) |
| "Acts"? | no, only answers                                   | yes: reason → act (tool) → observe → repeat          |

**ReAct = Reason + Act.** The defining feature is the **loop** created by a
conditional edge: model decides "need a tool?" → if yes, run tool, feed result
back, loop; if no, finish.

Modern "ReAct" uses the model's **native tool-calling**, not the old
Thought/Action/Observation text format. The name is historical.

---

## 4. Conditional edges vs interrupts — DON'T conflate these

They are **different mechanisms** that often work _together_.

- **Conditional edge** = _routing_ (which node next). A function that reads state
  and returns the **name of the next node**. `tools_condition` is just the prebuilt
  one that checks "did the last AIMessage contain `tool_calls`?" → `tools` else `END`.
  You can write your own router returning any node name.

- **Interrupt** = _pausing_. `interrupt(...)` **freezes the whole graph mid-run**,
  saves state via the checkpointer, and returns control to your code. Resume later
  with `Command(resume=...)`, which becomes the return value of `interrupt()`.

```
conditional edge → chooses the path
interrupt        → pauses on the path, waits for a human, then resumes
```

**Human-in-the-loop pattern:** a tool calls `interrupt()`; the graph pauses; your
app shows the query to a human; whenever they answer (seconds or hours later) you
call `graph.stream(Command(resume=...), config)` to continue. The `thread_id` +
persistent checkpointer is what lets the conversation survive that gap.

> Interrupt/pause-resume **only works because the checkpointer saved the state.**
> Checkpointer is mandatory for human-in-the-loop.

---

## 5. Checkpointer, memory, and multi-user scaling

### Checkpointer = persistence of state between calls

- Without one, the agent is **amnesiac** — every `invoke` starts blank.
- `MemorySaver` stores snapshots in **RAM** → dev/demo only. Gone when the process
  dies; can't be shared across servers.
- Production: swap for a **persistent** checkpointer — same code, different object:

| Checkpointer    | Stores in   | Use for                    |
| --------------- | ----------- | -------------------------- |
| `MemorySaver`   | RAM         | dev/demos/tests            |
| `SqliteSaver`   | SQLite file | small single-machine       |
| `PostgresSaver` | Postgres    | **production, multi-user** |
| Redis etc.      | Redis       | high-throughput            |

### `config` / `thread_id` = _which_ conversation

```python
config = {"configurable": {"thread_id": "alice-chat-1"}}
graph.invoke({"messages": [...]}, config=config)
```

The checkpointer keys history by `thread_id`. Different threads = isolated histories.

### THE scaling insight (this changed my understanding)

**You do NOT create a new agent per user or per conversation.**

```
ONE compiled graph (the logic)  ← built once, stateless, shared by everyone
        ├── thread_id "alice-1" → Alice's history   ┐
        ├── thread_id "bob-1"   → Bob's history      ├ stored in checkpointer (Postgres)
        └── ...                                       ┘
        └── configurable: per-call settings (prompt, tools, model) → tailors behavior
```

- **Agent/graph = the _program_** (logic). Compiled once. Reused like a web server.
- **State/history = the _data_**. Stored per conversation in the checkpointer.
- One prompt = **one graph invocation** (which may loop internally LLM→tool→LLM).
  NOT multiple agents.
- Scales because logic is stateless + state is externalized → run many server
  copies behind a load balancer; any server serves any user. Real bottleneck
  becomes **LLM throughput**, not the graph.

### "Tailor/optimize responses over time" is a SEPARATE layer

The checkpointer only stores raw conversation state. To _learn/improve_ you add:

- **Long-term memory** (LangGraph `Store` API, separate from checkpointer) — facts
  across threads.
- **Retrieval (RAG)** over past conversations.
- **Feedback + evaluation** (LangSmith) to refine prompts.
  Don't expect `MemorySaver` to do any of this.

---

## 6. `create_agent` vs hand-built `StateGraph`

`create_agent` (LangChain 1.0, `langchain.agents`) is a **factory that builds a
graph for you** — it does all the `StateGraph`/`add_node`/`tools_condition`/`compile`
wiring internally and returns the **same kind of compiled graph**.

- `create_react_agent` (`langgraph.prebuilt`) = the lower-level LangGraph primitive.
- `create_agent` = its LangChain-1.0 successor; adds **middleware**, structured
  output, etc. Use `create_agent` for new code. (Only exists in LangChain 1.0+.)

**It's not "limited to conditional edges" — it gives you ONE fixed topology** (the
standard ReAct loop). You **configure** it (model, tools, prompt, checkpointer,
middleware) rather than rearranging nodes.

### Decision rule

| Use `create_agent`               | Hand-build `StateGraph`                      |
| -------------------------------- | -------------------------------------------- |
| "model + tools, loop until done" | fixed stages / branches / parallelism        |
| LLM decides the order            | **you** must control order / guarantee steps |
| one agent                        | multiple agents / specialized nodes          |
| generic assistant                | validation loops, approval gates, compliance |

**Trigger phrases that mean "outgrow the standard loop → hand-build":**
_"must do X **before** Y"_, _"a human must approve **here**"_, _"retry if the check
fails"_, _"these should run **in parallel**"_.

### When hand-built wins in production

1. Multi-step pipelines with fixed ordered stages (RAG: retrieve→rerank→generate→cite-check).
2. Multi-agent / supervisor routing between specialized sub-agents.
3. Human-in-the-loop at _specific_ controlled points.
4. Validation / retry / self-correction loops (generate→test→fix, max N tries).
5. Parallel fan-out then merge.
6. Deterministic guardrails / compliance gates that **can't** be skipped.
7. Complex structured state beyond `messages`.
8. Custom streaming/observability at named checkpoints.

**Hybrid (worth remembering):** use `create_agent` for individual agents and a
hand-built `StateGraph` to orchestrate them. The standard agent often becomes a
_node_ inside a larger custom graph. Rarely all-or-nothing.

**Start with `create_agent`** — most production agents really are just the standard
loop; hand-building adds maintenance cost for no benefit until you need it.

---

## 7. Middleware (LangChain 1.0 `create_agent`)

Hooks that run at points **around** the agent loop, without rewriting it.

| Hook              | Runs                  | For                                    |
| ----------------- | --------------------- | -------------------------------------- |
| `before_model`    | before each LLM call  | trim/summarize history, inject context |
| `after_model`     | after each LLM call   | validate output, guardrails, logging   |
| `wrap_model_call` | around the model call | retries, fallback model, caching       |
| `wrap_tool_call`  | around tool execution | auth, rate limiting, error handling    |

Prebuilt: `SummarizationMiddleware` (auto-summarize old messages to fit context),
`HumanInTheLoopMiddleware`, PII redaction, prompt caching.

**Key insight: middleware = a convenience layer over what you'd otherwise wire as
extra nodes/edges.** Each hook maps to a graph construct:

- `before_model` → a node placed **before** the model node.
- `after_model` → a node **after** the model node.
- `wrap_model_call` → logic **inside** the model node wrapping `llm.invoke`.
- `wrap_tool_call` → custom `ToolNode` / wrapper.

So middleware lets `create_agent` stay a one-liner while still doing summarization,
guardrails, approvals — the same capability at a higher level of convenience.

---

## 8. Message types

Each message carries a **role** telling the model _who said what_ — this changes how
the model treats the text (authority/source separation; e.g. a jailbreak in a
HumanMessage can be refused per SystemMessage rules).

| Message           | Role      | Purpose                                                  |
| ----------------- | --------- | -------------------------------------------------------- |
| `SystemMessage`   | system    | instructions, persona, rules (highest authority)         |
| `HumanMessage`    | user      | user input                                               |
| `AIMessage`       | assistant | model's reply; **carries `tool_calls`**                  |
| `ToolMessage`     | tool      | the **result** of a tool execution, fed back to model    |
| `RemoveMessage`   | —         | LangGraph special: **delete** a message (trim/summarize) |
| `ChatMessage`     | custom    | arbitrary role (rare)                                    |
| `FunctionMessage` | function  | **legacy/deprecated** predecessor of ToolMessage         |

The four you use constantly (System/Human/AI/Tool) form the agent loop:

```
SystemMessage (rules) → HumanMessage (ask) → AIMessage (tool_calls)
→ ToolMessage (result) → AIMessage (final answer)
```

`{"role": "user", "content": "..."}` dicts auto-convert to `HumanMessage`.
Interchangeable — use whichever reads cleaner.

---

## 9. TypedDict vs dataclass vs Pydantic

|                       | `TypedDict`             | `dataclass`      | Pydantic `BaseModel`                |
| --------------------- | ----------------------- | ---------------- | ----------------------------------- |
| Really is             | a **dict** + type hints | a regular object | object that **validates & coerces** |
| Validates at runtime? | ❌                      | ❌               | ✅                                  |
| Access                | `x["k"]`                | `x.k`            | `x.k`                               |
| Cost                  | zero                    | ~zero            | small (validation)                  |

**The deciding rule: does the data cross a trust boundary (from LLM / user / API)?**

- **Yes → Pydantic.** Must validate untrusted input.
- **No, and it's graph state → TypedDict.** Ecosystem default; dict-based; merged by reducers.
- **No, internal code data → dataclass.** Lightweight, no dependency, real objects.

**Production pattern:**

```
Graph state            → TypedDict
LLM structured output  → Pydantic BaseModel   (the big one)
Tool input schemas     → Pydantic (often auto from type hints)
Internal/config        → dataclass
```

Pydantic for structured output because model text is untrusted (validates/coerces
`"23"`→`23.0`) and `Field(description=...)` feeds the schema/prompt to the model.

---

## 10. MCP (Model Context Protocol) servers

`FastMCP` + `@mcp.tool()` turns plain functions into tools an LLM can call.

- **Type hints** (`a: int -> int`) define the tool's **schema** (not just docs).
- **Docstring** becomes the tool's **description the LLM sees** to decide usage.
- `@mcp.tool()` is a **decorator** that _registers_ the function as a tool.

### `if __name__ == "__main__":`

`__name__` is auto-set by Python:

- run the file directly (`python math_server.py`) → `__name__ == "__main__"` → block runs.
- imported by another file → `__name__ == "math_server"` → block skipped.
  Means "only start the server if this file is the program being run, not when imported."

### Transports — KEY operational difference

|                        | `stdio`                       | `streamable_http`            |
| ---------------------- | ----------------------------- | ---------------------------- |
| Who starts the server  | **the client**, automatically | **you**, manually beforehand |
| Must be running first? | No (spawned on demand)        | **Yes**                      |
| Config has             | a `command` to launch         | a `url` to connect to        |
| Lifetime               | dies with the client run      | long-lived                   |
| Sharing                | private per client            | shared by many clients       |

`stdio` = local launch-on-demand tools. HTTP = shared/remote services that must be
up independently (start `weather_server.py` first, then `client.py`).

### MCP tools are async-only

`NotImplementedError: StructuredTool does not support sync invocation` =
MCP tools implement `_arun` but not `_run`. **Fix: drive the agent async** — use
`await agent.ainvoke(...)` / `astream`, never `invoke`/`stream`.

---

## 11. invoke vs stream — production chat shape

- `invoke` = blocking, returns the whole answer at once. Dev/notebook only.
- `astream` = yields chunks as generated → the "typing" effect. **Always stream in
  production** (same total time, feels instant).

```python
async for chunk, meta in graph.astream(
    {"messages": [{"role": "user", "content": "..."}]},
    config=config,
    stream_mode="messages",   # token-by-token
):
    print(chunk.content, end="", flush=True)
```

`stream_mode`:

- `"values"` → full state snapshot after each step (good for printing latest msg).
- `"updates"` → only what each node changed.
- `"messages"` → token-by-token (chat streaming).

**Efficiency insight:** you send only the **new** user message, not the whole
transcript — the checkpointer loads prior history via `thread_id` and `add_messages`
appends. The server holds history; the client sends one line. Also: send only
`response["messages"][-1]` to the user, not the whole list.

**Production shape:** Browser → async FastAPI endpoint → `graph.astream(msg, {thread_id})`
with Postgres checkpointer → stream tokens back over SSE/WebSocket. One event loop
serves many users concurrently.

---

## 12. asyncio

**Problem it solves:** most agent work is _waiting_ (LLM, network, DB). Sync code
**blocks** — freezes on the line doing nothing. asyncio stops wasting that wait.

**Core idea:** asyncio is NOT threads/parallelism. It's a **single worker (the event
loop)** juggling many tasks. When a task hits a wait, it says "go do something else"
and hands control back; the loop runs another task; resumes the first when its result
arrives. (The waiter serving many tables analogy.)

- `async def` → a **coroutine**: a function allowed to **pause and resume**, keeping
  its locals frozen. Calling it doesn't run it — it makes a coroutine object.
- `await` → the pause point: "suspend me here, let others run, wake me when ready."
  Only usable inside `async def`; only on awaitable (`a`-prefixed) things.
- `asyncio.run(main())` → starts the event loop, runs the coroutine, shuts it down.
  The bridge from sync into async.

**Two beginner traps:**

1. `await` does NOT make one call faster — the payoff is **concurrency** (many calls
   in flight). For a single sequential script, async isn't faster.
2. Sequential `await`s are still sequential. To overlap, use:
   ```python
   a, b = await asyncio.gather(fetch_one(), fetch_two())  # both at once
   ```
   This is the real superpower — hundreds of LLM calls in flight at once.

**Practical rule for agents:** async is for **I/O waiting**. Never put a heavy CPU
loop inside `async def` without yielding — it freezes the whole event loop (and in a
server, every user). Push CPU-heavy work to `multiprocessing`.

---

## 13. Coroutines under the hood

A coroutine is a **state machine**: at each `await` it yields control and saves
"where am I paused" + its locals (in a heap-allocated frame object). Resume restores
locals and jumps to the line after the `await`. It's an evolution of generators
(`yield` does the same pause-and-remember).

**Cooperative & voluntary:** a coroutine only pauses _at an `await`_. Between awaits
it runs uninterrupted. Nothing forces it to yield. (← crux of the Go comparison.)

---

## 14. Concurrency vs parallelism (the unlock)

They're **two different axes, not opposites:**

- **Concurrency** = how you **structure** work — many independent tasks that _can_
  interleave.
- **Parallelism** = how you **execute** — multiple tasks at the literal same instant
  on multiple cores.

|            | Not parallel                                 | Parallel                                  |
| ---------- | -------------------------------------------- | ----------------------------------------- |
| Concurrent | **asyncio** (many tasks, take turns, 1 core) | **goroutines** (many tasks, across cores) |

asyncio = concurrent but NOT parallel. Go = concurrent AND parallel.

---

## 15. The GIL (Global Interpreter Lock)

**One lock in CPython that lets only one thread execute Python bytecode at a time.**
8 threads on 8 cores doing math → ~1x, not 8x (they serialize).

- Exists because CPython uses **reference counting** for memory; one coarse lock is
  simpler/faster than locking every object.
- **Released during I/O** (network/disk/sleep — OS handles the wait) and **inside C
  extensions** that release it (NumPy etc.).

| Workload                         | Bottleneck | GIL hurts?                     | Use                      |
| -------------------------------- | ---------- | ------------------------------ | ------------------------ |
| **I/O-bound** (LLM, network, DB) | waiting    | **No** (released during waits) | asyncio / threads        |
| **CPU-bound** (math, parsing)    | computing  | **Yes** (threads serialize)    | multiprocessing / C libs |

→ asyncio is perfect for agent code: all I/O waiting, GIL never in the way.

### Real parallelism in Python

- **`multiprocessing`** — separate processes, each own interpreter + own GIL → true
  multi-core. Cost: data must be **pickled** between processes.
- **C extensions** (NumPy/Pandas/PyTorch) release the GIL internally.
- **Free-threaded Python (3.13+/3.14)** — experimental GIL-removed build; real thread
  parallelism. Still maturing; don't rely on it in production yet. (This repo's venv
  is on Python 3.14.)

```
I/O waiting (agents)  → asyncio
CPU-bound parallel    → multiprocessing (or C libs / free-threaded)
mixed                 → asyncio for I/O + offload CPU to processes
```

---

## 16. Go goroutines vs asyncio

Similar philosophy (lightweight, scheduled tasks, great I/O concurrency), but Go is
fundamentally more powerful:

|                              | asyncio                                        | goroutines                               |
| ---------------------------- | ---------------------------------------------- | ---------------------------------------- |
| Concurrent                   | ✅                                             | ✅                                       |
| **True multi-core parallel** | ❌ (GIL, 1 loop, 1 core)                       | ✅                                       |
| Scheduling                   | **cooperative** (yield at `await`)             | **preemptive** (runtime interrupts)      |
| Syntax                       | explicit `async`/`await` ("function coloring") | implicit (`go f()`)                      |
| Mapping                      | 1 loop on 1 core                               | M goroutines : N OS threads : many cores |

### Preemptive vs cooperative — who decides when a task pauses

- **Cooperative (asyncio):** task **voluntarily** yields, only at `await`. Scheduler
  is polite but powerless. A CPU loop with no `await` **freezes everything**.
- **Preemptive (goroutines / OS threads):** the scheduler can **forcibly interrupt** a
  running task mid-execution, save its state, switch. No task can monopolize the CPU.
  "Preempt" = seize the CPU back whether the task likes it or not. More robust.

### How Go is concurrent AND parallel: the G–M–P / M:N scheduler

- **G** = goroutine (tiny: starts ~2KB growable stack). You spawn hundreds of thousands.
- **M** = OS thread (runs on a core).
- **P** = processor/context holding a **run queue** of runnable G's.

```
many goroutines (M)  → Go scheduler → ~N OS threads (one per core) → N cores in parallel
```

### CRITICAL correction to my mental model

**One goroutine runs on one core at a time. Never split across cores.** Parallelism =
**different** goroutines on **different** cores simultaneously — NOT many cores
ganging up on one task.

- ❌ Not: 4 cores → task1 together → task2 together.
- ✅ Yes: core1→task1, core2→task2, core3→task3, all at once.

→ One task = one goroutine = one core (others idle). **To make one big job use many
cores, YOU split it into many goroutines** (e.g. process different slices of a list).
Switching is per-core: when a goroutine waits/is preempted, that core swaps in another
_ready_ goroutine. Same "one task per worker at a time" as asyncio — Go just has many
workers (cores) instead of one.

### Where goroutine state is stored between scheduling

- **Locals/data** → in the goroutine's own **small growable stack** (heap memory the
  runtime manages). When paused, the stack just **stays in place** — nothing copied out.
- **Execution position** (PC/SP + registers) → saved into the goroutine's **`g` struct**
  (`sched`/`gobuf` field).
- A **context switch** = copy live registers into the paused G's struct, load the next
  G's saved registers into the CPU. Done in **user space** by the Go runtime → ~ns,
  far cheaper than an OS/kernel thread switch.
- A paused-but-runnable goroutine waits in a **P's run queue** until a thread picks it up.

**Why Go saves full registers but asyncio only saves a state index:** asyncio suspends
only at `await` → just needs "which await am I at" (a state-machine index in a heap
frame). Go can interrupt **anywhere** → must save the full raw CPU register state, like
the OS does — just in user space, which is why it's so cheap.

---

## Quick decision cheat-sheet

- **Import won't resolve** → wrong interpreter, point IDE at `.venv`.
- **MCP tool error (sync invocation)** → use `await ainvoke`/`astream`.
- **Need memory across calls** → add a checkpointer; Postgres in prod, not MemorySaver.
- **Many users** → one compiled graph + per-user `thread_id`, NOT an agent per user.
- **Standard "model+tools loop"** → `create_agent`. **Need ordering/branch/parallel/
  approval/retry** → hand-build `StateGraph`.
- **Data from LLM/user/API** → Pydantic. **Graph state** → TypedDict. **Internal** →
  dataclass.
- **Cross-cutting behavior on create_agent** → middleware (= nodes you'd otherwise wire).
- **Production chat** → `astream` + send only new message + stream tokens over SSE/WS.
- **I/O-bound** → asyncio (GIL irrelevant). **CPU-bound parallel** → multiprocessing.
- **Never** put a heavy CPU loop in an `async def` without yielding (freezes the loop).
