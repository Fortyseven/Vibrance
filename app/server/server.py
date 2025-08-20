"""FastAPI server for modular speech recognition engines"""

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from engines.whisper_engine import WhisperEngine
from engines.parakeet_engine import ParakeetEngine
import argparse

HOST = "0.0.0.0"
PORT = 4242

app = FastAPI()

engine = None


class TranscribeRequest(BaseModel):
    file_path: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/transcribe/")
async def transcribe(request: TranscribeRequest):
    text = engine.transcribe(request.file_path)
    return {"text": text}


def parse_arguments():
    """
    Parses command-line arguments for the server.
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="FastAPI server for modular speech recognition engines"
    )
    parser.add_argument(
        "--cpu", action="store_true", help="Force CPU usage for the model"
    )
    parser.add_argument("--host", type=str, default=HOST, help="Host for the server")
    parser.add_argument("--port", type=int, default=PORT, help="Port for the server")
    parser.add_argument(
        "--engine",
        type=str,
        choices=["whisper", "parakeet"],
        default="whisper",
        help="Speech recognition engine to use",
    )
    return parser.parse_args()


def initialize_engine(engine_name: str, cpu: bool):
    """
    Initializes the selected speech recognition engine.
    """
    if engine_name == "whisper":
        return WhisperEngine(cpu)
    elif engine_name == "parakeet":
        return ParakeetEngine(cpu)
    else:
        raise ValueError(f"Unknown engine: {engine_name}")


def run_server():
    global engine
    args = parse_arguments()
    engine = initialize_engine(args.engine, args.cpu)
    uvicorn.run(app, host=args.host, port=args.port, log_level="error")


if __name__ == "__main__":
    run_server()
