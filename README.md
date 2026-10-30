# SAHAYAK – VS Code Agent Starter

Open this folder in VS Code, then give `VSCODE_AGENT_TASK.md` to your coding agent in **Agent mode**.

## What is included
- IndicTrans2 Hindi ↔ English translation service using AI4Bharat distilled checkpoints.
- FastAPI API with `/health`, `/translate`, `/voice-command/text`, and `/voice-command/audio`.
- A clear ASR adapter boundary: IndicTrans2 translates text; it does not transcribe audio.
- SAHAYAK Himachal pilot dataset workbook, CSV exports, and database files (where included).
- A detailed task prompt asking your VS Code agent to complete ASR, profile extraction, eligibility matching, RAG, TTS, database integration, WhatsApp and tests.

## Windows setup recommendation
The official IndicTransToolkit currently documents Python 3.10+ and a Linux/macOS environment; it says Windows is not built/tested. On a Windows PC, use **WSL2 + Ubuntu**, then open the WSL project folder in VS Code.
Official toolkit guidance: https://github.com/VarunGumma/IndicTransToolkit

## Run the starter (WSL2 / Ubuntu)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```
Install PyTorch using the official selector for your CPU/GPU:
https://pytorch.org/get-started/locally/

Then:
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open API docs at http://127.0.0.1:8000/docs

## Quick translation test
```bash
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"मेरी उम्र 52 साल है और मेरे पास तीन बीघा जमीन है।","src_lang":"hin_Deva","tgt_lang":"eng_Latn"}'
```
The first request downloads the selected model checkpoint(s) from Hugging Face. This requires internet access, disk space, and may be slow on CPU.

## Current status
- `/translate` calls IndicTrans2 when dependencies and model weights are installed.
- `/voice-command/text` tests the pipeline from an already-transcribed Hindi/English sentence.
- `/voice-command/audio` returns a clear 501 until a real ASR provider is configured.
- Real ASR, Gemini, RAG, TTS, and WhatsApp still require coding-agent implementation and provider credentials/configuration.

## Language support
IndicTrans2 supports Hindi (`hin_Deva`) and English (`eng_Latn`). Himachali is not listed as a separate IndicTrans2 language code. For Himachali dialect speech, use an ASR/local-speaker-validated normalisation path into Hindi; do not claim native Himachali translation.

## Safeguards
- IndicTrans2 is translation, not ASR or TTS.
- Keep `3 bigha` as `3 bigha`; never convert using an unverified generic conversion.
- Do not decide eligibility from translation alone.
- Confirm age, land, income and other critical values with the user.
- A preliminary `POTENTIAL_MATCH` is not an official government approval.
- Never store Aadhaar numbers or commit API keys.
