# Implementation status at handoff

## Included
- IndicTrans2 Hindi↔English service using the AI4Bharat distilled HF checkpoint IDs.
- FastAPI health, translation, transcript pipeline and audio-upload placeholder endpoints.
- Conservative demo extractor preserving the bigha unit.
- Starter unit tests.
- PPT-aligned dataset workbook and database files copied into `data/` where available.

## Coding agent must complete
- Verified IndicWhisper/Bhashini ASR adapter.
- Better Gemini profile extraction with confidence/evidence and confirmation questions.
- Full scheme rule-engine integration and source-bearing match results.
- Official-document RAG ingestion, embeddings and retrieval.
- TTS provider adapter.
- PostgreSQL migrations/seeding.
- WhatsApp webhook and outgoing messages.
- Admin dashboard and full test suite.

Do not claim live voice audio works until ASR is configured and tested. IndicTrans2 translates text only.
