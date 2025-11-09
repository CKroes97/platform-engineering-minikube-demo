import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Configuration
LLAMA_BACKEND = os.getenv(
    "LLAMA_BACKEND", "http://host.minikube.internal:39443/v1/chat/completions"
)

tools = [
            {
            "name": "time_now",
            "description": "Returns current time in ISO format",
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": {},
                }
            }
        ]

def add_system_message(messages: list[dict], new_content: str):
    msg = {"role": "system", "content": new_content}
    updated = False
    for message in messages:
        if message["role"] == "system":
            message["content"] += " \n" + new_content
            updated=True

    if not updated:
        messages.insert(0, msg)

    return messages


# Example simple policy function
def enforce_policy(payload: dict) -> tuple[bool, str]:
    """
    Apply inline policy enforcement on the request.
    Return (allowed: bool, message: str)
    """
    messages = payload.get("messages", [])
    for msg in messages:
        content = msg.get("content", "").lower()
        # Example policies
        if "password" in content:
            return (
                False,
                "Policy violation: request contains sensitive keyword 'password'.",
            )
        if len(content) > 2000:
            return False, "Policy violation: input too long."
    return True, "Allowed"


@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    try:
        # Parse incoming request
        body = await request.json()
        allowed, reason = enforce_policy(body)
        if not allowed:
            return JSONResponse(status_code=403, content={"error": reason})
        
        body["messages"] = add_system_message(body.get("messages", []), f"You can acces the tools: {str(tools)}")

        # Forward to actual LLaMA backend
        async with httpx.AsyncClient(timeout=60.0) as client:
            llama_response = await client.post(
                LLAMA_BACKEND, json=body, headers={"Content-Type": "application/json"}
            )

        return Response(
            content=llama_response.content,
            status_code=llama_response.status_code,
            media_type="application/json",
        )

    except Exception:
        return JSONResponse(status_code=500, content="An error occurred")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("llama-proxy:app", host="0.0.0.0", port=80)
