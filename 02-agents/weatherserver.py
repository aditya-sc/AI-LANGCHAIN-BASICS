# MCP server exposing a weather tool.  (See NOTES.md §10 — MCP servers.)
# Same FastMCP pattern as mathserver.py, but a *different transport*.
from mcp.server.fastmcp import FastMCP

mcp=FastMCP("WeatherServer")

@mcp.tool()
def get_weather(location:str)->str:
    """
    Get weather in location
    """
    return f"It's sunny in {location}"

if __name__=="__main__":
    # streamable-http transport: unlike stdio, *you* must start this server
    # manually and keep it running before the client connects (NOTES.md §10).
    # It's a long-lived service at http://localhost:8000/mcp, shareable by many
    # clients — the client reaches it by `url`, not by spawning a command.
    mcp.run(transport="streamable-http")
