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

export const SUGGESTIONS = [
  "What are the types of functions?",
  "What are the types of arguments?",
  "What is a lambda function?",
  "Difference between local and global variables?",
];
