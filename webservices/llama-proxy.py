import json
import os
from datetime import datetime, timezone

import httpx
import uvicorn
import yaml
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

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
    """
    Extracts and matches tool calls from a response JSON against a list of available tools.

    Args:
        tools (list[dict]): A list of dictionaries representing available tools,
                            where each dictionary contains a 'function' key with a 'name'.
        response_json (dict): A dictionary representing the response JSON,
                              which contains a 'choices' key with a 'message' that includes 'tool_calls'.

    Returns:
        list[str:str, str : dict[str:str]]: A list of matched tool function dictionaries
                                             that were called in the response.

    Prints:
        - Available tool names.
        - Called tools in the response.
        - Extracted tool calls.
    """
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
    """
    Returns the current time in ISO 8601 format.
    This function retrieves the current time in UTC and formats it as a string
    according to the ISO 8601 standard. The returned string can be used for
    timestamping events or logging purposes.
    Returns:
        str: The current time in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def list_directory() -> list[str]:
    """
    List the contents of the specified directory.

    This function retrieves a list of the names of the entries in the directory
    given by the path "/app/test_data". The entries are returned as a list of
    strings.

    Returns:
        list[str]: A list containing the names of the entries in the directory.
    """
    return os.listdir("/app/test_data")


def file_content(arguments: dict) -> str:
    """
    Retrieve the content of a specified file.

    This function takes a dictionary of arguments, extracts the file name,
    constructs the full file path, and attempts to read the file's content.
    If the file exists, its content is returned as a string. If the file
    does not exist, a "File not found" message is returned.

    Args:
        arguments (dict): A dictionary containing the key "file_name"
                          which specifies the name of the file to read.

    Returns:
        str: The content of the file if found, otherwise "File not found".
    """
    file_name = arguments["file_name"]
    file_path = os.path.join("/app/test_data/", file_name)
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return "File not found"


def add_system_message(messages: list[dict], new_content: str):
    """Add or append a system message to a list of chat messages.
    If one or more messages in the list have the role "system", this function appends
    the provided content to each such message's "content" using a separator " \n".
    If no system message is present, a new system message dictionary is inserted at
    the start of the list.
    Parameters
    ----------
    messages : list[dict]
        Mutable list of message dictionaries. Each dictionary is expected to contain
        at least the keys "role" and "content".
    new_content : str
        Text to add to an existing system message or to set as the content of a new
        system message.
    Returns
    -------
    list[dict]
        The same messages list after modification (the list is mutated in place and
        also returned for convenience).
    """
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
    """
    Make an asynchronous HTTP POST request to a Llama backend service.
    Args:
        backend (str): The URL of the Llama backend service to send the request to.
        body (dict): The request body to be sent as JSON to the backend service.
    Returns:
        httpx.Response: The HTTP response object returned by the backend service.
    Raises:
        httpx.TimeoutException: If the request exceeds the 60-second timeout.
        httpx.RequestError: If there is an error making the HTTP request.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        llama_response = await client.post(
            backend,
            json=body,
            headers={"Content-Type": "application/json"},
        )
    return llama_response


def enforce_user_policy(user_id: str, tool_name) -> tuple[bool, str]:
    """
        Enforce user-specific policies for tool usage.

    This function checks if a specified tool is allowed for a given user based on their individual policy file.
    The policy file is expected to be in YAML format and located in the `/app/policies/` directory, named after the user ID.

    Args:
        user_id (str): The unique identifier for the user whose policy is being enforced.
        tool_name (str): The name of the tool for which access is being checked.

    Returns:
        tuple[bool, str]: A tuple containing:
            - allowed (bool): Indicates whether the tool is allowed for the user.
            - message (str): A message explaining the result; if not allowed, it specifies the reason.
    """
    user_policy_yaml = f"/app/policies/{user_id}.yml"

    if os.path.isfile(user_policy_yaml):
        with open(user_policy_yaml, "r") as file:
            user_policy = yaml.safe_load(file)
            try:
                tool_allowed = user_policy["tools"][tool_name].get("allowed", False)
            except KeyError:
                tool_allowed = False

    if not tool_allowed:
        reason = "Tool not allowed by user policy."
    else:
        reason = None

    return tool_allowed, reason


def enforce_tenant_policy(payload: dict) -> tuple[bool, str]:
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
    """
    Proxy chat completions to the LLaMA backend.
    This asynchronous function handles incoming requests for chat completions,
    enforces tenant policies, and forwards the request to the LLaMA backend.
    It processes the response, executes any tools specified in the request,
    and updates the message history accordingly.
    Args:
        request (Request): The incoming HTTP request containing the chat completion parameters.
    Returns:
        Response: A JSON response containing the chat completion results or an error message.
    Raises:
        Exception: Catches and handles exceptions during request processing and tool execution.
    """

    try:
        # Parse incoming request
        body = await request.json()
        user_id = request.headers.get("authorization", "default_user")
        allowed, reason = enforce_tenant_policy(body)
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
                    allowed, reason = enforce_user_policy(user_id, tool_call["name"])
                    if not allowed:
                        return JSONResponse(
                            status_code=403, content=f"Forbidden + {reason}"
                        )
                    print("Executing tool:", tool_call["name"])
                    print("With arguments:", tool_call["arguments"])
                    if tool_call["arguments"] != "{}":
                        result = tool_registry[tool_call["name"]](
                            json.loads(tool_call["arguments"])
                        )
                    else:
                        result = tool_registry[tool_call["name"]]()
                    body["messages"].append(
                        llama_response_json["choices"][0]["message"]
                    )
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
