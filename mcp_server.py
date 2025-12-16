from fastmcp import FastMCP
from mcp.types import TextContent
import asyncio

app = FastMCP(
    name="test-mcp-server",
    version="0.1.0",
)

@app.tool(
    name="echo",
    description="Echo a message",
)
async def echo(message: str):
    return [
        TextContent(text=f"Echo: {message}")
    ]

if __name__ == "__main__":
    asyncio.run(app.run())

