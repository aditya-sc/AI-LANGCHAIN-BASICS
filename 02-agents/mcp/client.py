# MCP client: build one agent over tools served by TWO MCP servers, then ask it
# a math question.  Concepts: NOTES.md §10 (MCP transports, async-only) and
# §6 (create_agent) and §12 (asyncio).
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()  # loads TAVILY_API_KEY etc. from a local .env (never committed)

import asyncio
import time

# MCP tools are async-only: they implement _arun but not _run, so the whole agent
# must be driven async with `await agent.ainvoke(...)` — never sync .invoke
# (NOTES.md §10). asyncio.run(main()) at the bottom is the sync→async bridge.
async def main():
    t_start = time.perf_counter()

    # One client, two servers — note the two different transports (NOTES.md §10):
    client=MultiServerMCPClient(
        {
            "math":{
                # stdio: client launches this process on demand via `command`.
                # math_server.py does NOT need to be started beforehand.
                "command":"python",
                "args":["math_server.py"],
                "transport":"stdio",
            },
            "weather":
            {
                # streamable_http: connect by url to an already-running server.
                # Start `python weather_server.py` first or this will fail.
                "url":"http://localhost:8000/mcp",
                "transport":"streamable_http",
            }
        }
    )
    t0 = time.perf_counter()
    tools=await client.get_tools()  # discover tools from both servers (async)
    t1 = time.perf_counter()

    llm=init_chat_model("ollama:qwen3:8b")
    # create_agent = the standard ReAct loop (model + tools, loop until done)
    # wired for you — see NOTES.md §6 for when to hand-build a StateGraph instead.
    agent=create_agent(model=llm, tools=tools)
    t2 = time.perf_counter()

    math_response=await agent.ainvoke(
        {
            "messages":[
                {
                    # plain dict auto-converts to a HumanMessage (NOTES.md §8)
                    "role":"user",
                    "content":"What's (3 + 5) x 12?"
                }
            ]
        }
    )
    t3 = time.perf_counter()

    # send only the last message to the user, not the whole transcript (NOTES.md §11)
    print("Math response:", math_response["messages"][-1].content)

    # The timings make the bottleneck visible: tool loading and agent building are
    # near-instant; almost all wall-clock time is the LLM inference inside ainvoke.
    print("\n--- timings (seconds) ---")
    print(f"load MCP tools : {t1 - t0:6.2f}")
    print(f"build agent    : {t2 - t1:6.2f}")
    print(f"agent.ainvoke  : {t3 - t2:6.2f}   <-- LLM inference lives here")
    print(f"total          : {t3 - t_start:6.2f}")

asyncio.run(main())
