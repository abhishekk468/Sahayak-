from dataclasses import dataclass

@dataclass
class Transcription:
    text: str
    language_code: str
    confidence: float | None = None

class ASRNotConfiguredError(RuntimeError):
    pass

class ASRService:
    """ASR adapter boundary; IndicTrans2 itself does not accept audio."""

    def __init__(self, provider: str = "mock"):
        self.provider = provider.lower()

    async def transcribe(self, audio_bytes: bytes, filename: str) -> Transcription:
        if not audio_bytes:
            raise ValueError("Uploaded audio is empty.")
        raise ASRNotConfiguredError(
            f"ASR_PROVIDER={self.provider}. Implement a verified IndicWhisper or "
            "Bhashini adapter using its current official documentation. "
            "Use /voice-command/text to test the downstream pipeline meanwhile."
        )
