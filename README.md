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

3. Run the app (choose one UI):

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

4. Set **Subject** and **Topic**, upload a PDF, click **Index PDF**, then ask in chat.

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
5. The LLM replies as a step-by-step tutor grounded in those excepts.
