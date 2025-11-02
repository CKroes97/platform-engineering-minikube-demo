import os
import time
import json
import urllib.request
from datetime import datetime

LLAMA_URL = os.getenv("LLAMA_URL", "http://192.168.49.2:39443/v1/completions")
PROMPT = os.getenv("PROMPT", "Hello, how are you?")
INTERVAL = int(os.getenv("INTERVAL", "150"))  # seconds


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

        log_entry = f"[{datetime.datetime.now(datetime.UTC)}] {text.strip()}\n"
        print(log_entry.strip())


    except Exception as e:
        error_msg = f"[{datetime.datetime.now(datetime.UTC)}] ERROR: {e}\n"
        print(error_msg.strip())


def main():
    print("Starting LLaMA ping service...")
    while True:
        ping_llama()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()