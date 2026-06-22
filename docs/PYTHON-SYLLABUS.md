# Python + FastAPI Syllabus — for the AI Engineer transition

> **Who this is for:** an experienced dev (C# / Java, some Go / JS) who knows
> programming cold but is new to _Python idioms_. This is **not** a "learn to
> code" course — it's a map of the gaps that project-work and LeetCode leave open.
>
> **How to use it:** don't study this front-to-back in isolation. Build the
> [`PROJECTS.md`](./PROJECTS.md) work, and when a project touches a topic below,
> stop and learn that topic _properly_ (1–2 hrs), then apply it the same day.
> Check the box when you can **explain it cold AND have used it in your own code.**
>
> **Where this fits:** [`SYLLABUS.md`](./SYLLABUS.md) is the _AI_ knowledge map,
> [`PROJECTS.md`](./PROJECTS.md) is the portfolio that proves it — this file closes
> the _Python language_ gaps you'll hit while building both.

**Legend:** 🔴 must-know before Project 1 · 🟡 learn during Projects 1–2 · 🟢 nice-to-have

---

## 0 — Mental model shift (you already program; rewire these)

Coming from C#/Java, these are the things that will trip you up:

- [ ] 🔴 **Everything is an object, functions are first-class** — functions are values
      you pass around (like C# delegates / JS functions), not just methods on a class.
- [ ] 🔴 **No interfaces/`new`, no `public/private`** — convention over enforcement
      (`_private` is a hint, not a rule). Duck typing instead of nominal typing.
- [ ] 🔴 **Indentation is syntax**, truthiness (`if my_list:`), and `None` ≠ `null`
      semantics (use `is None`, never `== None`).
- [ ] 🔴 **The Pythonic way matters** — `for x in items:` not index loops;
      comprehensions over manual `.append()` loops. Reviewers read for this.

---

## 1 — Core language idioms (the LeetCode blind spots) 🔴

These are exactly what you flagged. They appear everywhere in AI/agent code.

- [ ] 🔴 **`*args` / `**kwargs`** — variadic args, packing/unpacking, `func(**config)`,
  `{**a, **b}`merge. Why frameworks use`**kwargs` for pass-through config.
- [ ] 🔴 **Callables & first-class functions** — passing functions as args, returning
      functions, `callable(x)`, why a "tool registry" is `dict[str, Callable]`.
- [ ] 🔴 **Decorators** — what `@decorator` desugars to, writing one, `functools.wraps`,
      decorators with arguments. _(FastAPI routes, caching, retries are all decorators.)_
- [ ] 🔴 **Comprehensions & generators** — list/dict/set comprehensions, `yield`,
      generator expressions, why generators matter for streaming LLM tokens.
- [ ] 🟡 **Closures & `functools`** — `partial`, `lru_cache`, late-binding gotcha.
- [ ] 🟡 **Unpacking & star-expressions** — `a, *rest = items`, tuple unpacking in loops.

---

## 2 — Types, data modeling & OOP 🔴

- [ ] 🔴 **Type hints** — `list[str]`, `dict[str, int]`, `Optional`, `Union`/`|`,
      `Callable`, `Any`. Python types are optional but **everything in modern AI
      code is typed** (and FastAPI _requires_ them to work).
- [ ] 🔴 **Dataclasses** — `@dataclass` for plain data holders (your Java POJO / C# record).
- [ ] 🔴 **`Pydantic` v2** — the big one. `BaseModel`, validation, `Field`, settings.
      This is how FastAPI defines request/response schemas. Learn it well.
- [ ] 🟡 **Abstraction / ABCs** — `abc.ABC`, `@abstractmethod`, `Protocol` (structural
      typing — closer to Go interfaces than Java's). Use for `get_model()` provider shim.
- [ ] 🟢 **`Enum`**, `NamedTuple`, `TypedDict` — when each beats a dataclass.

---

## 3 — Idiomatic patterns & resource management 🟡

- [ ] 🔴 **Context managers** — `with open(...)`, why (deterministic cleanup, like
      C# `using`), writing your own with `@contextmanager`.
- [ ] 🔴 **Exceptions** — `try/except/else/finally`, custom exception classes,
      catching narrowly, `raise ... from e`.
- [ ] 🟡 **Modules & packaging** — `import` system, `__init__.py`, relative vs absolute
      imports, `if __name__ == "__main__"`, project layout (`src/` layout).
- [ ] 🟡 **Virtual envs & deps** — `venv`, `pip`, `requirements.txt`, and ideally
      **`uv`** (fast, modern) or `poetry`. Pin your versions.
- [ ] 🟢 **Iterators & `itertools`**, `collections` (`defaultdict`, `Counter`, `deque`).

---

## 4 — Async Python 🟡 (critical for FastAPI & LLM calls)

- [ ] 🔴 **`async` / `await`** — coroutines, the event loop, why I/O-bound LLM/DB calls
      are async. Mental model is close to C#'s `async/await` — lean on that.
- [ ] 🟡 **`asyncio` basics** — `gather` for concurrent calls (parallel tool calls!),
      `asyncio.run`, not blocking the loop with sync code.
- [ ] 🟢 **Sync vs async libraries** — knowing when a library blocks the event loop.

---

## 5 — FastAPI 🟡 (Project 1 serving layer)

Learn this when you hit "Serve via FastAPI" in Project 1. Don't pre-learn it.

- [ ] 🔴 **First endpoint** — `@app.get` / `@app.post`, path & query params, `uvicorn`.
- [ ] 🔴 **Request/response models** — Pydantic models in and out, automatic validation,
      the auto-generated `/docs` (Swagger). This is FastAPI's killer feature.
- [ ] 🔴 **Dependency injection** — `Depends()` for shared resources (DB clients, the
      RAG retriever, auth). Cleaner than wiring it manually everywhere.
- [ ] 🟡 **Async endpoints** — `async def` routes, streaming responses
      (`StreamingResponse`) for token-by-token LLM output.
- [ ] 🟡 **Error handling** — `HTTPException`, exception handlers, status codes.
- [ ] 🟢 **Middleware, CORS, background tasks, lifespan** events (startup/shutdown).

---

## 6 — Tooling & quality 🟡 (do this once, benefit forever)

- [ ] 🔴 **`ruff`** — linter + formatter (replaces black/flake8/isort). One config, fast.
- [ ] 🟡 **`mypy` or `pyright`** — static type checking. Catches the bugs your C#
      compiler would have caught for free.
- [ ] 🟡 **`pytest`** — fixtures, parametrize, mocking. Your eval suites lean on this.
- [ ] 🟢 **`pdb` / debugger**, `logging` (not `print`), `.env` via `pydantic-settings`.

---

## 7 — AI-stack Python you'll meet in the projects 🟢

Learn as-needed; these are libraries, not language. Mentioned so they're not a surprise.

- [ ] `numpy` basics (vectors, shapes) — embeddings are arrays.
- [ ] `sentence-transformers`, vector clients (`qdrant-client` / `pgvector`).
- [ ] `httpx` (async HTTP), `tenacity` (retries) — robust LLM API calls.
- [ ] Observability SDKs (`langfuse`) and eval (`ragas`) — Project 1.

---

## Suggested rhythm

| When                        | Focus                                                              |
| --------------------------- | ------------------------------------------------------------------ |
| **Now (Project 0 done)**    | Backfill §1 + §2 (your flagged gaps) — 2–3 focused sessions        |
| **Start of Project 1**      | §3 context managers & errors; §2 Pydantic + ABCs for `get_model()` |
| **Mid Project 1 (serving)** | §4 async + §5 FastAPI together                                     |
| **Throughout**              | §6 tooling set up once on day 1; §7 per library as you import it   |

**Good free references** (skim, don't binge):

- _Real Python_ articles (decorators, `**kwargs`, async) — best for "coming from another language."
- _FastAPI official docs_ — genuinely excellent, tutorial-first.
- _Pydantic v2 docs_ — short, worth reading end-to-end.
- _Fluent Python_ (book, Ramalho) — the deep dive once idioms click; not a starting point.

> **Bottom line:** your project-driven + LeetCode approach is right for someone with
> your background. This file just closes the idiom gaps those two miss — study it
> _alongside_ the build, never instead of it.

---

*Companion files: [`SYLLABUS.md`](./SYLLABUS.md) — the AI knowledge map · [`PROJECTS.md`](./PROJECTS.md) — the portfolio that proves it.*
