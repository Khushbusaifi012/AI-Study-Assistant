import { useCallback, useEffect, useRef, useState } from "react";
import {
  fetchFiles,
  fetchSuggestions,
  indexFile,
  removeIndexedFile,
  sendChat,
} from "./api";
import ConfirmModal from "./ConfirmModal";
import { renderMarkdown } from "./markdown";
import { getStoredTheme, toggleTheme, type Theme } from "./theme";
import type { Message, StudyContext } from "./types";
import { DEFAULT_SUGGESTIONS, LEVELS } from "./types";

type ConfirmState = {
  title: string;
  message: string;
  confirmLabel: string;
  danger?: boolean;
  success?: boolean;
  onConfirm: () => void;
};

type AlertState = {
  title: string;
  message: string;
};

const defaultContext: StudyContext = {
  subject: "Python",
  topic: "Functions",
  level: "High school",
};

export default function App() {
  const [ctx, setCtx] = useState<StudyContext>(defaultContext);
  const [files, setFiles] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>(DEFAULT_SUGGESTIONS);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [toast, setToast] = useState<{ type: "error" | "success"; text: string } | null>(null);
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);
  const [successAlert, setSuccessAlert] = useState<AlertState | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [theme, setTheme] = useState<Theme>(getStoredTheme);
  const fileRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const chatSessionRef = useRef(0);

  const newId = () =>
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random()}`;

  const clearChat = () => {
    chatSessionRef.current += 1;
    setMessages([]);
    setInput("");
    setLoading(false);
  };

  const showToast = (type: "error" | "success", text: string) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 4000);
  };

  const refreshFiles = useCallback(async () => {
    try {
      setFiles(await fetchFiles());
    } catch {
      setFiles([]);
    }
  }, []);

  const refreshSuggestions = useCallback(async () => {
    try {
      const next = await fetchSuggestions(ctx);
      setSuggestions(next.length > 0 ? next : DEFAULT_SUGGESTIONS);
    } catch {
      setSuggestions(DEFAULT_SUGGESTIONS);
    }
  }, [ctx]);

  useEffect(() => {
    refreshFiles();
  }, [refreshFiles]);

  useEffect(() => {
    void refreshSuggestions();
  }, [refreshSuggestions, files]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const runRemoveIndexed = async (filename: string) => {
    try {
      const result = await removeIndexedFile(filename);
      if (pendingFile?.name === filename) {
        setPendingFile(null);
        if (fileRef.current) fileRef.current.value = "";
      }
      await refreshFiles();
      setSuccessAlert({
        title: "File removed",
        message:
          result.message ??
          `"${filename}" was removed from your index. Upload again anytime to re-index.`,
      });
    } catch (e) {
      showToast("error", e instanceof Error ? e.message : "Remove failed");
    }
  };

  const handleRemoveIndexed = (filename: string) => {
    setConfirm({
      title: "Remove from index",
      message: `Remove "${filename}" from your study materials? You can upload and index it again later.`,
      confirmLabel: "Remove",
      danger: true,
      onConfirm: () => {
        setConfirm(null);
        void runRemoveIndexed(filename);
      },
    });
  };

  const requestClearChat = () => {
    setConfirm({
      title: "Clear chat",
      message:
        "Clear all messages in this conversation? Your indexed PDFs will not be removed.",
      confirmLabel: "Clear chat",
      danger: true,
      onConfirm: () => {
        setConfirm(null);
        clearChat();
      },
    });
  };

  const handleIndex = async () => {
    if (!pendingFile) {
      showToast("error", "Choose a file first");
      return;
    }
    setIndexing(true);
    const fileName = pendingFile.name;
    try {
      const result = await indexFile(pendingFile);
      showToast(
        "success",
        result.message ??
          `"${fileName}" indexed successfully! You can ask questions now.`
      );
      setPendingFile(null);
      if (fileRef.current) fileRef.current.value = "";
      await refreshFiles();
      await refreshSuggestions();
    } catch (e) {
      showToast("error", e instanceof Error ? e.message : "Index failed");
    } finally {
      setIndexing(false);
    }
  };

  const ask = async (question: string) => {
    const q = question.trim();
    if (!q || loading) return;

    const session = chatSessionRef.current;
    const history = messages;

    const userMsg: Message = { id: newId(), role: "user", content: q };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChat(q, ctx, history);
      if (session !== chatSessionRef.current) return;

      setMessages((m) => [
        ...m,
        {
          id: newId(),
          role: "assistant",
          content: res.answer,
          citations: res.citations,
        },
      ]);
    } catch (e) {
      if (session !== chatSessionRef.current) return;

      setMessages((m) => [
        ...m,
        {
          id: newId(),
          role: "assistant",
          content: `**Error:** ${e instanceof Error ? e.message : "Request failed"}`,
        },
      ]);
    } finally {
      if (session === chatSessionRef.current) {
        setLoading(false);
      }
    }
  };

  const onFilePick = (f: File | null) => {
    if (!f) return;
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "txt", "md"].includes(ext ?? "")) {
      showToast("error", "Only PDF, TXT, MD allowed");
      return;
    }
    setPendingFile(f);
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-row">
            <span className="brand-logo" aria-hidden>
              SA
            </span>
            <div>
              <h1>Study Assistant</h1>
              <p>Upload · Index · Ask</p>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-title">Context</div>
          <div className="field">
            <label>Subject</label>
            <input
              value={ctx.subject}
              onChange={(e) => setCtx({ ...ctx, subject: e.target.value })}
              placeholder="Python"
            />
          </div>
          <div className="field">
            <label>Topic / chapter</label>
            <input
              value={ctx.topic}
              onChange={(e) => setCtx({ ...ctx, topic: e.target.value })}
              placeholder="Functions"
            />
          </div>
          <div className="field">
            <label>Level</label>
            <div className="level-pills" role="listbox" aria-label="Level">
              {LEVELS.map((l) => (
                <button
                  key={l}
                  type="button"
                  role="option"
                  aria-selected={ctx.level === l}
                  className={`level-pill${ctx.level === l ? " active" : ""}`}
                  onClick={() => setCtx({ ...ctx, level: l })}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="panel materials-panel">
          <div className="panel-title">Materials</div>

          <label
            className="file-zone"
            onDragOver={(e) => {
              e.preventDefault();
              e.currentTarget.classList.add("dragover");
            }}
            onDragLeave={(e) => e.currentTarget.classList.remove("dragover")}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.classList.remove("dragover");
              onFilePick(e.dataTransfer.files[0] ?? null);
            }}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.txt,.md"
              onChange={(e) => onFilePick(e.target.files?.[0] ?? null)}
            />
            <span className="file-zone-icon">📄</span>
            <span className="file-zone-text">
              {pendingFile ? "Change file" : "Drop PDF or click to browse"}
            </span>
            <span className="file-zone-hint">PDF, TXT, or MD</span>
          </label>

          {pendingFile && (
            <div className="pending-file">
              <span className="pending-file-name" title={pendingFile.name}>
                {pendingFile.name}
              </span>
              <button
                type="button"
                className="pending-file-clear"
                onClick={() => {
                  setPendingFile(null);
                  if (fileRef.current) fileRef.current.value = "";
                }}
                aria-label="Remove file"
              >
                ×
              </button>
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={handleIndex}
            disabled={indexing || !pendingFile}
          >
            {indexing ? "Indexing…" : "Index PDF"}
          </button>

          <div className="indexed-section">
            <div className="indexed-label">Indexed</div>
            {files.length === 0 ? (
              <p className="indexed-empty">No files indexed yet</p>
            ) : (
              <div className="file-list">
                {files.map((f) => (
                  <div key={f} className="file-chip" title={f}>
                    <span className="file-dot" />
                    <span className="file-chip-name">
                      {f.length > 22 ? f.slice(0, 19) + "…" : f}
                    </span>
                    <button
                      type="button"
                      className="file-chip-remove"
                      onClick={() => handleRemoveIndexed(f)}
                      aria-label={`Remove ${f}`}
                      title="Remove from index"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <button
          type="button"
          className="btn btn-ghost"
          onClick={requestClearChat}
          disabled={messages.length === 0 && !loading}
        >
          Clear chat
        </button>
      </aside>

      <main className="main">
        <div className="main-topbar">
          <div
            className={`status-pill${files.length ? " status-pill--ready" : ""}`}
          >
            <span className="status-dot" />
            {files.length
              ? `${files.length} material${files.length > 1 ? "s" : ""} indexed`
              : "Upload & index a PDF to start"}
          </div>
          <button
            type="button"
            className="theme-toggle theme-toggle--bar"
            onClick={() => setTheme((t) => toggleTheme(t))}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            title={theme === "dark" ? "Light mode" : "Dark mode"}
          >
            <span className="theme-toggle-icon" aria-hidden>
              {theme === "dark" ? "☀" : "☾"}
            </span>
            <span className="theme-toggle-label">
              {theme === "dark" ? "Light" : "Dark"}
            </span>
          </button>
        </div>

        <header className="hero">
          <span className="hero-tag">AI · RAG · PDF</span>
          <h2>Your personal study tutor</h2>
          <p>Answers grounded in your uploaded notes — set subject & topic in the sidebar.</p>
        </header>

        <div className="stats">
          <div className="stat stat--subject">
            <span className="stat-icon" aria-hidden>
              ◈
            </span>
            <div>
              <div className="stat-label">Subject</div>
              <div className="stat-value">{ctx.subject || "—"}</div>
            </div>
          </div>
          <div className="stat stat--topic">
            <span className="stat-icon" aria-hidden>
              ◉
            </span>
            <div>
              <div className="stat-label">Topic</div>
              <div className="stat-value">{ctx.topic || "—"}</div>
            </div>
          </div>
          <div className="stat stat--materials">
            <span className="stat-icon" aria-hidden>
              ◫
            </span>
            <div>
              <div className="stat-label">Materials</div>
              <div className="stat-value">
                {files.length ? `${files.length} ready` : "None"}
              </div>
            </div>
          </div>
        </div>

        <section className="chat-panel">
          <div className="chat-header">
            <span className="live-dot" />
            Conversation
          </div>

          <div className="messages">
            {messages.length === 0 && !loading && (
              <>
                <div className="welcome">
                  <div className="welcome-icon" aria-hidden>
                    <svg viewBox="0 0 48 48" fill="none">
                      <circle cx="24" cy="24" r="22" stroke="currentColor" strokeWidth="2" opacity="0.35" />
                      <path
                        d="M16 28h16M20 20h8M22 14h4"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  </div>
                  <h3>Start learning</h3>
                  <p>Index your PDF in the sidebar, then ask below.</p>
                  <div className="steps">
                    <span className="step">
                      <span className="step-num">1</span> Upload
                    </span>
                    <span className="step">
                      <span className="step-num">2</span> Index
                    </span>
                    <span className="step">
                      <span className="step-num">3</span> Ask
                    </span>
                  </div>
                </div>
                <p className="suggestions-title">
                  {files.length > 0 ? "Try asking (from your PDF)" : "Try asking"}
                </p>
                <div className="suggestions">
                  {suggestions.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className="suggestion-btn"
                      onClick={() => ask(s)}
                    >
                      <span className="suggestion-arrow" aria-hidden>
                        →
                      </span>
                      {s}
                    </button>
                  ))}
                </div>
              </>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`message-group message-group--${msg.role}`}
              >
                {msg.role === "user" ? (
                  <>
                    <span className="msg-label">You</span>
                    <div className="bubble user">{msg.content}</div>
                  </>
                ) : (
                  <>
                    <span className="msg-label">Assistant</span>
                    <div
                      className="bubble assistant"
                      dangerouslySetInnerHTML={{
                        __html: renderMarkdown(msg.content),
                      }}
                    />
                    {msg.citations && msg.citations.length > 0 && (
                      <details className="sources">
                        <summary>Sources from your PDF</summary>
                        <ul>
                          {msg.citations.map((c, j) => (
                            <li key={j}>
                              {c.source} — section {c.chunk_index + 1}
                            </li>
                          ))}
                        </ul>
                      </details>
                    )}
                  </>
                )}
              </div>
            ))}

            {loading && (
              <div className="message-group message-group--assistant">
                <span className="msg-label">Assistant</span>
                <div className="typing" aria-label="Thinking">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <form
            className="chat-input-row"
            onSubmit={(e) => {
              e.preventDefault();
              ask(input);
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything from your study material…"
              disabled={loading}
            />
            <button
              type="submit"
              className="send-btn"
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden>
                <path
                  d="M3.4 20.6l17.2-8.6L3.4 3.4l2.9 6.8 6.8 2.1-6.8 2.1-2.9 6.8z"
                  fill="currentColor"
                />
              </svg>
            </button>
          </form>
        </section>
      </main>

      {toast && (
        <div className={`toast ${toast.type}`} role="status">
          <span className="toast-icon" aria-hidden>
            {toast.type === "success" ? "✓" : "!"}
          </span>
          {toast.text}
        </div>
      )}

      <ConfirmModal
        open={confirm !== null}
        title={confirm?.title ?? ""}
        message={confirm?.message ?? ""}
        confirmLabel={confirm?.confirmLabel}
        danger={confirm?.danger}
        onConfirm={() => confirm?.onConfirm()}
        onCancel={() => setConfirm(null)}
      />

      <ConfirmModal
        open={successAlert !== null}
        title={successAlert?.title ?? ""}
        message={successAlert?.message ?? ""}
        confirmLabel="Done"
        success
        onConfirm={() => setSuccessAlert(null)}
        onCancel={() => setSuccessAlert(null)}
      />
    </div>
  );
}
