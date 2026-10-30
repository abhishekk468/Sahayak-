from typing import Any, Literal
from pydantic import BaseModel, Field

LanguageCode = Literal["hin_Deva", "eng_Latn", "pan_Guru"]

class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    src_lang: LanguageCode
    tgt_lang: LanguageCode

class TranslateResponse(BaseModel):
    translated_text: str
    src_lang: str
    tgt_lang: str
    model_id: str

class VoiceTextRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=5000)
    language_code: LanguageCode = "hin_Deva"
    district: str | None = "Mandi"

class VoiceTextResponse(BaseModel):
    original_transcript: str
    english_text: str
    extracted_profile: dict[str, Any]
    clarification_needed: list[str]
    pipeline_status: str
    note: str

class HealthResponse(BaseModel):
    status: str
    translation_service: str
    asr_provider: str
    tts_provider: str
