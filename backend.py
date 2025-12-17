from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastmcp import Client

app = FastAPI()

# Create a client pointing to your HTTP MCP server
client = Client("http://127.0.0.1:8001/mcp")

@app.on_event("startup")
async def startup():
    # Connect on startup using async context
    await client.__aenter__()

@app.on_event("shutdown")
async def shutdown():
    await client.__aexit__(None, None, None)

@app.get("/tools")
async def list_tools():
    return await client.list_tools()

class ToolCall(BaseModel):
    tool: str
    arguments: dict

@app.post("/call")
async def call_tool(req: ToolCall):
    return await client.call_tool(
        name=req.tool,
        arguments=req.arguments,
    )
