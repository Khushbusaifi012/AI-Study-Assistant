import hashlib
import re
from pathlib import Path

import fitz

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, UPLOADS_DIR
from app.rag.store import get_collection, use_local_embeddings
from app.rag.embeddings import embed_texts


def _chunk_text(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def _read_pdf(path: Path) -> str:
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix in {".txt", ".md"}:
        return _read_text_file(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _file_doc_id(filename: str) -> str:
    return hashlib.sha256(filename.encode()).hexdigest()[:16]


def ingest_file(uploaded_name: str, raw_bytes: bytes) -> dict:
    safe_name = Path(uploaded_name).name
    dest = UPLOADS_DIR / safe_name
    dest.write_bytes(raw_bytes)

    text = load_document_text(dest)
    chunks = _chunk_text(text)
    if not chunks:
        return {"ok": False, "message": "No readable text found in this file."}

    collection = get_collection()
    doc_id = _file_doc_id(safe_name)

    existing = collection.get(where={"source": safe_name})
    if existing and existing.get("ids"):
        collection.delete(ids=existing["ids"])

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": safe_name,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]

    if use_local_embeddings():
        collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        mode = "local (no API)"
    else:
        embeddings = embed_texts(chunks)
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        mode = "cloud API"

    return {
        "ok": True,
        "message": f"{safe_name} is ready for questions ({len(chunks)} sections indexed).",
        "chunks": len(chunks),
        "filename": safe_name,
        "mode": mode,
    }


def list_indexed_files() -> list[str]:
    collection = get_collection()
    result = collection.get(include=["metadatas"])
    sources = set()
    for meta in result.get("metadatas") or []:
        if meta and meta.get("source"):
            sources.add(meta["source"])
    return sorted(sources)


def remove_indexed_file(filename: str) -> dict:
    safe_name = Path(filename).name
    if not safe_name:
        return {"ok": False, "message": "Invalid filename."}

    collection = get_collection()
    existing = collection.get(where={"source": safe_name})
    ids = existing.get("ids") if existing else None
    if not ids:
        return {"ok": False, "message": f"{safe_name} is not in the index."}

    collection.delete(ids=ids)

    upload_path = UPLOADS_DIR / safe_name
    if upload_path.is_file():
        upload_path.unlink()

    return {
        "ok": True,
        "message": f"{safe_name} was removed from your study materials.",
        "filename": safe_name,
    }
