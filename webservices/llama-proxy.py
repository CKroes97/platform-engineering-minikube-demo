import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import uvicorn
import json

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
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": """Returns a list of files of which the content can be provided to the LLM
                                The files concern details about Dutch towns and cities.""",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_content",
            "description": "Returns the content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": """Name of the file to read content from,
                          files can be listed using list_directory tool""",
                    }
                },
            },
        },
    },
]


def get_tools() -> list[dict]:
    tool_registry = {
        "time_now": time_now,
        "list_directory": list_directory,
        "file_content": file_content,
    }
    return tool_registry


def tools_matched(
    tools: list[dict], response_json: dict
) -> list[str:str, str : dict[str:str]]:
    tool_names = {tool["function"]["name"] for tool in tools}
    print("Available tool names:", tool_names)
    message = response_json["choices"][0]["message"]
    tool_calls = message["tool_calls"]
    called_tools = {tool["function"]["name"] for tool in tool_calls}
    print("Called tools in response:", called_tools)
    matched = called_tools & tool_names
    full_matched_calls = [
        call["function"] for call in tool_calls if call["function"]["name"] in matched
    ]
    print("Extracted tool calls:", tool_calls)
    return full_matched_calls


def time_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def list_directory() -> list[str]:
    return os.listdir("test_data")


def file_content(arguments: dict) -> str:
    file_name = arguments["file_name"]
    file_path = os.path.join("test_data", file_name)
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return "File not found"


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
        if len(content) > 20000:
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

        try:
            while tools_matched(tools, llama_response_json):
                tool_registry = get_tools()
                tools_called = tools_matched(tools, llama_response_json)
                print("Tools called:", tools_called)
                for tool_call in tools_called:
                    print("Executing tool:", tool_call["name"])
                    print("With arguments:", tool_call["arguments"])
                    if tool_call["arguments"] != "{}":
                        result = tool_registry[tool_call["name"]](
                            json.loads(tool_call["arguments"])
                        )
                    else:
                        result = tool_registry[tool_call["name"]]()
                    body["messages"].append(llama_response_json["choices"][0]["message"])
                    body["messages"].append(
                        {
                            "role": "tool",
                            "name": tool_call["name"],
                            "content": result,
                        }
                    )
                print("Updated body with tool results:", body)
                llama_response = await llama_request(LLAMA_BACKEND, body)
                llama_response_json = llama_response.json()
        except Exception as e:
            print(f"Error during tool execution: {str(e)}")
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
