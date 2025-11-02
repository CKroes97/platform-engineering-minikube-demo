import os
import time
import json
import urllib.request
from datetime import datetime, timezone

LLAMA_URL = os.getenv("LLAMA_URL", "http://host.minikube.internal:39443/v1/chat/completions")
PROMPT = os.getenv("PROMPT", "Hello, how are you?")
INTERVAL = int(os.getenv("INTERVAL", "15"))  # seconds


def ping_llama():
    try:
        # Prepare OpenAI-style chat request
        payload = json.dumps({
            "model": "bartowski/openai_gpt-oss-20b-GGUF",
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": 50
        }).encode("utf-8")

        req = urllib.request.Request(
            LLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)

            # Extract assistant message
            choices = data.get("choices", [])
            if choices:
                assistant_msg = choices[0].get("message", {}).get("content", "").strip()
            else:
                assistant_msg = "No response"

        log_entry = f"[{datetime.now(timezone.utc).isoformat()}] {assistant_msg}"
        print(log_entry, flush=True)

    except Exception as e:
        error_msg = f"[{datetime.now(timezone.utc).isoformat()}] ERROR: {e}"
        print(error_msg, flush=True)


def main():
    print("Starting LLaMA ping service...", flush=True)
    while True:
        ping_llama()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()