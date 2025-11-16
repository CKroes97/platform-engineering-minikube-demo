import json
import urllib.request


def main():
    print("=== LLaMA Proxy Python Client ===")

    # Get server IP and port
    host = "192.168.49.2"
    port = input(
        "Enter proxy port (e.g., 32307, run `minikube service llama-proxy --url` when in doubt): "
    ).strip()
    truncate = (
        input("Truncate long responses? (y/n, default n): ").strip().lower() == "y"
    )
    url = f"http://{host}:{port}/v1/chat/completions"

    print("\nType your queries below. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Exiting client.")
            break

        # Build request payload
        payload = {
            "model": "Qwen/Qwen2.5-14B-Instruct-AWQ",
            "messages": [{"role": "user", "content": user_input}],
        }.encode("utf-8")

        headers = {"Content-Type": "application/json", "authorization": "client"}

        response = urllib.request.Request(
            url, data=payload, headers=headers, method="POST"
        )

        with urllib.request.urlopen(response) as http_response:
            data = json.loads(http_response.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                if truncate:
                    content = choices[0].get("message", {}).get("content", "")
                else:
                    content = choices[0]
                print(f"LLaMA: {content}\n")
            else:
                print(f"LLaMA: {json.dumps(data)}\n")


if __name__ == "__main__":
    main()
