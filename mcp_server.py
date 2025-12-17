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
        TextContent(type="text", text=f"Echo: {message}")
    ]

if __name__ == "__main__":
    # Run server with HTTP transport on port 8001
    asyncio.run(app.run(transport="http", host="127.0.0.1", port=8001))
