import re
from pathlib import Path

from app.rag.ingest import list_indexed_files
from app.rag.retrieve import retrieve_context
from app.rag.store import get_collection


def _fallback_no_files(subject: str, topic: str, limit: int) -> list[str]:
    t = (topic or "").strip()
    s = (subject or "").strip()
    if t and t.lower() not in {"not set", "functions", "general"}:
        return [
            f"What are the main ideas about {t}?",
            f"Explain {t} in simple terms.",
            f"What should I remember about {t} for an exam?",
            f"Give me an example related to {t}.",
        ][:limit]
    if s:
        return [
            f"What topics does my {s} material cover?",
            f"Summarize the key points from my uploaded notes.",
            f"What is the most important concept in these notes?",
            f"Quiz me on one idea from my material.",
        ][:limit]
    return [
        "What are the main topics in my uploaded notes?",
        "Summarize the key points from my material.",
        "What is the most important concept here?",
        "Give me a practice question from my notes.",
    ][:limit]


def _sample_all_chunks(max_chunks: int = 16) -> str:
    collection = get_collection()
    if collection.count() == 0:
        return ""
    result = collection.get(include=["documents"], limit=max_chunks)
    docs = [d for d in (result.get("documents") or []) if d and d.strip()]
    return "\n\n".join(docs)


def _is_good_topic(t: str) -> bool:
    if len(t.split()) > 10:
        return False
    letters = [c for c in t if c.isalpha()]
    if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.45:
        return False
    words = [w.lower() for w in re.findall(r"\b\w+\b", t)]
    if len(words) >= 3 and len(words) != len(set(words)):
        return False
    return True


def _extract_topics(text: str) -> list[str]:
    topics: list[str] = []
    seen: set[str] = set()

    def add(raw: str) -> None:
        t = re.sub(r"\s+", " ", raw).strip(" .:-")
        if len(t) < 3 or len(t) > 70 or not _is_good_topic(t):
            return
        key = t.lower()
        if key in seen:
            return
        seen.add(key)
        topics.append(t)

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(":") and 2 <= len(line.split()) <= 12:
            add(line[:-1])
            continue
        if re.match(r"^(?:\d+[\.)]\s*)+[A-Z]", line) and len(line.split()) <= 14:
            add(re.sub(r"^(?:\d+[\.)]\s*)+", "", line))
            continue
        if re.match(r"^[A-Z][A-Za-z0-9\s\-]{2,50}$", line) and len(line.split()) <= 10:
            add(line)

    patterns = [
        r"(?:types of|definition of|introduction to|overview of)\s+([a-z][\w\s\-]{2,45})",
        r"\b(try[\s\-]?except|except\s+block|finally\s+block|raise\s+statement)\b",
        r"\b(exception handling|custom exception|built[\s\-]?in exception)\b",
        r"\b([A-Z][a-z]+(?:Error|Exception))\b",
        r"\*\*([A-Za-z][\w\s]{2,40})\*\*",
        r"`([A-Za-z_][\w]*)`",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.I):
            add(m.group(1) if m.lastindex else m.group(0))

    return topics


def _build_questions(topics: list[str], topic: str, subject: str, limit: int) -> list[str]:
    questions: list[str] = []
    used: set[str] = set()

    def push(q: str) -> None:
        key = q.lower()
        if key in used or len(questions) >= limit:
            return
        used.add(key)
        questions.append(q)

    ui_topic = (topic or "").strip()
    if ui_topic and ui_topic.lower() not in {"not set", "functions"}:
        push(f"What is {ui_topic}?")
        push(f"Explain {ui_topic} with an example from my notes.")
        push(f"What are the important points about {ui_topic}?")

    templates = [
        "What is {t}?",
        "Explain {t} in simple terms.",
        "How does {t} work according to my notes?",
        "What should I remember about {t}?",
    ]
    for i, t in enumerate(topics):
        push(templates[i % len(templates)].format(t=t))

    if subject and len(questions) < limit:
        push(f"What does my {subject} material say about {ui_topic or 'this topic'}?")

    files = list_indexed_files()
    if files and len(questions) < limit:
        push(f"Summarize the main ideas in {Path(files[0]).stem}.")

    return questions[:limit]


def generate_suggestions(
    subject: str = "",
    topic: str = "",
    limit: int = 4,
) -> list[str]:
    if not list_indexed_files():
        return _fallback_no_files(subject, topic, limit)

    seed = " ".join(
        p
        for p in [subject, topic, "key concepts definitions examples"]
        if p and p.strip()
    ).strip()
    context, _ = retrieve_context(seed or "introduction overview", n_results=10)
    if not context:
        context = _sample_all_chunks()

    topics = _extract_topics(context)
    questions = _build_questions(topics, topic, subject, limit)

    if len(questions) < limit:
        for q in _fallback_no_files(subject, topic, limit):
            if q not in questions:
                questions.append(q)
            if len(questions) >= limit:
                break

    return questions[:limit]
