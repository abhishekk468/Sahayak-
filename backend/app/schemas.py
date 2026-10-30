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

MatchStatus = Literal["POTENTIAL_MATCH", "NOT_MATCHED", "NEED_MORE_INFORMATION", "MANUAL_REVIEW"]

class SchemeSummary(BaseModel):
    scheme_id: str
    scheme_name: str
    segment: str
    benefit_summary: str | None = None
    official_source_url: str
    eligibility_mode: str

class SchemeMatchRequest(BaseModel):
    profile: dict[str, Any]
    scheme_ids: list[str] | None = None

class SchemeMatch(BaseModel):
    scheme_id: str
    scheme_name: str
    status: MatchStatus
    reasons: list[str]
    official_source_url: str
    documents: list[str] = []

class SchemeMatchResponse(BaseModel):
    matches: list[SchemeMatch]
    disclaimer: str

class RagAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    scheme_id: str | None = None

class RagCitation(BaseModel):
    title: str
    url: str
    section: str | None = None

class RagAskResponse(BaseModel):
    answer: str
    citations: list[RagCitation]
    source_found: bool
