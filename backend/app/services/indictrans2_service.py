from dataclasses import dataclass
from typing import Any

SUPPORTED_CODES = {"hin_Deva", "eng_Latn", "pan_Guru"}

@dataclass
class LoadedDirection:
    model_id: str
    tokenizer: Any
    model: Any
    device: str

class IndicTrans2Service:
    """Lazy IndicTrans2 translator using AI4Bharat's HF inference pattern."""

    def __init__(self, indic_en_model: str, en_indic_model: str,
                 device_preference: str = "auto", max_length: int = 256,
                 num_beams: int = 5):
        self.indic_en_model_id = indic_en_model
        self.en_indic_model_id = en_indic_model
        self.device_preference = device_preference
        self.max_length = max_length
        self.num_beams = num_beams
        self._directions: dict[str, LoadedDirection] = {}
        self._processor = None

    @staticmethod
    def _device(preference: str) -> str:
        import torch
        if preference.lower() == "cpu":
            return "cpu"
        if preference.lower() == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError("MODEL_DEVICE=cuda but CUDA is unavailable.")
            return "cuda"
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _get_processor(self):
        if self._processor is None:
            try:
                from IndicTransToolkit.processor import IndicProcessor
            except ImportError as exc:
                raise RuntimeError(
                    "IndicTransToolkit missing. Install backend/requirements.txt "
                    "in WSL2/Linux or macOS."
                ) from exc
            self._processor = IndicProcessor(inference=True)
        return self._processor

    def _load_direction(self, src_lang: str, tgt_lang: str) -> LoadedDirection:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        key = f"{src_lang}:{tgt_lang}"
        if key in self._directions:
            return self._directions[key]
        if (src_lang, tgt_lang) == ("hin_Deva", "eng_Latn"):
            model_id = self.indic_en_model_id
        elif (src_lang, tgt_lang) == ("eng_Latn", "hin_Deva"):
            model_id = self.en_indic_model_id
        else:
            raise ValueError(
                "Only Hindi↔English checkpoints are configured in this starter. "
                "Add an appropriate checkpoint to enable this direction."
            )

        device = self._device(self.device_preference)
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        kwargs = {"trust_remote_code": True, "low_cpu_mem_usage": True}
        if device == "cuda":
            kwargs["torch_dtype"] = torch.float16
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id, **kwargs).to(device)
        model.eval()
        loaded = LoadedDirection(model_id, tokenizer, model, device)
        self._directions[key] = loaded
        return loaded

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        if len(text) > 5000:
            raise ValueError("Text is too long; maximum is 5000 characters.")
        if src_lang not in SUPPORTED_CODES or tgt_lang not in SUPPORTED_CODES:
            raise ValueError(f"Unsupported language code. Choose from {sorted(SUPPORTED_CODES)}.")
        if src_lang == tgt_lang:
            return text.strip()

        loaded = self._load_direction(src_lang, tgt_lang)
        processor = self._get_processor()
        batch = processor.preprocess_batch(
            [text.strip()], src_lang=src_lang, tgt_lang=tgt_lang
        )
        inputs = loaded.tokenizer(
            batch, truncation=True, padding="longest",
            return_tensors="pt", return_attention_mask=True
        ).to(loaded.device)

        import torch
        with torch.inference_mode():
            generated = loaded.model.generate(
                **inputs, use_cache=True, min_length=0,
                max_length=self.max_length, num_beams=self.num_beams,
                num_return_sequences=1
            )
        decoded = loaded.tokenizer.batch_decode(
            generated, skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )
        result = processor.postprocess_batch(decoded, lang=tgt_lang)
        if not result:
            raise RuntimeError("IndicTrans2 returned an empty translation.")
        return result[0]
