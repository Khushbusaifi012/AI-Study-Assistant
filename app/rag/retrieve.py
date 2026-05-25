from app.config import TOP_K_CHUNKS
from app.rag.store import get_collection, use_local_embeddings
from app.rag.embeddings import embed_texts


def _expand_query(query: str) -> str:
    q = query.lower()
    extra: list[str] = []
    if "argument" in q:
        extra.extend(
            [
                "parameter",
                "positional",
                "keyword",
                "default",
                "variable length",
                "*args",
                "**kwargs",
            ]
        )
    if "lambda" in q:
        extra.extend(["anonymous function", "lambda argument expression", "syntax"])
    if "function" in q and ("type" in q or "types" in q):
        extra.extend(
            [
                "built in",
                "user defined",
                "pre defined",
                "types of functions",
            ]
        )
    elif "user defined" in q or "user-defined" in q:
        extra.extend(
            ["user defined functions", "def", "reusability", "programmer", "return"]
        )
    elif "function" in q or "def " in q:
        extra.append("user defined function syntax advantages reusability")
    if extra:
        return f"{query} {' '.join(extra)}"
    return query


def retrieve_context(query: str, n_results: int = TOP_K_CHUNKS) -> tuple[str, list[dict]]:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return "", []

    search_query = _expand_query(query)
    n = min(n_results, count)
    if use_local_embeddings():
        results = collection.query(
            query_texts=[search_query],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
    else:
        query_embedding = embed_texts([search_query], task_type="retrieval_query")[0]
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )

    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    blocks: list[str] = []
    citations: list[dict] = []
    for i, doc in enumerate(documents):
        meta = metadatas[i] if i < len(metadatas) else {}
        source = meta.get("source", "unknown")
        chunk_index = meta.get("chunk_index", i)
        blocks.append(f"[{source} — section {chunk_index + 1}]\n{doc}")
        citations.append(
            {
                "source": source,
                "chunk_index": chunk_index,
                "distance": distances[i] if i < len(distances) else None,
            }
        )

    return "\n\n---\n\n".join(blocks), citations
