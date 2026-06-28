export type Profile = "M1" | "M2" | "M3";

export interface Exercise {
  id: string;
  index: number;
  topic: string;
  difficulty: number;
  /** Where this difficulty sits on a real BAC paper, e.g. "Subiectul II". */
  bac_context?: string;
  question_latex: string;
  hint_latex: string;
  answer_latex: string;
  /** Worked solution, one step per entry (may contain $…$ math). */
  steps_latex?: string[];
}

export interface GenerateResponse {
  seed: string;
  items: Exercise[];
}

export interface SimulateResponse {
  seed: string;
  subiectul_I: Exercise[];
  subiectul_II: Exercise[];
  subiectul_III: Exercise[];
}

export interface TopicEntry {
  code: string;
  label: string;
}

export interface TopicsResponse {
  labels: Record<string, string>;
  by_profile: Record<Profile, TopicEntry[]>;
}

export interface User {
  id: number;
  email: string;
  username: string;
  profile: Profile;
  date_joined: string;
}

export interface BlogPostSummary {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  published_at: string | null;
}

export interface BlogPost extends BlogPostSummary {
  body_md: string;
}
