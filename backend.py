# run with: uvicorn backend:app --host 127.0.0.1 --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastmcp import Client

app = FastAPI()

# Enable CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow requests from any origin
    allow_methods=["*"],      # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],      # allow any headers
)

# MCP client pointing to HTTP MCP server
client = Client("http://127.0.0.1:8001/mcp")

@app.on_event("startup")
async def startup():
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
        arguments=req.arguments
    )



