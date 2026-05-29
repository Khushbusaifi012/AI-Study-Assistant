import type { Citation, Message, StudyContext } from "./types";

const API = "/api";

export async function fetchFiles(): Promise<string[]> {
  const res = await fetch(`${API}/files`);
  if (!res.ok) throw new Error("Failed to load files");
  const data = await res.json();
  return data.files ?? [];
}

export async function removeIndexedFile(filename: string): Promise<{ message: string }> {
  const encoded = encodeURIComponent(filename);
  const res = await fetch(`${API}/files/${encoded}`, { method: "DELETE" });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(
      typeof data.detail === "string" ? data.detail : "Remove failed"
    );
  }
  return data;
}

export async function indexFile(file: File): Promise<{ message: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/index`, { method: "POST", body: form });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? data.message ?? "Index failed");
  return data;
}

export async function sendChat(
  question: string,
  ctx: StudyContext,
  messages: Message[]
): Promise<{ answer: string; citations: Citation[]; has_context: boolean }> {
  const res = await fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      subject: ctx.subject,
      topic: ctx.topic,
      level: ctx.level,
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
    }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "Chat failed";
    throw new Error(detail);
  }
  return data;
}

export async function fetchConfig(): Promise<{ local_embeddings: boolean }> {
  const res = await fetch(`${API}/config`);
  if (!res.ok) return { local_embeddings: true };
  return res.json();
}

export async function fetchSuggestions(ctx: StudyContext): Promise<string[]> {
  const params = new URLSearchParams({
    subject: ctx.subject,
    topic: ctx.topic,
  });
  const res = await fetch(`${API}/suggestions?${params}`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.suggestions ?? [];
}
