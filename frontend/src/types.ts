export type Profile =
  | "mate-info"
  | "stiintele-naturii"
  | "tehnologic"
  | "pedagogic";

// Canonical profile list (hardest → easiest) with display labels. Single source
// of truth for the selector UIs.
export const PROFILES: { code: Profile; label: string }[] = [
  { code: "mate-info", label: "Mate-Info" },
  { code: "stiintele-naturii", label: "Științele Naturii" },
  { code: "tehnologic", label: "Tehnologic" },
  { code: "pedagogic", label: "Pedagogic" },
];

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

/** One numbered item of Subiectul I (independent, 5p). */
export interface SimItem {
  id?: string;
  number: number;
  points: number;
  topic: string;
  difficulty: number;
  question_latex: string;
  answer_latex: string;
  hint_latex?: string;
  steps_latex?: string[];
}

/** One sub-point (a/b/c…) of a Subiect II/III problem. */
export interface SimSubItem {
  label: string;
  points: number;
  difficulty: number;
  question_latex: string;
  answer_latex: string;
  hint_latex?: string;
  steps_latex?: string[];
}

/** A multi-part problem with a shared statement and linked sub-points. */
export interface SimProblem {
  number: number;
  topic_primary: string;
  statement_latex: string;
  sub_items: SimSubItem[];
}

export interface SimulateResponse {
  profile: Profile;
  seed: string;
  total_points: number;
  officiu_points: number;
  subiect_I: { points: number; items: SimItem[] };
  subiect_II: { points: number; problems: SimProblem[] };
  subiect_III: { points: number; problems: SimProblem[] };
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
  is_staff: boolean;
}

export interface AdminUser {
  id: number;
  email: string;
  username: string;
  profile: Profile;
  date_joined: string;
  last_login: string | null;
  is_active: boolean;
  is_staff: boolean;
}

export interface AdminBlogPost {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  body_md: string;
  is_published: boolean;
  author: string | null;
  created_at: string;
  published_at: string | null;
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
