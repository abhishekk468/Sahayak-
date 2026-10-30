# Implementation status at handoff

## Included
- IndicTrans2 Hindi↔English service using the AI4Bharat distilled HF checkpoint IDs.
- FastAPI health, translation, transcript pipeline and audio-upload placeholder endpoints.
- Conservative demo extractor preserving the bigha unit.
- Starter unit tests.
- PPT-aligned dataset workbook and database files copied into `data/` where available.
- Local `faster-whisper` ASR adapter with configurable model/device and audio validation.
- CSV-backed `/schemes`, `/schemes/match` and `/rag/ask` routes with official source URLs and safe no-source fallback.
- PPT-specific tests for Sunita, PM-KMY age rejection, PM-KISAN manual review, student missing data and citations.

## Coding agent must complete
- Verified IndicWhisper/Bhashini ASR adapter.
- Better Gemini profile extraction with confidence/evidence and confirmation questions.
- Full scheme rule-engine integration and source-bearing match results.
- Official-document RAG ingestion, embeddings and retrieval.
- TTS provider adapter.
- PostgreSQL migrations/seeding.
- WhatsApp webhook and outgoing messages.
- Admin dashboard and full test suite.

## Verified locally
- Backend tests: 6 passed.
- Live API: `/health`, `/schemes`, `/schemes/match` and `/rag/ask` return successfully on port 8001.
- Whisper voice transcription: enabled with `ASR_PROVIDER=whisper`, `ASR_MODEL_ID=tiny`.
- Hindi-to-English IndicTrans2: code path is wired, but the Hugging Face checkpoint currently requires accepted model terms and `HF_TOKEN` authentication.

## Still blocked or provider-required
- IndicWhisper/Bhashini production ASR, Gemini extraction, TTS, WhatsApp and PostgreSQL persistence require a selected provider, credentials and integration testing.
- The current RAG route is a provenance-safe CSV/source lookup; PDF/HTML ingestion and embeddings are not yet implemented.

Do not claim live voice audio works until ASR is configured and tested. IndicTrans2 translates text only.
