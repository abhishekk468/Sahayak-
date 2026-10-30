# VS CODE CODING AGENT TASK – COMPLETE SAHAYAK VOICE PIPELINE

You are working inside the supplied SAHAYAK project workspace. **Do the work, not just provide a plan.** Inspect files, create/edit code, run tests, fix errors, and report what works and what still needs credentials or manual verification. Ask before running destructive commands or commands with unexpected external side effects.

## 1. Follow this project scope
SAHAYAK is a voice-first government-scheme discovery assistant for a Himachal Pradesh pilot:
- Geography: Mandi and Kangra.
- Main demo profiles: Sunita, age 52, farmer, Mandi, 3 bigha land; and a student asking about Himachal scholarships.
- Languages in the PPT: Hindi, Himachali dialect and English.
- Channels: WhatsApp first; IVR/feature-phone support later.
- User journey: voice/text → transcript → citizen profile → scheme matching → official document checklist/source answer → response in citizen's language.
- Planned components: IndicWhisper/ASR, IndicTrans2, Gemini profile extraction, Python JSON rule engine, RAG over official scheme documents, FastAPI, WhatsApp, admin insight dashboard.

Use the supplied `data/SAHAYAK_Himachal_Pilot_Data.xlsx` and CSV data as the starting scheme source if present. Preserve every official-source URL and manual-review status. Never invent missing eligibility thresholds, benefits, documents or current scheme rules.

### Important PPT consistency checks
- Sunita is 52 years old.
- PM-Kisan Maandhan entry age is 18–40. It must NOT be shown as a positive match for Sunita.
- HP Swavalamban material in the supplied research has a dated detailed guideline and a current portal summary with age criteria that require reconciliation. Do not show Sunita as eligible; return manual verification/not matched on age pending current official department confirmation.
- PM-KISAN can only be a potential match until landholding family records, exclusions, eKYC and state verification are checked.
- The PPT student example has no class, institution, merit-list or other details. Ask for missing information instead of guessing.

## 2. IndicTrans2 – exact integration
Use AI4Bharat Hugging Face-compatible distilled models:
- Hindi → English: `ai4bharat/indictrans2-indic-en-dist-200M`
- English → Hindi: `ai4bharat/indictrans2-en-indic-dist-200M`

Use:
- `AutoTokenizer`
- `AutoModelForSeq2SeqLM`
- `IndicProcessor` from `IndicTransToolkit.processor`

Follow AI4Bharat's official example pattern:
1. `IndicProcessor(inference=True)`
2. `preprocess_batch(texts, src_lang=..., tgt_lang=...)`
3. Tokenize with padding/truncation/tensors.
4. `model.generate(...)` inside `torch.inference_mode()`.
5. `tokenizer.batch_decode(..., skip_special_tokens=True)`.
6. `postprocess_batch(decoded, lang=tgt_lang)`.

Load models lazily and cache them. Use CPU-safe float32 on CPU and supported reduced precision on CUDA. Do not load unnecessary model families.

Initial language codes:
- Hindi: `hin_Deva`
- English: `eng_Latn`
- Punjabi optional later: `pan_Guru`

Himachali is NOT a separate language code in IndicTrans2's published supported list. Implement a dialect ASR/normalisation fallback that can map verified local speech into Hindi; do not claim native Himachali IndicTrans2 translation.

Official references:
- https://github.com/AI4Bharat/IndicTrans2
- https://github.com/AI4Bharat/IndicTrans2/tree/main/huggingface_interface
- https://raw.githubusercontent.com/AI4Bharat/IndicTrans2/main/huggingface_interface/example.py
- https://github.com/VarunGumma/IndicTransToolkit

The toolkit currently documents Python 3.10+ and Linux/macOS; it says Windows is not built/tested. Provide Windows instructions through WSL2 Ubuntu. Do not promise native Windows compatibility.

## 3. Implement the end-to-end voice flow as separate services
A. Audio upload and validation.
B. ASR transcription using a verified IndicWhisper or Bhashini adapter.
C. Preserve transcript, detected language, ASR confidence and timestamps.
D. IndicTrans2 translates Hindi → English for downstream processing.
E. Extract user intent and structured profile.
F. Ask a confirmation question for uncertain/missing critical values.
G. Run deterministic Python eligibility pre-screen from supplied scheme rules.
H. Retrieve official source chunks with RAG and return citations.
I. Prepare a simple English answer grounded in retrieved sources.
J. IndicTrans2 translates answer English → user's language.
K. TTS speaks the answer if a configured provider exists.
L. Return transcript, profile, clarification, matches, citations, response text and optional audio URL.

Do not combine translation and eligibility into an LLM decision.

## 4. ASR provider
IndicTrans2 accepts text; it does not transcribe audio. Inspect current official IndicWhisper/AI4Bharat/Bhashini documentation before implementing ASR. Never invent a package, checkpoint ID, endpoint, API schema or authentication flow. If a reproducible local model is unavailable, keep a provider interface plus mock/test provider and clearly document what model/credentials are still needed. The transcript endpoint must work independently of audio.

Implement:
- `POST /voice-command/audio` with file validation and clear provider-not-configured errors.
- `POST /voice-command/text` for testing from a supplied transcript.

## 5. Profile extraction
Create a typed nullable profile containing:
- age_years
- district
- state
- occupation
- land_area
- land_unit
- annual_income_inr
- family_size
- student_class_or_course
- social_category (only if voluntarily provided and required for a scheme)
- bonafide_himachali
- preferred_language
- intent

Each extracted field needs value, confidence and evidence text. If Gemini is used, put its key in `.env`; keep deterministic fallback for tests and validate output with Pydantic. Do not guess missing fields. Keep `3 bigha` as number 3 and unit `bigha`, never silently convert.

## 6. Eligibility matching
Use deterministic Python logic, not Gemini, for rule decisions. Support:
- EQ, GTE, LTE, BETWEEN, IN
- REQUIRE, EXCLUDE, MANUAL_REVIEW
- missing field → NEED_MORE_INFORMATION
- manual rule → MANUAL_REVIEW
- human-readable reasons and official source URL per result

Allowed statuses:
- `POTENTIAL_MATCH`: all verified automated checks pass and no manual unresolved condition remains.
- `NOT_MATCHED`: a verified requirement fails or a verified exclusion applies.
- `NEED_MORE_INFORMATION`: required user field is missing.
- `MANUAL_REVIEW`: department, local record, merit-list or document verification is required.

Add tests:
- Sunita: 52, farmer, Mandi, 3 bigha.
- PM-KMY must fail age rule.
- PM-KISAN must never return confirmed eligible on occupation/land quantity alone.
- HP MMSY must not be positive for Sunita's age; preserve guideline date/current-rule discrepancy.
- Student with missing class/merit/institution details must request more information or manual review.

## 7. RAG
Build official-document ingestion for official PDFs/HTML:
- source title, department, URL, fetch date, version, page/section, text and chunk ID.
- embeddings and FAISS (or a clearly documented lightweight local alternative).
- retrieval by scheme/question.
- citations contain official URL and page/section.
- do not answer eligibility questions from LLM memory.
- safe fallback if no source is retrieved.

Create a manual ingestion command first; do not aggressively crawl official sites without rate limiting/source checks.

## 8. FastAPI routes
Implement and document:
- `GET /health`
- `POST /translate`
- `POST /voice-command/text`
- `POST /voice-command/audio`
- `POST /schemes/match`
- `GET /schemes`
- `POST /rag/ask`

Use Pydantic request/response models, validation, useful HTTP errors, safe logging and environment-configured CORS.

## 9. Database
Use PostgreSQL for the application, with SQLite allowed for unit tests if useful. Include schema/migrations and a repeatable seed loader for supplied CSVs. Tables should cover:
- schemes
- eligibility_rules
- scheme_documents
- official_sources
- citizen_profiles (consent status)
- user_interactions (no raw audio retention by default)
- rag_documents
- rag_chunks
- eligibility_results
- application_tracker
- district_insights_daily (aggregated/anonymised)

Do not store Aadhaar numbers. Do not include real citizen data in fixtures.

## 10. TTS and WhatsApp
TTS must be a provider adapter. Without provider credentials, return a text-only answer and a capability status. Do not invent endpoints.
Implement WhatsApp only after choosing/configuring a provider. Keep tokens and secrets in `.env`; verify webhook signature/challenge according to current provider documentation. Mock webhook tests; never send real messages during tests.

## 11. Tests
Test:
- IndicTrans2 supported language validation and mocked translation path.
- Hindi→English and English→Hindi optional model integration.
- empty/long inputs.
- ASR not configured response.
- profile extraction, missing values, confidence/evidence.
- numeric values and bigha unit preservation.
- rule engine statuses and PPT-specific cases.
- RAG citations and no-source fallback.
- audio MIME/size validation.
- no Aadhaar storage; no full transcript/audio logging.

Run tests; fix what is locally fixable. Model downloads, GPU, API keys and live provider accounts should be optional integration tests, clearly labelled.

## 12. Required deliverables
- Complete backend code.
- `.env.example`.
- compatible `requirements.txt`.
- exact Windows+WSL2 setup/run/test steps in README.
- database schema/migrations and seed loader.
- official data provenance retained.
- unit tests.
- `IMPLEMENTATION_STATUS.md` stating implemented, tested, blocked and credential-required items.
- curl examples for every endpoint.

## 13. Execution order
1. Inspect workspace; make a brief plan.
2. Complete IndicTrans2 integration and tests first.
3. Complete transcript profile extraction and eligibility engine.
4. Implement/document ASR, RAG and TTS adapters.
5. Complete DB seeding and API endpoints.
6. Run tests, fix failures, update README/status.

Do not stop after a plan. Make changes in this workspace and report exact commands for me to run next.
