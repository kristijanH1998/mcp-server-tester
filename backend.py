# Run with: uvicorn backend:app --reload --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastmcp import Client
from uuid import uuid4
from statistics import mean
import time

from dotenv import load_dotenv
import os

load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
MAX_EXPERIMENT_ITERATIONS = int(os.getenv("MAX_EXPERIMENT_ITERATIONS", 100))
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")

app = FastAPI()

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOW_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# In-memory state
# -------------------------
mcp_servers = {}      # server_id -> url
mcp_clients = {}     # server_id -> Client
experiments = {}     # experiment_id -> results

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
# MCP helpers
# -------------------------
async def create_and_warm_client(url: str) -> Client:
    """
    Create a persistent MCP client and force full tool initialization.
    """
    client = Client(url)
    await client.__aenter__()

    # 🔥 CRITICAL: force handshake + tool discovery
    try:
        await client.list_tools()
    except Exception:
        pass

    return client

# -------------------------
# Server registry
# -------------------------
@app.post("/servers")
async def register_server(req: RegisterServer):
    server_id = str(uuid4())

    client = await create_and_warm_client(req.url)

    mcp_servers[server_id] = req.url
    mcp_clients[server_id] = client

    return {
        "id": server_id,
        "url": req.url,
    }

@app.get("/servers")
async def list_servers():
    return mcp_servers

# -------------------------
# Tools
# -------------------------
@app.get("/servers/{server_id}/tools")
async def list_tools(server_id: str):
    client = mcp_clients[server_id]
    return await client.list_tools()

# -------------------------
# Experiments
# -------------------------
@app.post("/experiments")
async def run_experiment(req: ExperimentRequest):
    if req.iterations > MAX_EXPERIMENT_ITERATIONS:
        return {
            "error": f"iterations must be <= {MAX_EXPERIMENT_ITERATIONS}"
        }

    client = mcp_clients[req.server_id]

    timings = []
    responses = []
    errors = 0

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
        "server": mcp_servers[req.server_id],
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

# -------------------------
# Graceful shutdown
# -------------------------
@app.on_event("shutdown")
async def shutdown():
    for client in mcp_clients.values():
        await client.__aexit__(None, None, None)






