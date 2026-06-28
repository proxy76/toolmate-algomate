import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api, apiErrorMessage } from "../api";
import type { BlogPost } from "../types";

export function BlogPostPage() {
  const { slug = "" } = useParams<{ slug: string }>();
  const [post, setPost] = useState<BlogPost | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .blogPost(slug)
      .then(setPost)
      .catch((err) => setError(apiErrorMessage(err)));
  }, [slug]);

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-10 md:py-14">
        <div
          role="alert"
          className="px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm"
        >
          {error}
        </div>
        <Link
          to="/blog"
          className="inline-flex items-center gap-1.5 mt-4 text-oxblood font-semibold hover:underline"
        >
          <ArrowLeft size={16} /> Înapoi la blog
        </Link>
      </div>
    );
  }

  if (!post) {
    return <div className="max-w-3xl mx-auto px-6 py-10 md:py-14 text-ink-muted">Se încarcă…</div>;
  }

  return (
    <article className="max-w-3xl mx-auto px-6 py-10 md:py-14">
      <Link
        to="/blog"
        className="inline-flex items-center gap-1.5 text-sm text-ink-muted font-medium hover:text-oxblood transition-colors"
      >
        <ArrowLeft size={16} /> Toate articolele
      </Link>
      <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong text-balance mt-5 mb-2">
        {post.title}
      </h1>
      {post.published_at && (
        <div className="text-sm text-ink-faint mb-8">
          {new Date(post.published_at).toLocaleDateString("ro-RO")}
        </div>
      )}
      <div className="prose max-w-none whitespace-pre-wrap text-ink leading-relaxed">
        {post.body_md}
      </div>
    </article>
  );
}
