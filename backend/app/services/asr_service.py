import asyncio
import os
import tempfile
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

    def __init__(self, provider: str = "mock", model_id: str = "small",
                 device: str = "cpu", compute_type: str = "int8"):
        self.provider = provider.lower()
        self.model_id = model_id
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _get_model(self):
        if self._model is None:
            if self.provider != "whisper":
                return None
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise ASRNotConfiguredError(
                    "ASR_PROVIDER=whisper requires faster-whisper. "
                    "Install backend/requirements.txt first."
                ) from exc
            self._model = WhisperModel(
                self.model_id,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def _transcribe_file(self, path: str) -> Transcription:
        model = self._get_model()
        import av
        import numpy as np

        samples = []
        with av.open(path) as container:
            resampler = av.audio.resampler.AudioResampler(
                format="s16", layout="mono", rate=16000
            )
            for frame in container.decode(audio=0):
                resampled_frames = resampler.resample(frame)
                if not isinstance(resampled_frames, list):
                    resampled_frames = [resampled_frames]
                samples.extend(
                    frame.to_ndarray().reshape(-1) for frame in resampled_frames
                )
        if not samples:
            raise ValueError("The uploaded audio contains no decodable samples.")
        audio = np.concatenate(samples).astype(np.float32) / 32768.0
        segments, info = model.transcribe(audio, beam_size=5, vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise ValueError("The audio did not contain recognizable speech.")
        language_code = "hin_Deva" if info.language == "hi" else "eng_Latn"
        confidence = max(0.0, min(1.0, float(info.language_probability)))
        return Transcription(text, language_code, confidence)

    async def transcribe(self, audio_bytes: bytes, filename: str) -> Transcription:
        if not audio_bytes:
            raise ValueError("Uploaded audio is empty.")
        if self.provider == "whisper":
            suffix = os.path.splitext(filename)[1] or ".audio"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as audio_file:
                audio_file.write(audio_bytes)
                audio_path = audio_file.name
            try:
                return await asyncio.to_thread(self._transcribe_file, audio_path)
            finally:
                try:
                    os.unlink(audio_path)
                except FileNotFoundError:
                    pass
        raise ASRNotConfiguredError(
            f"ASR_PROVIDER={self.provider}. Implement a verified IndicWhisper or "
            "Bhashini adapter using its current official documentation. "
            "Use /voice-command/text to test the downstream pipeline meanwhile."
        )
