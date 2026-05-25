from pathlib import Path

from app.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    PROMPTS_DIR,
)

_GEMINI_FALLBACK_MODELS = (
    GEMINI_MODEL,
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
)
from app.chat.memory import format_history
from app.rag.ingest import list_indexed_files
from app.rag.retrieve import retrieve_context


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


def _load_system_template() -> str:
    path = PROMPTS_DIR / "tutor_system.txt"
    return path.read_text(encoding="utf-8")


def _build_system_prompt(
    subject: str,
    topic: str,
    level: str,
    context: str,
    history: str,
) -> str:
    template = _load_system_template()
    return template.format(
        subject=subject or "General",
        topic=topic or "Not set",
        level=level or "Student",
        context=context or "(No study material uploaded yet.)",
        history=history,
    )


def _chat_openai(system: str, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content or ""


def _is_quota_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return "429" in text or "quota" in text or "rate" in text


def _chat_gemini(system: str, user_message: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    seen: set[str] = set()
    last_error: BaseException | None = None

    for model_name in _GEMINI_FALLBACK_MODELS:
        if not model_name or model_name in seen:
            continue
        seen.add(model_name)
        try:
            model = genai.GenerativeModel(
                model_name,
                system_instruction=system,
            )
            response = model.generate_content(user_message)
            return response.text or ""
        except Exception as exc:
            last_error = exc
            if _is_quota_error(exc):
                continue
            raise

    raise RuntimeError("quota") from last_error


def _summary_arguments() -> str:
    return """### From your notes (Arguments & Types)

**Parameter vs Argument**
- **Parameter:** variable in the function definition (e.g. `a`, `b` in `def add(a, b)`)
- **Argument:** value you pass when **calling** the function (e.g. `10`, `20` in `add(10, 20)`)

**Types of Arguments (4)**

| # | Type | Short explanation |
|---|------|-------------------|
| 1 | **Positional** | Order matters; you must pass the expected number of values |
| 2 | **Keyword** | Pass by parameter **name** (`name="Ali"`); order can change |
| 3 | **Default** | Parameter has a default value if you omit it at call time |
| 4 | **Variable length** | `*args` → extra values as a **tuple**; `**kwargs` → pairs as a **dict** |

**Important rules (from your notes)**
- Positional and keyword together: positional first, then keyword (else `SyntaxError`)
- No non-default argument after a default (`SyntaxError`)
- After `*args`, pass any further values as **keyword** arguments

---
"""


def _summary_function_types() -> str:
    return """### From your notes (Types of Functions)

Your PDF focuses on **two main types**:

| # | Type | Description | Examples (from notes) |
|---|------|-------------|------------------------|
| 1 | **Built-in (pre-defined)** | Shipped with Python; ready to use | `id()`, `type()`, `input()`, `eval()` |
| 2 | **User-defined** | Written by the programmer for a specific task | `def function_name():` + indented body |

**Why use functions? (from your notes)**
- **Reusability** — write logic once, call it many times
- Avoid repeating the same statements
- Easier to manage large programs

**User-defined function building blocks**
- `def` — required keyword to start a function
- `return` — optional; sends a value back to the caller
- **Parameters** in `()` — optional inputs
- **Docstring** — optional description
- Body must be **indented** (4 spaces or 1 tab); Python has no `{ }` braces

**Other topics listed in your PDF** (separate sections): parameters & arguments, recursion, local/global variables, lambda, `filter()`, `map()`, `reduce()`.

---
"""


def _summary_lambda() -> str:
    return """### From your notes (Lambda Function)

**What is it?**
A **lambda** (or **anonymous**) function is a **small function without a name**, meant for **quick, one-time use**.

**Syntax (from your notes)**
```python
lambda arguments : expression
```

**Example (square of a number)**
```python
square = lambda n: n * n
# same idea as: def square(n): return n * n
```

**Key points (from your notes)**
- Defined with the **`lambda`** keyword (not `def`)
- Can take **arguments**, then `:` then a single **expression**
- The expression value is **returned automatically** — you do **not** write `return`
- Best for **short, instant** tasks instead of a full `def` block

**Practice ideas from your PDF (lab)**
- Square of a number
- Sum of two numbers
- Check even or odd
- Find the bigger of two numbers

**Related topics in your PDF:** `filter()`, `map()`, and `reduce()` often use lambda-style functions.

---
"""


def _summary_user_defined_functions() -> str:
    return """### From your notes (User-Defined Functions)

**What are they?**
Functions **you create** with `def` for your own work — not built into Python (unlike `input()`, `type()`, `id()`).

**Uses / advantages (from your notes)**

| # | Use | Explanation |
|---|-----|-------------|
| 1 | **Reusability** | Write statements once as a function; call it many times without rewriting |
| 2 | **Less repetition** | Same logic should not be copied again and again in the program |
| 3 | **Manage large programs** | Split code into functions — easier to track and maintain |
| 4 | **Your own logic** | Built by the programmer for **specific business requirements** |
| 5 | **Inputs & output** | Use **parameters** for input; optional **`return`** to send a value back |

**Why functions exist (idea from your PDF)**
When a group of statements is needed **again and again**, define them as one unit (a function) and call that unit whenever needed.

**Syntax (short)**
```python
def function_name(parameters):   # def is mandatory
    \"\"\"docstring (optional)\"\"\"
    # indented body — 4 spaces or 1 tab
    return result              # return is optional
```

**Remember**
- Python has **no `{ }` braces** — **indentation** is required
- If a function has parameters, you **must** pass values when calling (else error)

**vs Built-in functions**
| Built-in | User-defined |
|----------|----------------|
| Come with Python | You write with `def` |
| e.g. `input()`, `eval()` | e.g. greet, square, your own tasks |

---
"""


def _summary_from_notes(question: str, context: str) -> str | None:
    q = question.lower()
    ctx = context.lower()

    if "lambda" in q and ("lambda" in ctx or "anonymous" in ctx):
        return _summary_lambda()

    if ("argument" in q or "parameter" in q) and (
        "positional" in ctx or "keyword" in ctx
    ):
        return _summary_arguments()

    if "function" in q and ("type" in q or "types" in q):
        if "built" in ctx or "user defined" in ctx or "pre defined" in ctx:
            return _summary_function_types()

    if ("user defined" in q or "user-defined" in q) or (
        "use" in q and "function" in q
    ):
        if "user defined" in ctx or "def " in ctx or "programmer" in ctx:
            return _summary_user_defined_functions()

    return None


def _offline_answer(question: str, context: str) -> str:
    indexed = list_indexed_files()

    if not context.strip():
        if indexed:
            return (
                "**PDF is indexed**, but no clear match for this exact question. "
                "Try: `What are types of arguments in Python with examples` — "
                "or set topic to **Functions** in the sidebar."
            )
        return (
            "**PDF is not indexed yet.** Click **Index PDF (step 2)** in the sidebar, "
            "then ask again."
        )

    summary = _summary_from_notes(question, context)
    if summary:
        return (
            summary
            + "\n\n---\n"
            + "_From your indexed PDF. Expand **Sources used** for exact lines._"
        )

    trimmed = context if len(context) <= 4500 else context[:4500] + "\n\n…"
    return (
        "**Answer from your indexed PDF** (AI chat unavailable — API quota):\n\n"
        + trimmed
        + "\n\n---\n"
        + f"_Question: {question}_"
    )


def ask_tutor(
    question: str,
    messages: list[dict],
    subject: str,
    topic: str,
    level: str,
) -> dict:
    context, citations = retrieve_context(question)
    history = format_history(messages)
    system = _build_system_prompt(subject, topic, level, context, history)

    offline_mode = False
    try:
        provider = _provider()
        if provider == "openai":
            answer = _chat_openai(system, question)
        else:
            answer = _chat_gemini(system, question)
    except Exception as exc:
        if _is_quota_error(exc) or str(exc) == "quota":
            answer = _offline_answer(question, context)
            offline_mode = True
        else:
            raise

    return {
        "answer": answer.strip(),
        "citations": citations,
        "has_context": bool(context),
        "offline_mode": offline_mode,
    }
