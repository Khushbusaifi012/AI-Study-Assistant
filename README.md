# AI Study Assistant

Context-aware doubt solver that answers from **your** uploaded notes (PDF, TXT, MD) using RAG, plus session context (subject, topic, level).

## Quick start

1. **Python 3.11+** installed.

2. Create a virtual environment and install dependencies:

```bash
cd "Study Assitant"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Copy environment file and add an API key:

```bash
copy .env.example .env
```

Edit `.env`:

- **Gemini (recommended, free tier):** set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=...`
- **OpenAI:** set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...`

Get a Gemini key: https://aistudio.google.com/apikey

4. Run the app (choose one UI):

### React UI (recommended)

**Terminal 1 — API:**
```bash
pip install -r requirements.txt
uvicorn app.api.server:app --reload --port 8000
```
Or double-click `run-api.bat`

**Terminal 2 — React:**
```bash
cd frontend
npm install
npm run dev
```
Or double-click `run-react.bat`

Open **http://localhost:5173**

### Streamlit UI (legacy)

```bash
streamlit run app/main.py
```

5. Set **Subject** and **Topic**, upload a PDF, click **Index PDF**, then ask in chat.

## Project layout

```
frontend/           # React + Vite UI
app/
  api/server.py     # FastAPI for React
  main.py           # Streamlit UI (optional)
  config.py         # paths and settings
  chat/tutor.py     # LLM + embeddings
  chat/memory.py    # conversation formatting
  rag/ingest.py     # PDF/text chunking and indexing
  rag/retrieve.py   # similarity search
  rag/store.py      # Chroma vector DB
data/
  uploads/          # saved files
  chroma/           # vector index (local)
```

## How it works

1. Documents are split into overlapping chunks and embedded.
2. Chunks are stored in a local Chroma database.
3. Each question retrieves the most relevant chunks.
4. The tutor prompt includes subject/topic/level, excerpts, and recent chat history.
5. The LLM replies as a step-by-step tutor grounded in those excerpts.

## Troubleshooting

### `ECONNREFUSED` or Vite proxy errors
Start the API first (`run-api.bat`), then React (`run-react.bat`), or use `run-dev.bat` from the **project root** (not the `frontend` folder).

### `WinError 10013` on port 8000
Port 8000 is already in use. Either:
- The API is **already running** — open http://127.0.0.1:8000/api/health (should show `{"status":"ok"}`), then only start React.
- Or run `stop-api.bat`, then `run-api.bat` again.

### `run-dev.bat` not found (PowerShell)
Use `.\run-dev.bat` and make sure you are in the `Study Assitant` folder (parent of `frontend`), not inside `frontend`.

### Run uvicorn from project root
```powershell
cd "C:\Users\FARUKH KHAN\OneDrive\khushbu personal\Study Assitant"
.\venv\Scripts\Activate.ps1
uvicorn app.api.server:app --reload --port 8000
```
Do **not** run uvicorn from the `frontend` folder.

- **No API key:** ensure `.env` exists in the project root (same folder as `requirements.txt`).
- **Empty PDF text:** some scanned PDFs have no selectable text; use OCR or a text-based PDF.
- **Gemini model errors:** change the model name in `app/chat/tutor.py` to `gemini-1.5-flash` if needed.
