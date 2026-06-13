# ScreenCopilot

**Drop a screenshot. Get a plain-English explanation and action list in under 10 seconds. Runs 100% locally — no API keys, no cloud, no data leaves your machine.**

![ScreenCopilot UI](https://placeholder.pics/svg/800x400/141417/6c6fff/ScreenCopilot)

---

## Why

You're looking at a cryptic error message, an unfamiliar UI, or a dense settings screen. You know roughly what you want to do — you just don't know what the screen is telling you. ScreenCopilot reads the screen and tells you exactly what's happening and what to do next, using a local LLM so nothing is sent anywhere.

---

## What it does

| Input | Output |
|---|---|
| Any screenshot (drag & drop or browse) | Plain-English explanation of what's on screen |
| | 3–5 concrete action suggestions |
| | Searchable local history |

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11 · FastAPI · Uvicorn |
| OCR | Tesseract 5 via pytesseract |
| LLM | Ollama (Llama3 / Phi-3 — your choice) |
| Storage | SQLite (local, `~/.screen-copilot/history.db`) |
| Desktop UI | Tauri 1 (Rust shell + HTML/CSS/JS frontend) |

---

## Requirements

- Python 3.11+
- [Tesseract 5](https://github.com/tesseract-ocr/tesseract#installing-tesseract)
- [Ollama](https://ollama.com) with at least one model pulled
- Rust + Tauri CLI (for desktop app build)

---

## Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/screen-copilot
cd screen-copilot

# 2. Pull a model (fast, ~4GB)
ollama pull llama3
# or for lower RAM:
ollama pull phi3

# 3. Python backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Start backend
python src/main.py
# → running at http://127.0.0.1:8765

# 5. Open UI (browser for dev, or build with Tauri)
open src/ui/index.html
```

### Desktop app (Tauri)

```bash
cargo install tauri-cli
cargo tauri dev      # dev mode
cargo tauri build    # production binary
```

---

## Usage

1. Start Ollama: `ollama serve`
2. Start backend: `python src/main.py`
3. Open the app, drag in a screenshot, click **Analyze**
4. Done — explanation + actions appear in under 10 seconds

Switch models anytime from the dropdown in the top-right.

---

## Project structure

```
screen-copilot/
├── src/
│   ├── main.py              # FastAPI entry point (port 8765)
│   ├── api/
│   │   ├── screenshot.py    # Upload + analyze endpoints
│   │   └── analysis.py      # History + search endpoints
│   ├── core/
│   │   ├── ocr.py           # Tesseract wrapper
│   │   ├── llm.py           # Ollama client + prompt
│   │   └── storage.py       # SQLite CRUD
│   ├── ui/
│   │   ├── index.html
│   │   ├── app.css
│   │   └── app.js
│   └── utils/
│       └── helpers.py
├── tests/
│   ├── test_ocr.py
│   └── test_analysis.py
├── requirements.txt
├── Cargo.toml
└── tauri.conf.json
```

---

## API

```
POST /screenshot/upload          multipart file upload → analysis
POST /screenshot/analyze-b64     base64 image JSON → analysis
GET  /analysis/history?limit=20  recent analyses
GET  /analysis/search?q=<query>  full-text search
DELETE /analysis/{id}            delete a record
GET  /analysis/models            list available Ollama models
GET  /health                     liveness check
```

---

## Tests

```bash
pytest tests/ -v
```

---

## Privacy

Everything runs on your machine. The only network calls are:
- `localhost:11434` → Ollama (local)
- `localhost:8765` → backend (local)
- `fonts.googleapis.com` → Inter font (can be self-hosted to go fully offline)

No telemetry. No accounts. No keys.

---

## Roadmap

- [ ] Clipboard paste support (Ctrl+V to analyze)
- [ ] System tray with global hotkey
- [ ] Batch analysis mode
- [ ] Custom prompt templates

---

## License

MIT
