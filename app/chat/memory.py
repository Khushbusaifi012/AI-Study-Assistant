def init_session():
    defaults = {
        "messages": [],
        "subject": "General",
        "topic": "Not set",
        "level": "High school",
        "indexed_notice": "",
    }
    return defaults


def format_history(messages: list[dict], max_turns: int = 8) -> str:
    recent = messages[-(max_turns * 2) :]
    lines: list[str] = []
    for msg in recent:
        role = "Student" if msg["role"] == "user" else "Tutor"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines) if lines else "(No prior messages in this session.)"
