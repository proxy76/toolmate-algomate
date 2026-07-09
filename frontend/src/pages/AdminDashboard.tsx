import { FileText, Loader2, PlusCircle, ShieldCheck, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, apiErrorMessage } from "../api";
import { useAuth } from "../auth";
import type { AdminBlogPost, AdminUser } from "../types";

const fmt = (iso: string | null) =>
  iso ? new Date(iso).toLocaleString("ro-RO", { dateStyle: "medium", timeStyle: "short" }) : "—";

export function AdminDashboard() {
  const { user } = useAuth();

  if (!user?.is_staff) {
    return (
      <div className="max-w-md mx-auto px-6 py-20 text-center">
        <ShieldCheck size={32} className="mx-auto text-ink-faint" />
        <h1 className="mt-4 text-2xl font-extrabold tracking-tight text-ink-strong">
          Acces restricționat
        </h1>
        <p className="mt-2 text-ink-muted">Această pagină este disponibilă doar administratorilor.</p>
        <Link to="/" className="mt-6 inline-block text-oxblood font-semibold hover:underline">
          Înapoi la pagina principală
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 md:py-14">
      <header className="mb-8 flex items-center gap-3">
        <span className="grid place-items-center w-11 h-11 rounded-xl bg-oxblood/10 text-oxblood">
          <ShieldCheck size={24} strokeWidth={2.25} />
        </span>
        <div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong">
            Panou de administrare
          </h1>
          <p className="text-ink-muted text-sm mt-0.5">
            Conectat ca <span className="font-semibold text-ink">{user.username}</span>
          </p>
        </div>
      </header>

      <div className="grid lg:grid-cols-2 gap-6 items-start">
        <NewPostCard />
        <UsersCard />
      </div>
    </div>
  );
}

// --- create a blog post ------------------------------------------------------
function NewPostCard() {
  const [title, setTitle] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [body, setBody] = useState("");
  const [published, setPublished] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [posts, setPosts] = useState<AdminBlogPost[]>([]);

  async function loadPosts() {
    try {
      setPosts(await api.adminListPosts());
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }
  useEffect(() => {
    loadPosts();
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setOk(null);
    try {
      const post = await api.adminCreatePost({ title, excerpt, body_md: body, is_published: published });
      setOk(`Articolul „${post.title}” a fost ${post.is_published ? "publicat" : "salvat ca ciornă"}.`);
      setTitle("");
      setExcerpt("");
      setBody("");
      setPublished(true);
      loadPosts();
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  const field =
    "w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors";

  return (
    <section className="bg-paper border border-edge rounded-2xl shadow-sm">
      <div className="flex items-center gap-2 px-5 md:px-6 pt-5 pb-3 border-b border-edge">
        <FileText size={18} className="text-oxblood" />
        <h2 className="font-bold text-ink-strong">Articol nou</h2>
      </div>

      <form onSubmit={onSubmit} className="p-5 md:p-6 space-y-4">
        {error && (
          <div role="alert" className="px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm">
            {error}
          </div>
        )}
        {ok && (
          <div className="px-4 py-3 rounded-xl bg-oxblood/10 border border-oxblood/20 text-oxblood-deep text-sm">
            {ok}
          </div>
        )}

        <div>
          <label className="block text-sm font-semibold text-ink mb-1.5">Titlu</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} required maxLength={200} className={field} />
        </div>
        <div>
          <label className="block text-sm font-semibold text-ink mb-1.5">
            Rezumat <span className="font-normal text-ink-faint">(opțional)</span>
          </label>
          <input value={excerpt} onChange={(e) => setExcerpt(e.target.value)} maxLength={400} className={field} />
        </div>
        <div>
          <label className="block text-sm font-semibold text-ink mb-1.5">
            Conținut <span className="font-normal text-ink-faint">(Markdown)</span>
          </label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            required
            rows={8}
            className={`${field} font-mono text-sm leading-relaxed resize-y`}
          />
        </div>

        <label className="flex items-center gap-2.5 text-sm text-ink cursor-pointer select-none">
          <input
            type="checkbox"
            checked={published}
            onChange={(e) => setPublished(e.target.checked)}
            className="w-4 h-4 accent-oxblood"
          />
          Publică imediat <span className="text-ink-faint">(altfel se salvează ca ciornă)</span>
        </label>

        <button
          type="submit"
          disabled={saving}
          className="inline-flex w-full items-center justify-center gap-2 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? <Loader2 size={18} className="animate-spin" /> : <PlusCircle size={18} />}
          {saving ? "Se salvează…" : "Publică articolul"}
        </button>
      </form>

      {posts.length > 0 && (
        <div className="border-t border-edge px-5 md:px-6 py-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-faint mb-2">
            Articole existente ({posts.length})
          </p>
          <ul className="divide-y divide-edge">
            {posts.map((p) => (
              <li key={p.id} className="py-2 flex items-center justify-between gap-3 text-sm">
                <span className="truncate text-ink">{p.title}</span>
                <span
                  className={`shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full ${
                    p.is_published
                      ? "text-oxblood-deep bg-oxblood/10"
                      : "text-ink-muted bg-sunken border border-edge"
                  }`}
                >
                  {p.is_published ? "publicat" : "ciornă"}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

// --- registered accounts -----------------------------------------------------
function UsersCard() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .adminListUsers()
      .then(setUsers)
      .catch((err) => setError(apiErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="bg-paper border border-edge rounded-2xl shadow-sm">
      <div className="flex items-center justify-between gap-2 px-5 md:px-6 pt-5 pb-3 border-b border-edge">
        <div className="flex items-center gap-2">
          <Users size={18} className="text-oxblood" />
          <h2 className="font-bold text-ink-strong">Conturi înregistrate</h2>
        </div>
        {!loading && (
          <span className="text-xs font-semibold text-ink-muted bg-sunken border border-edge px-2.5 py-0.5 rounded-full">
            {users.length}
          </span>
        )}
      </div>

      <div className="p-2 md:p-3">
        {error && (
          <div role="alert" className="m-3 px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm">
            {error}
          </div>
        )}
        {loading ? (
          <div className="p-8 text-center text-ink-muted">
            <Loader2 size={20} className="animate-spin mx-auto" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-ink-faint">
                  <th className="px-3 py-2 font-semibold">Utilizator</th>
                  <th className="px-3 py-2 font-semibold">Profil</th>
                  <th className="px-3 py-2 font-semibold">Înregistrat</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-edge">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-sunken/50 transition-colors">
                    <td className="px-3 py-2.5">
                      <div className="font-semibold text-ink-strong flex items-center gap-1.5">
                        {u.username}
                        {u.is_staff && (
                          <ShieldCheck size={13} className="text-oxblood" aria-label="Administrator" />
                        )}
                      </div>
                      <div className="text-ink-muted text-xs">{u.email}</div>
                    </td>
                    <td className="px-3 py-2.5 text-ink">{u.profile}</td>
                    <td className="px-3 py-2.5 text-ink-muted whitespace-nowrap">{fmt(u.date_joined)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
