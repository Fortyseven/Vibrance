from ollama import chat
from ollama import ChatResponse
from rich import print


MODEL = "llama3.1:latest"
TEMP = 0.8


def fetch_response(query: str, clipboard_contents:str = "") -> str:
    if clipboard_contents:
        print(f"[blue]==== Clipboard:[/blue]\n{clipboard_contents}")
        messages = [
                {
                    "role": "system",
                    "content": query,
                },
                {
                    "role": "user",
                    "content": clipboard_contents,
                },
            ]
    else:
        messages = [
            {
                "role": "user",
                "content": query,
            },
        ]

    response: ChatResponse = chat(
        model=MODEL,
        messages=messages,
        options={
            "temperature": TEMP,
        },
    )

    return response.message.content.strip()