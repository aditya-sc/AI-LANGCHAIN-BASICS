# MCP server exposing math tools.  (See NOTES.md §10 — MCP servers.)
# FastMCP + @mcp.tool() turns plain functions into tools an LLM can call:
#   - the type hints (a: int, b: int -> int) define the tool's *schema*
#   - the docstring becomes the tool *description* the LLM sees to decide usage
from mcp.server.fastmcp import FastMCP

mcp=FastMCP("MathServer")

@mcp.tool()  # decorator that *registers* this function as a callable tool
def add(a:int,b:int)->int:
    """
    Add two numbers
    """
    return a+b

@mcp.tool()
def multiply(a:int,b:int)->int:
    """
    Multiply two numbers
    """
    return a*b

# `__name__ == "__main__"` is True only when run directly (python mathserver.py),
# False when imported — so the server starts only when this file is the program.
if __name__=="__main__":
    # stdio transport: the *client* spawns this process on demand (NOTES.md §10).
    # Nothing to start manually — client.py launches it via a `command`.
    mcp.run(transport="stdio")
