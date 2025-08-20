from engines.speech_engine import SpeechRecognitionEngine


class ParakeetEngine(SpeechRecognitionEngine):
    def __init__(self, cpu: bool):
        import nemo.collections.asr as nemo_asr

        self.model = nemo_asr.models.ASRModel.from_pretrained(
            model_name="nvidia/parakeet-tdt-0.6b-v2"
        )

    def transcribe(self, file_path: str):
        text = self.model.transcribe(file_path)[0][0]
        return text
