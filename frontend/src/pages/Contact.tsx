import { Loader2, Send } from "lucide-react";
import { useState } from "react";

import { api, apiErrorMessage } from "../api";

export function Contact() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", body: "" });
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.contact(form);
      setDone(true);
      setForm({ name: "", email: "", subject: "", body: "" });
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-14 md:py-20">
      <header className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-ink-strong">Contact</h1>
        <p className="mt-2 text-ink-muted text-pretty">
          Ai întrebări, raportezi o eroare la o problemă, sau vrei să sugerezi un capitol nou?
          Scrie-ne aici.
        </p>
      </header>

      {done && (
        <div
          role="status"
          className="mb-5 px-4 py-3 rounded-xl bg-verified-tint border border-verified-edge text-verified-ink text-sm"
        >
          Mesaj trimis. Mulțumim!
        </div>
      )}
      {error && (
        <div
          role="alert"
          className="mb-5 px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm"
        >
          {error}
        </div>
      )}

      <form
        onSubmit={onSubmit}
        className="bg-paper border border-edge rounded-2xl p-6 md:p-8 shadow-sm space-y-5"
      >
        <Input label="Nume" value={form.name} onChange={(v) => setForm({ ...form, name: v })} />
        <Input
          label="Email"
          type="email"
          value={form.email}
          onChange={(v) => setForm({ ...form, email: v })}
        />
        <Input
          label="Subiect"
          value={form.subject}
          onChange={(v) => setForm({ ...form, subject: v })}
        />
        <div>
          <div className="text-sm font-semibold text-ink mb-1.5">Mesaj</div>
          <textarea
            value={form.body}
            onChange={(e) => setForm({ ...form, body: e.target.value })}
            required
            rows={6}
            minLength={10}
            maxLength={4000}
            className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          {loading ? "Se trimite…" : "Trimite"}
        </button>
      </form>
    </div>
  );
}

function Input({
  label,
  type = "text",
  value,
  onChange,
}: {
  label: string;
  type?: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <div className="text-sm font-semibold text-ink mb-1.5">{label}</div>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
      />
    </div>
  );
}
