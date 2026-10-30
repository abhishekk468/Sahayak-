from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import (
    TranslateRequest, TranslateResponse, VoiceTextRequest,
    VoiceTextResponse, HealthResponse
)
from app.schemas import SchemeMatchRequest, SchemeMatchResponse, SchemeSummary, RagAskRequest, RagAskResponse
from app.services.indictrans2_service import IndicTrans2Service
from app.services.asr_service import ASRService, ASRNotConfiguredError
from app.services.profile_extractor import extract_profile_from_english
from app.services.scheme_service import ask_sources, match, schemes

settings = get_settings()
app = FastAPI(
    title="SAHAYAK Voice & Translation API",
    description="Hindi/English translation and transcript pipeline starter.",
    version="0.1.0"
)
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["GET", "POST"], allow_headers=["*"]
)
translator = IndicTrans2Service(
    settings.indic_en_model, settings.en_indic_model,
    settings.model_device, settings.model_max_length, settings.model_num_beams
)
asr = ASRService(
    settings.asr_provider,
    settings.asr_model_id,
    settings.asr_device,
    settings.asr_compute_type,
)

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok", translation_service="lazy-loaded",
        asr_provider=settings.asr_provider, tts_provider=settings.tts_provider
    )

@app.get("/schemes", response_model=list[SchemeSummary])
def list_schemes():
    return schemes()

@app.post("/schemes/match", response_model=SchemeMatchResponse)
def match_schemes(request: SchemeMatchRequest):
    return {"matches": match(request.profile, request.scheme_ids), "disclaimer": "Preliminary screening only. This is not government approval or an entitlement decision."}

@app.post("/rag/ask", response_model=RagAskResponse)
def rag_ask(request: RagAskRequest):
    return ask_sources(request.question, request.scheme_id)

@app.post("/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest):
    try:
        result = translator.translate(request.text, request.src_lang, request.tgt_lang)
        model_id = settings.indic_en_model if request.src_lang == "hin_Deva" else settings.en_indic_model
        return TranslateResponse(
            translated_text=result, src_lang=request.src_lang,
            tgt_lang=request.tgt_lang, model_id=model_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Translation service error: {exc}") from exc

@app.post("/voice-command/text", response_model=VoiceTextResponse)
def voice_text(request: VoiceTextRequest):
    try:
        english = request.transcript if request.language_code == "eng_Latn" else translator.translate(
            request.transcript, request.language_code, "eng_Latn"
        )
        profile = extract_profile_from_english(english, request.district)
        clarification = []
        if profile.get("age_years") is None:
            clarification.append("Please confirm your age.")
        if profile.get("occupation") is None:
            clarification.append("Please confirm your occupation.")
        if profile.get("land_area") is not None and profile.get("land_unit") == "bigha":
            clarification.append("Please confirm the land area and local bigha measurement; no conversion was applied.")
        return VoiceTextResponse(
            original_transcript=request.transcript,
            english_text=english,
            extracted_profile=profile,
            clarification_needed=clarification,
            pipeline_status="TRANSCRIBED_TRANSLATED_PROFILE_DEMO",
            note="Voice transcription is available with the configured ASR provider. Scheme matching, cited RAG and TTS remain separate capabilities."
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Voice pipeline error: {exc}") from exc

@app.post("/voice-command/audio")
async def voice_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Audio filename is required.")
    allowed = {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3",
               "audio/ogg", "audio/webm", "audio/mp4", "audio/m4a"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Unsupported audio content type.")
    audio_bytes = await file.read()
    if len(audio_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds 20 MB.")
    try:
        result = await asr.transcribe(audio_bytes, file.filename)
        return {
            "transcript": result.text, "language_code": result.language_code,
            "asr_confidence": result.confidence
        }
    except ASRNotConfiguredError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
