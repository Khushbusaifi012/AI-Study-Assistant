from app.config import GEMINI_API_KEY, LLM_PROVIDER, OPENAI_API_KEY


def _is_quota_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return "429" in text or "quota" in text or "rate" in text


def _provider() -> str:
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        return "openai"
    if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
        return "gemini"
    if GEMINI_API_KEY:
        return "gemini"
    if OPENAI_API_KEY:
        return "openai"
    raise RuntimeError(
        "No API key found. Set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
    )


def embed_texts(
    texts: list[str],
    *,
    task_type: str = "retrieval_document",
) -> list[list[float]]:
    provider = _provider()
    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return [item.embedding for item in response.data]

    import google.generativeai as genai
    import time

    genai.configure(api_key=GEMINI_API_KEY)
    vectors: list[list[float]] = []
    batch_size = 20

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=batch,
                task_type=task_type,
            )
            batch_vectors = result["embedding"]
            if batch_vectors and isinstance(batch_vectors[0], (int, float)):
                vectors.append(batch_vectors)
            else:
                vectors.extend(batch_vectors)
        except Exception as exc:
            if _is_quota_error(exc):
                raise RuntimeError(
                    "Embedding quota limit — wait 1–2 minutes, then click "
                    "'Index PDF' once."
                ) from exc
            raise
        if i + batch_size < len(texts):
            time.sleep(0.5)

    return vectors
