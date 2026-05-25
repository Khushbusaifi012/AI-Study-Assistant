import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99, 102, 241, 0.18), transparent),
        linear-gradient(180deg, #FAFBFF 0%, #F4F6FB 50%, #EEF1F8 100%);
}

.block-container {
    padding-top: 0.75rem;
    padding-bottom: 2rem;
    max-width: 880px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(195deg, #0F172A 0%, #1E293B 55%, #334155 100%);
    box-shadow: 4px 0 24px rgba(15, 23, 42, 0.12);
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption {
    color: #CBD5E1 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #F8FAFC !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
}
section[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #E2E8F0 !important;
    border-radius: 10px !important;
}

/* ── Hero ── */
.sa-hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(125deg, #4338CA 0%, #6366F1 40%, #7C3AED 100%);
    border-radius: 24px;
    padding: 2rem 2.25rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow:
        0 4px 6px -1px rgba(67, 56, 202, 0.15),
        0 25px 50px -12px rgba(99, 102, 241, 0.35);
}
.sa-hero::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -15%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.sa-hero-inner { position: relative; z-index: 1; }
.sa-hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #E0E7FF !important;
    margin-bottom: 0.75rem;
}
.sa-hero h1 {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2.5rem;
    font-weight: 600;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.03em;
    color: #FFFFFF !important;
    line-height: 1.15;
}
.sa-hero p {
    margin: 0;
    font-size: 1rem;
    color: rgba(255,255,255,0.88) !important;
    max-width: 32rem;
}

/* ── Stat pills ── */
.sa-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.sa-stat {
    background: #FFFFFF;
    border: 1px solid #E8ECF4;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.sa-stat:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}
.sa-stat-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94A3B8 !important;
    margin-bottom: 0.2rem;
}
.sa-stat-value {
    font-size: 1rem;
    font-weight: 700;
    color: #1E293B !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.sa-stat-icon { font-size: 1.1rem; margin-right: 0.35rem; }

/* ── Chat panel ── */
.sa-chat-panel {
    background: #FFFFFF;
    border: 1px solid #E8ECF4;
    border-radius: 20px;
    padding: 1.25rem 1.35rem 0.5rem;
    min-height: 200px;
    box-shadow: 0 4px 24px -6px rgba(15, 23, 42, 0.07);
}
.sa-chat-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B !important;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.sa-chat-dot {
    width: 8px;
    height: 8px;
    background: #22C55E;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.25);
}

/* ── Empty & prompts ── */
.sa-welcome {
    text-align: center;
    padding: 2rem 1rem 1.25rem;
}
.sa-welcome h3 {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.35rem;
    color: #1E293B !important;
    margin: 0 0 0.35rem 0;
}
.sa-welcome p {
    color: #64748B !important;
    font-size: 0.92rem;
    margin: 0;
}
.sa-steps {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 1.25rem 0 0;
}
.sa-step {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.78rem;
    font-weight: 500;
    color: #475569 !important;
}
.sa-step-num {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: white !important;
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
}

/* Sidebar */
.sa-sidebar-brand {
    padding: 0.25rem 0 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1rem;
}
.sa-sidebar-brand h2 {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
    color: #FFFFFF !important;
}
.sa-sidebar-brand p {
    margin: 0.2rem 0 0;
    font-size: 0.82rem;
    color: #94A3B8 !important;
}
.sa-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8 !important;
    margin-bottom: 0.5rem;
}
.sa-file-chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(129, 140, 248, 0.25);
    border-radius: 10px;
    padding: 0.55rem 0.8rem;
    margin-bottom: 0.35rem;
    font-size: 0.8rem;
    font-weight: 500;
    color: #E0E7FF !important;
}
.sa-file-dot {
    width: 6px;
    height: 6px;
    background: #4ADE80;
    border-radius: 50%;
    flex-shrink: 0;
}

/* Suggestion buttons in main */
div[data-testid="stMain"] button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    color: #334155 !important;
    font-weight: 500 !important;
    padding: 0.65rem 0.85rem !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04) !important;
}
div[data-testid="stMain"] button[kind="secondary"]:hover {
    border-color: #A5B4FC !important;
    background: #EEF2FF !important;
    color: #4338CA !important;
    transform: translateY(-1px);
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: transparent !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #F8FAFC !important;
    border: 1px solid #EEF2F6 !important;
    border-radius: 16px !important;
    padding: 0.25rem 0.5rem !important;
}

.stChatInput > div {
    border-radius: 16px !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: 0 4px 16px -4px rgba(15, 23, 42, 0.08) !important;
    background: #FFFFFF !important;
}
.stChatInput textarea { font-size: 0.95rem !important; }

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
"""


def inject_styles() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_stats(subject: str, topic: str, indexed_count: int) -> None:
    topic_val = topic if topic and topic != "Not set" else "—"
    subject_val = subject if subject and subject != "General" else "—"
    files_val = (
        f"{indexed_count} ready" if indexed_count else "None yet"
    )
    st.markdown(
        f"""
        <div class="sa-stats">
            <div class="sa-stat">
                <div class="sa-stat-label">Subject</div>
                <div class="sa-stat-value"><span class="sa-stat-icon">📘</span>{subject_val}</div>
            </div>
            <div class="sa-stat">
                <div class="sa-stat-label">Topic</div>
                <div class="sa-stat-value"><span class="sa-stat-icon">📖</span>{topic_val}</div>
            </div>
            <div class="sa-stat">
                <div class="sa-stat-label">Materials</div>
                <div class="sa-stat-value"><span class="sa-stat-icon">📎</span>{files_val}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="sa-hero">
            <div class="sa-hero-inner">
                <span class="sa-hero-tag">Context-aware · RAG</span>
                <h1>Study Assistant</h1>
                <p>Ask doubts grounded in your uploaded notes and PDFs — step-by-step, exam-ready answers.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.markdown(
        """
        <div class="sa-sidebar-brand">
            <h2>Study Assistant</h2>
            <p>Your personal doubt solver</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_empty() -> None:
    st.markdown(
        """
        <div class="sa-welcome">
            <h3>Start learning</h3>
            <p>Index your PDF in the sidebar, then ask anything below.</p>
            <div class="sa-steps">
                <span class="sa-step"><span class="sa-step-num">1</span> Upload</span>
                <span class="sa-step"><span class="sa-step-num">2</span> Index</span>
                <span class="sa-step"><span class="sa-step-num">3</span> Ask</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def open_chat_panel() -> None:
    st.markdown(
        '<div class="sa-chat-panel"><div class="sa-chat-label">'
        '<span class="sa-chat-dot"></span> Conversation</div>',
        unsafe_allow_html=True,
    )


def close_chat_panel() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
