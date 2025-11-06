import json
import requests


def extract_final_message(raw_text: str) -> str:
    """
    Extracts the final assistant message from LLaMA chat output.
    """
    marker = "<|channel|>final<|message|>"
    if marker in raw_text:
        output = raw_text.split(marker)[-1].strip()
        if output:
            return output
    return raw_text.strip()  # fallback to full text if marker missing


def main():
    print("=== LLaMA Proxy Python Client ===")

    # Get server IP and port
    host = "192.168.49.2"
    port = input("Enter proxy port (e.g., 32307, run `minikube service llama-proxy --url` when in doubt): ").strip()
    url = f"http://{host}:{port}/v1/chat/completions"

    print("\nType your queries below. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Exiting client.")
            break

        # Build request payload
        payload = {
            "model": "llama-2-7b-chat",
            "messages": [{"role": "user", "content": user_input}],
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                # Print the response content
                # Assuming OpenAI-style responses: data["choices"][0]["message"]["content"]
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    content = extract_final_message(content)
                    print(f"LLaMA: {content}\n")
                else:
                    print(f"LLaMA: {json.dumps(data)}\n")
            else:
                print(f"Error {response.status_code}: {response.text}\n")
        except Exception as e:
            print(f"Request failed: {e}\n")


if __name__ == "__main__":
    main()
