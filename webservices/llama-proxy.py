import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

app = FastAPI()

# Configuration
LLAMA_BACKEND = os.getenv(
    "LLAMA_BACKEND", "http://host.minikube.internal:39443/v1/chat/completions"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "time_now",
            "description": "Returns current time in ISO format",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]


def tools_matched(tools: list[dict], response_json: dict) -> set[str]:
    tool_names = {tool["function"]["name"] for tool in tools}
    print("Available tool names:", tool_names)
    message = response_json["choices"][0]["message"]
    called_tools = {tool["function"]["name"] for tool in message["tool_calls"]}
    print("Called tools in response:", called_tools)
    matched = called_tools & tool_names
    return matched


def time_now() -> str:
    return datetime.now(datetime.UTC).isoformat()


def add_system_message(messages: list[dict], new_content: str):
    msg = {"role": "system", "content": new_content}
    updated = False
    for message in messages:
        if message["role"] == "system":
            message["content"] += " \n" + new_content
            updated = True

    if not updated:
        messages.insert(0, msg)

    return messages


async def llama_request(backend, body) -> httpx.Response:
    async with httpx.AsyncClient(timeout=60.0) as client:
        llama_response = await client.post(
            backend,
            json=body,
            headers={"Content-Type": "application/json"},
        )
    return llama_response


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

        body["tools"] = tools

        # Forward to actual LLaMA backend
        llama_response = await llama_request(LLAMA_BACKEND, body)

        llama_response_json = llama_response.json()

        print("Initial LLaMA response:", llama_response_json)

        try:
            while tools_matched(tools, llama_response_json):
                tools_called = tools_matched(tools, llama_response_json)
                print("Tools called:", tools_called)
                for tool_name in tools_called:
                    if tool_name == "time_now":
                        result = time_now()
                        body["messages"].append(
                            {
                                "role": "tool",
                                "name": "time_now",
                                "content": result,
                            }
                        )
                print("Updated body with tool results:", body)
                llama_response = await llama_request(LLAMA_BACKEND, body)
                llama_response_json = llama_response.json()
        except Exception as e:
            print("Error during tool execution:", e)
            pass

        return Response(
            content=llama_response.content,
            status_code=llama_response.status_code,
            media_type="application/json",
        )

    except Exception:
        return JSONResponse(status_code=500, content="Server error")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("llama-proxy:app", host="0.0.0.0", port=80)
