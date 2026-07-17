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
  generated_tests: number;
  generated_problems: number;
  downloaded_pdfs: number;
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

/* ── Arhivă ───────────────────────────────────────────────────────────────
   Past BAC problems, cut out of the exam papers and grouped by the position
   they occupied. Built by `scripts/extract_arhiva.py` into static files under
   `public/arhiva/`, so the archive is served by nginx and never touches the API.  */

/** How many exercises each subject holds — the shape of a real paper. */
export const SUBJECTS: { num: number; label: string; exercises: number }[] = [
  { num: 1, label: "SUBIECTUL I", exercises: 6 },
  { num: 2, label: "al II-lea", exercises: 2 },
  { num: 3, label: "al III-lea", exercises: 2 },
];

export interface ArchiveProblem {
  /** Slot-scoped, e.g. `mate-info-1-1/2026-model-114`. Also the key a completion
   *  is recorded under, so it must stay stable across re-extractions. */
  id: string;
  year: number;
  /** The paper this came from: `Varianta 3`, `Model`, `Simulare`, … */
  session: string;
  src: string;
  /** width/height of the artwork, so the list can hold its space before load. */
  ratio: number;
}

export interface ArchiveSet {
  specialization: Profile;
  subject: number;
  exercise: number;
  count: number;
  /** Frame width in points — one scale for the whole set. See `MIN_LEGIBLE_PX_PER_PT`. */
  width: number;
  problems: ArchiveProblem[];
}

/** Which archive problems the signed-in user has ticked off. Ids as in `ArchiveProblem`. */
export interface ArchiveProgress {
  count: number;
  done: string[];
}

export interface ArchiveIndex {
  total: number;
  sets: Record<
    string,
    {
      specialization: Profile;
      subject: number;
      exercise: number;
      count: number;
      years: number[];
    }
  >;
}
