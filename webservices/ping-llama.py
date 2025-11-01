import os
import time
import json
import urllib.request
from datetime import datetime

LLAMA_URL = os.getenv("LLAMA_URL", "http://localhost:8080/v1/completions")
PROMPT = os.getenv("PROMPT", "Hello, how are you?")
INTERVAL = int(os.getenv("INTERVAL", "150"))  # seconds
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "/data/llama_responses.log")


def ping_llama():
    try:
        payload = json.dumps({
            "prompt": PROMPT,
            "n_predict": 32
        }).encode("utf-8")

        req = urllib.request.Request(
            LLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
            text = data.get("content", data.get("response", str(data)))

        log_entry = f"[{datetime.utcnow().isoformat()}] {text.strip()}\n"
        print(log_entry.strip())

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except Exception as e:
        error_msg = f"[{datetime.utcnow().isoformat()}] ERROR: {e}\n"
        print(error_msg.strip())
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(error_msg)


def main():
    while True:
        ping_llama()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()