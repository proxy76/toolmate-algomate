import { Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api, apiErrorMessage } from "../api";
import { useAuth } from "../auth";
import type { Profile } from "../types";
import { PROFILES } from "../types";

export function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    profile: "mate-info" as Profile,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.register(form);
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto px-6 py-14 md:py-20">
      <header className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-ink-strong">Înregistrare</h1>
        <p className="mt-2 text-ink-muted">
          Creează un cont gratuit pentru a salva și relua seturile de exerciții.
        </p>
      </header>

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
        <Field label="Nume utilizator">
          <input
            type="text"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
            minLength={3}
            maxLength={50}
            autoComplete="username"
            className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
          />
        </Field>
        <Field label="Email">
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
            autoComplete="email"
            className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
          />
        </Field>
        <Field label="Parolă (minim 10 caractere)">
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
            minLength={10}
            autoComplete="new-password"
            className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
          />
        </Field>
        <Field label="Profil">
          <select
            value={form.profile}
            onChange={(e) => setForm({ ...form, profile: e.target.value as Profile })}
            className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge focus:border-oxblood transition-colors"
          >
            {PROFILES.map((p) => (
              <option key={p.code} value={p.code}>
                {p.label}
              </option>
            ))}
          </select>
        </Field>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex w-full items-center justify-center gap-2 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && <Loader2 size={18} className="animate-spin" />}
          {loading ? "Se creează contul…" : "Creează cont"}
        </button>
      </form>

      <p className="text-sm text-ink-muted text-center mt-5">
        Ai deja cont?{" "}
        <Link to="/login" className="text-oxblood font-semibold hover:underline">
          Conectează-te
        </Link>
      </p>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-sm font-semibold text-ink mb-1.5">{label}</div>
      {children}
    </div>
  );
}
