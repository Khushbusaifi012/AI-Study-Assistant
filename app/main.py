import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.chat.memory import init_session
from app.chat.tutor import ask_tutor
from app.config import USE_LOCAL_EMBEDDINGS
from app.rag.ingest import ingest_file, list_indexed_files
from app.rag.suggestions import generate_suggestions
from app.ui.styles import (
    close_chat_panel,
    inject_styles,
    open_chat_panel,
    render_header,
    render_sidebar_brand,
    render_stats,
    render_welcome_empty,
)

LEVELS = ["Middle school", "High school", "Undergraduate", "Competitive exam"]


st.set_page_config(
    page_title="Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()


def _ensure_session():
    for key, value in init_session().items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


_ensure_session()


def _level_index() -> int:
    if st.session_state.level in LEVELS:
        return LEVELS.index(st.session_state.level)
    return 1


def _clear_chat():
    st.session_state.messages = []
    st.session_state.pending_prompt = None


def _render_sidebar():
    with st.sidebar:
        render_sidebar_brand()

        st.markdown('<p class="sa-section-label">Context</p>', unsafe_allow_html=True)
        with st.container(border=True):
            st.session_state.subject = st.text_input(
                "Subject",
                value=st.session_state.subject,
                placeholder="Python",
            )
            st.session_state.topic = st.text_input(
                "Topic / chapter",
                value=st.session_state.topic,
                placeholder="Functions",
            )
            st.session_state.level = st.selectbox("Level", LEVELS, index=_level_index())

        st.markdown('<p class="sa-section-label">Materials</p>', unsafe_allow_html=True)
        with st.container(border=True):
            if USE_LOCAL_EMBEDDINGS:
                st.caption("Offline indexing enabled")

            uploaded = st.file_uploader(
                "Upload PDF, TXT, or MD",
                type=["pdf", "txt", "md"],
                accept_multiple_files=True,
            )

            indexed = list_indexed_files()
            if uploaded and not indexed:
                st.warning("Click **Index PDF** after uploading.")
            elif uploaded and indexed:
                pending = [f.name for f in uploaded if f.name not in indexed]
                if pending:
                    st.warning(f"Pending: {', '.join(pending)}")

            if st.button("Index PDF", type="primary", use_container_width=True):
                if not uploaded:
                    st.warning("Select a file first.")
                else:
                    with st.spinner("Indexing…"):
                        for file in uploaded:
                            try:
                                result = ingest_file(file.name, file.getvalue())
                            except Exception as exc:
                                st.error(str(exc))
                                break
                            if result["ok"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])
                    st.rerun()

            indexed = list_indexed_files()
            if indexed:
                for name in indexed:
                    short = name if len(name) <= 28 else name[:25] + "…"
                    st.markdown(
                        f'<div class="sa-file-chip">'
                        f'<span class="sa-file-dot"></span>{short}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No materials indexed yet.")

        st.button(
            "Clear chat",
            use_container_width=True,
            on_click=_clear_chat,
            key="clear_chat",
        )


def _render_suggestions():
    st.markdown("**Quick questions**")
    questions = generate_suggestions(
        subject=st.session_state.subject,
        topic=st.session_state.topic,
        limit=4,
    )
    cols = st.columns(2)
    for i, question in enumerate(questions):
        with cols[i % 2]:
            if st.button(question, use_container_width=True, key=f"suggest_{i}"):
                st.session_state.pending_prompt = question
                st.rerun()


def _render_chat_history():
    for message in st.session_state.messages:
        avatar = "🧑‍🎓" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message.get("citations") and message["role"] == "assistant":
                with st.expander("Sources from your PDF"):
                    for cite in message["citations"]:
                        st.markdown(
                            f"**{cite['source']}** — section {cite['chunk_index'] + 1}"
                        )


def _handle_prompt(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.status("Reading your notes…", expanded=False):
            try:
                result = ask_tutor(
                    question=prompt,
                    messages=st.session_state.messages[:-1],
                    subject=st.session_state.subject,
                    topic=st.session_state.topic,
                    level=st.session_state.level,
                )
                answer = result["answer"]
                if not result["has_context"] and not list_indexed_files():
                    st.info("Index a PDF in the sidebar to unlock context-aware answers.")
            except Exception as exc:
                answer = f"**Something went wrong:** {exc}"
                result = {"citations": [], "has_context": False}

        st.markdown(answer)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "citations": result.get("citations", []),
            }
        )


# ── Layout ──
_render_sidebar()

render_header()
render_stats(
    st.session_state.subject,
    st.session_state.topic,
    len(list_indexed_files()),
)

open_chat_panel()

if st.session_state.pending_prompt:
    pending = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    _handle_prompt(pending)
elif not st.session_state.messages:
    render_welcome_empty()
    _render_suggestions()

_render_chat_history()

close_chat_panel()

if user_input := st.chat_input("Ask anything from your study material…"):
    _handle_prompt(user_input)
