import { useCallback, useEffect, useRef, useState } from "react";
import { fetchFiles, indexFile, removeIndexedFile, sendChat } from "./api";
import ConfirmModal from "./ConfirmModal";
import { renderMarkdown } from "./markdown";
import type { Message, StudyContext } from "./types";
import { LEVELS, SUGGESTIONS } from "./types";

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
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [toast, setToast] = useState<{ type: "error" | "success"; text: string } | null>(null);
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);
  const [successAlert, setSuccessAlert] = useState<AlertState | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
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

  useEffect(() => {
    refreshFiles();
  }, [refreshFiles]);

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
          <h1>Study Assistant</h1>
          <p>Upload · Index · Ask</p>
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
        <header className="hero">
          <span className="hero-tag">React · RAG</span>
          <h2>Study Assistant</h2>
          <p>Context-aware doubt solver grounded in your notes and PDFs.</p>
        </header>

        <div className="stats">
          <div className="stat">
            <div className="stat-label">Subject</div>
            <div className="stat-value">{ctx.subject || "—"}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Topic</div>
            <div className="stat-value">{ctx.topic || "—"}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Materials</div>
            <div className="stat-value">
              {files.length ? `${files.length} ready` : "None"}
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
                <div className="suggestions">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className="suggestion-btn"
                      onClick={() => ask(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className="message-group">
                {msg.role === "user" ? (
                  <div className="bubble user">{msg.content}</div>
                ) : (
                  <>
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
              <div className="typing">
                <span />
                <span />
                <span />
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
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      </main>

      {toast && <div className={`toast ${toast.type}`}>{toast.text}</div>}

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
