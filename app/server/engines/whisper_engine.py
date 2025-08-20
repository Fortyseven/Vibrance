from faster_whisper import WhisperModel
from engines.speech_engine import SpeechRecognitionEngine


class WhisperEngine(SpeechRecognitionEngine):
    def __init__(self, cpu: bool):
        if cpu:
            self.model = WhisperModel("medium", device="cpu", compute_type="int8")
        else:
            self.model = WhisperModel("large", device="cuda", compute_type="float16")

    def transcribe(self, file_path: str):
        segments, info = self.model.transcribe(file_path)
        segments = " ".join([segment.text.strip() for segment in segments])
        return segments
