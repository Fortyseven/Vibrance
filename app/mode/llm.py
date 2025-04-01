from ollama import chat
from ollama import ChatResponse


MODEL = "llama3.1:latest"
TEMP = 0.8


def fetch_response(query: str) -> str:

    response: ChatResponse = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": query,
            },
        ],
        options={
            "temperature": TEMP,
        },
    )

    return response.message.content.strip()
