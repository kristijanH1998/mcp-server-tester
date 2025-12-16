import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from mcp.client import Client
from mcp.client.stdio import StdioTransport

