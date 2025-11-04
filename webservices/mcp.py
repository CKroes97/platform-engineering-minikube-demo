from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import Any, Dict
import httpx

app = FastAPI(title="My MCP Server", version="0.1.0")


# MCP "ping" tool schema
class PingArgs(BaseModel):
    message: str


@app.post("/tools/time_now")
async def ping_tool() -> str:
    url = "http://time_now.default.svc.cluster.local:80"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
    except httpx.RequestError:
        return {"error": "request failed"}

    try:
        payload = resp.json()
    except ValueError:
        payload = resp.text

    return {"status_code": resp.status_code, "response": payload}


@app.get("/manifest")
async def manifest():
    return {
        "name": "my-mcp-server",
        "version": "0.1.0",
        "tools": [
            {
                "name": "time_now",
                "description": "Returns current time in ISO format",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            }
        ],
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=False)
