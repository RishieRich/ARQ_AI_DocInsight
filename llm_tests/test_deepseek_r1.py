"""Simple script to sanity-check DeepSeek R1 via the local Ollama service."""

from ollama import Client


def main() -> None:
    client = Client(host="http://localhost:11434")
    response = client.chat(
        model="deepseek-r1",
        messages=[
            {"role": "user", "content": "Write a short summary about AI agents."}
        ],
    )

    content = response.get("message", {}).get("content")
    if not content:
        raise RuntimeError("Ollama response did not include message content.")

    print(content)


if __name__ == "__main__":
    main()
