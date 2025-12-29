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

from db import init_db
from db import get_conn
from datetime import datetime
import json

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

def serialize_call_result(result):
    """
    Convert CallToolResult into JSON-serializable data.
    """
    if hasattr(result, "content"):
        return [
            {
                "type": c.type,
                "text": getattr(c, "text", None)
            }
            for c in result.content
        ]
    return result

# -------------------------
# Server registry
# -------------------------
@app.post("/servers")
async def register_server(req: RegisterServer):
    server_id = str(uuid4())

    client = await create_and_warm_client(req.url)
    mcp_clients[server_id] = client
    mcp_servers[server_id] = req.url

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO servers VALUES (?, ?, ?)",
            (server_id, req.url, datetime.utcnow().isoformat())
        )
        conn.commit()

    return {"id": server_id, "url": req.url}

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
            responses.append(serialize_call_result(resp))

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

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experiment_id,
                req.server_id,
                req.tool,
                json.dumps(req.arguments),
                req.iterations,
                result["avg_ms"],
                result["errors"],
                json.dumps(result["timings_ms"]),
                json.dumps(result["responses"]),
                datetime.utcnow().isoformat(),
            )
        )
        conn.commit()

    return result

@app.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    from db import get_conn
    import json

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM experiments WHERE id = ?",
            (experiment_id,)
        ).fetchone()

    if not row:
        return {"error": "experiment not found"}

    (
        id, server_id, tool, arguments,
        iterations, avg_ms, errors,
        timings_ms, responses, created_at
    ) = row

    return {
        "experiment_id": id,
        "server_id": server_id,
        "tool": tool,
        "arguments": json.loads(arguments),
        "iterations": iterations,
        "avg_ms": avg_ms,
        "errors": errors,
        "timings_ms": json.loads(timings_ms),
        "responses": json.loads(responses),
        "created_at": created_at,
    }

# -------------------------
# Graceful shutdown
# -------------------------
@app.on_event("shutdown")
async def shutdown():
    for client in mcp_clients.values():
        await client.__aexit__(None, None, None)

# -------------------------
# Initialize database when starting the app
# -------------------------
@app.on_event("startup")
async def startup():
    init_db()

    with get_conn() as conn:
        rows = conn.execute("SELECT id, url FROM servers").fetchall()

    for server_id, url in rows:
        client = await create_and_warm_client(url)
        mcp_servers[server_id] = url
        mcp_clients[server_id] = client






