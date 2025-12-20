# Run with: uvicorn backend:app --reload --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastmcp import Client
from uuid import uuid4
from contextlib import asynccontextmanager
from statistics import mean
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# In-memory storage (MVP)
# -------------------------
mcp_servers = {}      # server_id -> url
experiments = {}     # experiment_id -> results

# -------------------------
# MCP client helper
# -------------------------
@asynccontextmanager
async def mcp_client(url: str):
    client = Client(url)
    await client.__aenter__()
    try:
        yield client
    finally:
        await client.__aexit__(None, None, None)

# -------------------------
# Models
# -------------------------
class RegisterServer(BaseModel):
    url: str

class ExperimentRequest(BaseModel):
    server_id: str
    tool: str
    arguments: dict
    iterations: int

# -------------------------
# Server registry
# -------------------------
@app.post("/servers")
async def register_server(req: RegisterServer):
    server_id = str(uuid4())
    mcp_servers[server_id] = req.url
    return {"id": server_id, "url": req.url}

@app.get("/servers")
async def list_servers():
    return mcp_servers

# -------------------------
# Tools
# -------------------------
@app.get("/servers/{server_id}/tools")
async def list_tools(server_id: str):
    url = mcp_servers[server_id]
    async with mcp_client(url) as client:
        return await client.list_tools()

# -------------------------
# Experiments
# -------------------------
@app.post("/experiments")
async def run_experiment(req: ExperimentRequest):
    url = mcp_servers[req.server_id]

    timings = []
    responses = []
    errors = 0

    async with mcp_client(url) as client:
        for _ in range(req.iterations):
            start = time.perf_counter()
            try:
                resp = await client.call_tool(
                    name=req.tool,
                    arguments=req.arguments
                )
                responses.append(resp)
            except Exception as e:
                errors += 1
                responses.append({"error": str(e)})
            finally:
                timings.append(time.perf_counter() - start)

    experiment_id = str(uuid4())
    result = {
        "experiment_id": experiment_id,
        "server": url,
        "tool": req.tool,
        "iterations": req.iterations,
        "avg_ms": mean(timings) * 1000,
        "errors": errors,
        "timings_ms": [t * 1000 for t in timings],
        "responses": responses,
    }

    experiments[experiment_id] = result
    return result

@app.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    return experiments[experiment_id]




