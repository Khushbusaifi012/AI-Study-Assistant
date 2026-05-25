import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.chat.tutor import ask_tutor
from app.config import USE_LOCAL_EMBEDDINGS
from app.rag.ingest import ingest_file, list_indexed_files, remove_indexed_file

app = FastAPI(title="Study Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    subject: str = "General"
    topic: str = "Not set"
    level: str = "High school"
    messages: list[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    source: str
    chunk_index: int
    distance: float | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    has_context: bool
    offline_mode: bool


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/config")
def config():
    return {"local_embeddings": USE_LOCAL_EMBEDDINGS}


@app.get("/api/files")
def files():
    return {"files": list_indexed_files()}


@app.delete("/api/files/{filename:path}")
def delete_indexed_file(filename: str):
    safe_name = Path(filename).name
    try:
        result = remove_indexed_file(safe_name)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc

    if not result.get("ok"):
        raise HTTPException(404, result.get("message", "File not found"))

    return result


@app.post("/api/index")
async def index_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(400, "Only PDF, TXT, and MD files are supported")

    raw = await file.read()
    if not raw:
        raise HTTPException(400, "Empty file")

    try:
        result = ingest_file(file.filename, raw)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc

    if not result.get("ok"):
        raise HTTPException(400, result.get("message", "Indexing failed"))

    return result


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in body.messages]
    try:
        result = ask_tutor(
            question=body.question,
            messages=history,
            subject=body.subject,
            topic=body.topic,
            level=body.level,
        )
    except RuntimeError as exc:
        raise HTTPException(500, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Chat failed: {exc}") from exc

    citations = [
        Citation(
            source=c.get("source", "unknown"),
            chunk_index=c.get("chunk_index", 0),
            distance=c.get("distance"),
        )
        for c in result.get("citations", [])
    ]

    return ChatResponse(
        answer=result["answer"],
        citations=citations,
        has_context=result.get("has_context", False),
        offline_mode=result.get("offline_mode", False),
    )
