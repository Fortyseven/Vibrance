from ollama import chat
from ollama import ChatResponse

from pydantic import BaseModel


class CodeRequest(BaseModel):
    code: str


last_query = None


MODEL = "llama3.1:latest"
TEMP = 0.4
SPROMPT = """
    You are a helpful assistant that generates clean formatted, concise code that implements
    best pratices. Do not include usage examples. Only respond with the requested code. If
    it's not possible, return a code comment with the reason. Pay careful attention to security
    and performance.
""".strip()


def fetch_code(query: str, clipboard_contents=None) -> str:
    global last_query

    if query.lower().startswith("retry") and last_query:
        query = last_query

    last_query = query

    if clipboard_contents:
        print(f"[blue]==== Clipboard:[/blue]\n{clipboard_contents}")

    response: ChatResponse = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SPROMPT,
            },
            {
                "role": "user",
                "content": query + (f"\n\n```\n{clipboard_contents}```" or ""),
            },
        ],
        format=CodeRequest.model_json_schema(),
        options={
            "temperature": TEMP,
        },
    )

    response = CodeRequest.model_validate_json(response.message.content)

    print(response)

    return response.code
