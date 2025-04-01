"""FastAPI server for Whisper transcription"""

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from faster_whisper import WhisperModel
import argparse

HOST = "0.0.0.0"
PORT = 4242

app = FastAPI()

model = None


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


def parse_arguments():
    """
    Parses command-line arguments for the server.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="FastAPI server for Whisper transcription")
    parser.add_argument("--cpu", action="store_true", help="Force CPU usage for the Whisper model")
    parser.add_argument("--host", type=str, default=HOST, help="Host for the server")
    parser.add_argument("--port", type=int, default=PORT, help="Port for the server")
    return parser.parse_args()


def initialize_model(cpu: bool):
    """
    Initializes the Whisper model based on the device preference.

    Args:
        cpu (bool): Whether to force CPU usage.

    Returns:
        WhisperModel: The initialized Whisper model.
    """
    if cpu:
        return WhisperModel("medium", device="cpu", compute_type="int8")
    return WhisperModel("large", device="cuda", compute_type="float16")


def run_server():
    global model
    args = parse_arguments()
    model = initialize_model(args.cpu)
    uvicorn.run(app, host=args.host, port=args.port, log_level="error")


if __name__ == "__main__":
    run_server()
