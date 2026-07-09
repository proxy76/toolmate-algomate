import { Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiErrorMessage } from "../api";
import { useAuth } from "../auth";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
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
        <h1 className="text-3xl font-extrabold tracking-tight text-ink-strong">Autentificare</h1>
        <p className="mt-2 text-ink-muted">Intră în cont pentru a-ți regăsi sesiunile salvate.</p>
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
        <div>
          <div className="text-sm font-semibold text-ink mb-1.5">Email sau nume utilizator</div>
          <input
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="username"
            className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
          />
        </div>
        <div>
          <div className="text-sm font-semibold text-ink mb-1.5">Parolă</div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex w-full items-center justify-center gap-2 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && <Loader2 size={18} className="animate-spin" />}
          {loading ? "Se conectează…" : "Conectează-mă"}
        </button>
      </form>

      <p className="text-sm text-ink-muted text-center mt-5">
        Nu ai cont?{" "}
        <Link to="/register" className="text-oxblood font-semibold hover:underline">
          Creează unul
        </Link>
      </p>
    </div>
  );
}
