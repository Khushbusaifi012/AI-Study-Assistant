export type Role = "user" | "assistant";

export interface Message {
  id: string;
  role: Role;
  content: string;
  citations?: Citation[];
}

export interface Citation {
  source: string;
  chunk_index: number;
  distance?: number | null;
}

export interface StudyContext {
  subject: string;
  topic: string;
  level: string;
}

export const LEVELS = [
  "Middle school",
  "High school",
  "Undergraduate",
  "Competitive exam",
] as const;

/** Shown only before any PDF is indexed */
export const DEFAULT_SUGGESTIONS = [
  "What are the main topics in my notes?",
  "Summarize the key points from my material.",
  "What is the most important concept here?",
  "Give me a practice question from my notes.",
];
