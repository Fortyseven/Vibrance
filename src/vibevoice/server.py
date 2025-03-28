"""FastAPI server for Whisper transcription"""

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from faster_whisper import WhisperModel

HOST = "0.0.0.0"
PORT = 4242

app = FastAPI()

model = WhisperModel("large", device="cuda", compute_type="float16")
# Enable in case you want to run on CPU, but it's much slower
# model = WhisperModel("medium", device="cpu", compute_type="int8")


class TranscribeRequest(BaseModel):
    file_path: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/transcribe/")
async def transcribe(request: TranscribeRequest):
    segments, info = model.transcribe(request.file_path)
    text = " ".join([segment.text.strip() for segment in segments])
    return {"text": text}


def run_server():
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    run_server()
