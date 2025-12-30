# Mini MCP Server Tester

This project is a lightweight, full-stack web application for testing and evaluating
Model Context Protocol (MCP) servers. It allows users to register MCP server endpoints,
inspect available tools, run repeated tool invocations, and measure response latency
and reliability over time.

## How to Start the Project

### 1. Install Dependencies

Ensure Python 3.10+ is installed. Install required Python packages by running:

pip install fastapi uvicorn fastmcp mcp python-dotenv

### 2. Configure Environment Variables
Copy the example environment file with:

cp .env.example .env

All variables have safe defaults, so no changes are required for local development.

### 3. Start the MCP Test Server

Run the sample MCP server with:

python mcp_server.py

This starts a FastMCP server on http://127.0.0.1:8001/mcp with a simple echo tool.


### 4. Start the Backend API

In a separate terminal, run:
uvicorn backend:app --reload --port 8000

This starts the FastAPI backend used to manage MCP servers and experiments.

### 5. Open the Frontend

Open the frontend file directly in your browser:

<browser_name> index.html

You should now see an interface that allows you to register MCP servers, inspect tools,
run experiments, and view timing results.

## Design Decisions and Trade-offs
### Architecture

The application is structured as a three-component system:
MCP Server: A simple FastMCP server used as a test target.
Backend (FastAPI): Acts as an MCP client manager, experiment runner, and result store.
Frontend (HTML/JS): A minimal UI for interacting with the backend.
This separation keeps the system modular.

### Persistent MCP Clients

A persistent MCP client is maintained per registered server to ensure tool discovery
and session initialization behave correctly. This avoids issues with lazy tool loading
that can occur when clients are created per request.

### In-memory Storage

Server registrations and experiment results are stored in memory:
Pros: Simple, fast, and sufficient for an MVP.
Data is preserved on backend restart thanks to SQLite persistence.

### Experiment Execution

Experiments execute tool calls sequentially rather than in parallel:
This simplifies timing accuracy and avoids concurrency concerns.
Parallel execution could be added in a future iteration.

### Configuration via Environment Variables

Runtime configuration (ports, limits, CORS) is handled via environment variables:
Supports reproducibility and deployment flexibility. A .env.example file documents all required configuration.

## Unit Tests

Pytest is used to perform simple unit tests on server registration, client creation (with mock MCP client only to confirm accurate API and SQLite behavior), and database and backend functionality.

## Use of AI Coding Tools

AI coding tools were used as an assistance mechanism, not as a replacement for
understanding or design decisions:

ChatGPT was used to generate boilerplate code patterns, refine FastAPI routes,
and assist with frontend JavaScript structure.

Google Gemini was used for background research on MCP concepts and framework
behavior.