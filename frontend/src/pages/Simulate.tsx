import { Loader2, Play } from "lucide-react";
import { useState } from "react";

import { api, apiErrorMessage } from "../api";
import { ExerciseCard } from "../components/ExerciseCard";
import type { Profile, SimulateResponse } from "../types";

const PROFILES: { code: Profile; label: string }[] = [
  { code: "M1", label: "M1 — Mate-Info" },
  { code: "M2", label: "M2 — Științele Naturii" },
  { code: "M3", label: "M3 — Pedagogic / Tehnologic" },
];

const DIFFICULTIES = [
  { value: 1, label: "Ușor" },
  { value: 2, label: "Mediu" },
  { value: 3, label: "Dificil" },
];

export function Simulate() {
  const [profile, setProfile] = useState<Profile>("M1");
  const [difficulty, setDifficulty] = useState(2);
  const [data, setData] = useState<SimulateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onRun(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      setData(await api.simulate({ profile, difficulty }));
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 md:py-14">
      <header className="mb-8 max-w-2xl">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong text-balance">
          Simulare BAC
        </h1>
        <p className="mt-3 text-ink-muted leading-relaxed text-pretty">
          Generează un subiect complet cu structura oficială: SUBIECTUL I (6 itemi), SUBIECTUL II
          (2 probleme), SUBIECTUL III (2 probleme).
        </p>
      </header>

      <form
        onSubmit={onRun}
        className="bg-paper border border-edge rounded-2xl p-6 md:p-8 shadow-sm mb-10"
      >
        <div className="grid md:grid-cols-2 gap-x-8 gap-y-7">
          <div>
            <div className="text-sm font-semibold text-ink mb-2">Profil</div>
            <div className="flex flex-wrap gap-2">
              {PROFILES.map((p) => {
                const active = profile === p.code;
                return (
                  <button
                    type="button"
                    key={p.code}
                    onClick={() => setProfile(p.code)}
                    aria-pressed={active}
                    className={`px-3 py-2 rounded-lg text-sm font-semibold border transition-colors ${
                      active
                        ? "bg-oxblood text-paper border-oxblood"
                        : "bg-paper text-ink border-edge hover:border-oxblood/40 hover:bg-sunken"
                    }`}
                  >
                    {p.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <div className="text-sm font-semibold text-ink mb-2">Dificultate</div>
            <div className="flex gap-2">
              {DIFFICULTIES.map((d) => {
                const active = difficulty === d.value;
                return (
                  <button
                    type="button"
                    key={d.value}
                    onClick={() => setDifficulty(d.value)}
                    aria-pressed={active}
                    className={`flex-1 px-3 py-2 rounded-lg text-sm font-semibold border transition-colors ${
                      active
                        ? "bg-ochre text-ink-strong border-ochre"
                        : "bg-paper text-ink border-edge hover:border-ochre/50 hover:bg-sunken"
                    }`}
                  >
                    {d.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {error && (
          <div
            role="alert"
            className="mt-6 px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm"
          >
            {error}
          </div>
        )}

        <div className="mt-7">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
            {loading ? "Se generează…" : "Generează subiect"}
          </button>
        </div>
      </form>

      {data && (
        <div className="space-y-12">
          <Section index="I" title="Subiectul I" items={data.subiectul_I} />
          <Section index="II" title="Subiectul II" items={data.subiectul_II} />
          <Section index="III" title="Subiectul III" items={data.subiectul_III} />
        </div>
      )}
    </div>
  );
}

function Section({
  index,
  title,
  items,
}: {
  index: string;
  title: string;
  items: SimulateResponse["subiectul_I"];
}) {
  return (
    <section>
      <div className="flex items-center gap-3 mb-5">
        <span className="grid place-items-center min-w-9 h-9 px-2 rounded-lg bg-oxblood/10 text-oxblood-deep text-sm font-bold">
          {index}
        </span>
        <h2 className="text-xl font-bold text-ink-strong">{title}</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {items.map((ex) => (
          <ExerciseCard key={ex.id} exercise={ex} />
        ))}
      </div>
    </section>
  );
}
