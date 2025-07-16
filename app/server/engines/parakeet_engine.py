from engines.speech_engine import SpeechRecognitionEngine


class ParakeetEngine(SpeechRecognitionEngine):
    def __init__(self, cpu: bool):
        pass  # Stub implementation

    def transcribe(self, file_path: str):
        class DummySegment:
            def __init__(self, text):
                self.text = text

        return [DummySegment("[Parakeet stub: transcription not implemented]")], {}
