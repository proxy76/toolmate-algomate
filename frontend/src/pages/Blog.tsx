import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, apiErrorMessage } from "../api";
import type { BlogPostSummary } from "../types";

export function BlogIndex() {
  const [posts, setPosts] = useState<BlogPostSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .blogList()
      .then(setPosts)
      .catch((err) => setError(apiErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 md:py-14">
      <header className="mb-8">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong text-balance">
          Blog
        </h1>
        <p className="mt-2 text-ink-muted text-pretty">
          Sfaturi de pregătire, analize de subiecte oficiale și ghiduri pentru BAC.
        </p>
      </header>

      {loading && <div className="text-ink-muted">Se încarcă…</div>}
      {error && (
        <div
          role="alert"
          className="px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm"
        >
          {error}
        </div>
      )}
      {!loading && !error && posts.length === 0 && (
        <div className="rounded-2xl border border-dashed border-edge bg-paper/50 px-6 py-14 text-center text-ink-muted">
          Nu există încă articole publicate.
        </div>
      )}

      <ul className="space-y-4">
        {posts.map((p) => (
          <li
            key={p.id}
            className="bg-paper border border-edge rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <Link
              to={`/blog/${p.slug}`}
              className="text-xl font-bold text-ink-strong hover:text-oxblood transition-colors"
            >
              {p.title}
            </Link>
            {p.excerpt && <p className="text-ink-muted mt-2 leading-relaxed">{p.excerpt}</p>}
            {p.published_at && (
              <div className="text-xs text-ink-faint mt-3">
                {new Date(p.published_at).toLocaleDateString("ro-RO")}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
