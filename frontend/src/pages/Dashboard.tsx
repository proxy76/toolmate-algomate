import { CheckCheck, ChevronDown } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, apiErrorMessage } from "../api";
import { useAuth } from "../auth";
import { ExerciseCard } from "../components/ExerciseCard";
import { roCount } from "../ro";
import type { ArchiveIndex, Exercise } from "../types";

interface SessionRow {
  id: number;
  profile: string;
  topics: string[];
  difficulty: number;
  seed: string;
  created_at: string;
  items: Exercise[];
}

const DIFFICULTY_LABEL: Record<number, string> = { 1: "Ușor", 2: "Mediu", 3: "Dificil" };

export function Dashboard() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<SessionRow[]>([]);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [openId, setOpenId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [archiveDone, setArchiveDone] = useState<number | null>(null);
  const [archiveTotal, setArchiveTotal] = useState<number | null>(null);

  useEffect(() => {
    api
      .listSessions()
      .then((rows: SessionRow[]) => setSessions(rows))
      .catch((err) => setError(apiErrorMessage(err)));
    api
      .topics()
      .then((t) => setLabels(t.labels))
      .catch(() => {});
  }, []);

  useEffect(() => {
    api
      .archiveProgress()
      .then((p) => setArchiveDone(p.count))
      .catch(() => {});
    // The archive's own manifest knows how many problems there are; the API doesn't,
    // and shouldn't have to.
    fetch("/arhiva/index.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((idx: ArchiveIndex) => setArchiveTotal(idx.total))
      .catch(() => {});
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 md:py-14">
      <header className="mb-8">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong text-balance">
          Seturile mele
        </h1>
        <p className="mt-2 text-ink-muted">
          Salut, {user?.username || user?.email}! Deschide un set salvat ca să-i revezi exercițiile.
        </p>
      </header>

      <ArchiveProgressCard done={archiveDone} total={archiveTotal} />

      {error && (
        <div
          role="alert"
          className="mb-5 px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm"
        >
          {error}
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-edge bg-paper/50 px-6 py-14 text-center">
          <p className="text-ink font-semibold">Nu ai încă seturi salvate</p>
          <p className="mt-1 text-sm text-ink-muted max-w-md mx-auto">
            Generează un set de exerciții și salvează-l pentru a-l relua oricând.
          </p>
          <Link
            to="/practice"
            className="mt-6 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99]"
          >
            Generează un set
          </Link>
        </div>
      ) : (
        <ul className="space-y-3">
          {sessions.map((s) => {
            const open = openId === s.id;
            const topicNames = s.topics.map((c) => labels[c] ?? c).join(", ");
            return (
              <li
                key={s.id}
                className="bg-paper border border-edge rounded-2xl shadow-sm overflow-hidden"
              >
                <button
                  type="button"
                  onClick={() => setOpenId(open ? null : s.id)}
                  aria-expanded={open}
                  className="w-full flex items-center justify-between gap-3 p-5 text-left hover:bg-sunken transition-colors"
                >
                  <div className="min-w-0">
                    <div className="font-bold text-ink-strong">
                      {s.profile} ·{" "}
                      {DIFFICULTY_LABEL[s.difficulty] ?? `dificultate ${s.difficulty}`} ·{" "}
                      {s.items.length} exerciții
                    </div>
                    {topicNames && (
                      <div className="text-sm text-ink-muted mt-1 truncate">{topicNames}</div>
                    )}
                    <div className="text-xs text-ink-faint mt-1.5">
                      {new Date(s.created_at).toLocaleString("ro-RO")} · seed{" "}
                      <code className="bg-sunken text-ink px-1.5 py-0.5 rounded border border-edge">
                        {s.seed}
                      </code>
                    </div>
                  </div>
                  <ChevronDown
                    size={20}
                    className={`shrink-0 text-ink-muted transition-transform ${
                      open ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {open && (
                  <div className="border-t border-edge bg-sunken/40 p-5">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {s.items.map((ex) => (
                        <ExerciseCard key={ex.id} exercise={ex} topicLabel={labels[ex.topic]} />
                      ))}
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

/**
 * How far through the archive you are. Deliberately a count and not a percentage:
 * nobody is going to work all 2,350, so a bar creeping along at 1% would read as
 * failure. The number going up is the whole reward.
 */
function ArchiveProgressCard({
  done,
  total,
}: {
  done: number | null;
  total: number | null;
}) {
  // Don't flash a zero before the count lands — an empty state that turns out to be
  // wrong is worse than a beat of nothing.
  if (done === null) return null;

  return (
    <Link
      to="/arhiva"
      className="mb-6 flex items-center gap-4 rounded-2xl border border-edge bg-paper px-5 py-4 shadow-sm hover:border-oxblood/40 transition-colors"
    >
      <span
        aria-hidden
        className="grid place-items-center w-10 h-10 shrink-0 rounded-xl bg-oxblood-tint text-oxblood-deep"
      >
        <CheckCheck size={20} />
      </span>
      <div className="min-w-0">
        <div className="font-bold text-ink-strong">
          {/* With a total, the noun agrees with the total, not the tally:
              "1 din 2350 de probleme rezolvate". */}
          {total
            ? `${done} din ${roCount(total, "problemă rezolvată", "probleme rezolvate")}`
            : roCount(done, "problemă rezolvată", "probleme rezolvate")}
        </div>
        <div className="text-sm text-ink-muted mt-0.5">
          {done === 0
            ? "Deschide arhiva și bifează prima problemă pe care o rezolvi."
            : "Continuă de unde ai rămas în arhiva de BAC."}
        </div>
      </div>
    </Link>
  );
}
