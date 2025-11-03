import os
import time
import json
import urllib.request
from datetime import datetime, timezone

LLAMA_URL = os.getenv(
    "LLAMA_URL", "http://llama-proxy.default.svc.cluster.local:80/v1/chat/completions"
)
PROMPT = os.getenv("PROMPT", "Hello, how are you?")
INTERVAL = int(os.getenv("INTERVAL", "15"))  # seconds


def extract_final_message(raw_text: str) -> str:
    """
    Extracts the final assistant message from LLaMA chat output.
    """
    marker = "<|channel|>final<|message|>"
    if marker in raw_text:
        return raw_text.split(marker)[-1].strip()
    return raw_text.strip()  # fallback to full text if marker missing


def ping_llama():
    try:
        # Prepare OpenAI-style chat request
        payload = json.dumps(
            {
                "model": "bartowski/openai_gpt-oss-20b-GGUF",
                "messages": [
                    {"role": "system", "content": "You are friendly and very concise."},
                    {"role": "user", "content": PROMPT},
                ],
                "max_tokens": 400,
            }
        ).encode("utf-8")

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

        assistant_msg = extract_final_message(assistant_msg)
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
