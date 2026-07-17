import { Link, useSearchParams } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";

import { PROFILES, SUBJECTS } from "../types";
import type { ArchiveIndex, ArchiveProblem, ArchiveSet, Profile } from "../types";

const ARCHIVE_YEARS = "2013–2026";

/**
 * The floor for how small the exam's own typesetting may be drawn, in CSS px per
 * point of artwork. A problem is ~500pt wide, so fitting one to a 390px phone would
 * render its 11pt maths at about 8px — present, but not readable. Below this the card
 * scrolls sideways instead, the same bargain `.katex-display` already makes with
 * wide equations elsewhere on the site.
 */
const MIN_LEGIBLE_PX_PER_PT = 1.15;

const setKey = (p: Profile, subject: number, exercise: number) =>
  `${p}-${subject}-${exercise}`;

/** Sessions sort within a year: the real paper first, then the rehearsals. */
const sessionRank = (s: string) =>
  /principal/i.test(s) ? 0 : /varianta/i.test(s) ? 1 : /model/i.test(s) ? 2 : 3;

/** `Varianta 10` follows `Varianta 2`, which sorting the strings would not do. */
const sessionNumber = (s: string) => Number(s.match(/\d+/)?.[0] ?? 0);

const bySession = (a: ArchiveProblem, b: ArchiveProblem) =>
  b.year - a.year ||
  sessionRank(a.session) - sessionRank(b.session) ||
  sessionNumber(a.session) - sessionNumber(b.session) ||
  a.session.localeCompare(b.session, "ro");

function Spinner() {
  return (
    <div className="py-16 text-center text-sm text-ink-muted">Se încarcă arhiva…</div>
  );
}

/** The archive is there but didn't arrive. Say what happened and offer the way out. */
function Failed({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="border border-danger-edge bg-danger-tint rounded-2xl px-6 py-10 text-center">
      <p className="font-semibold text-danger-ink">Arhiva nu s-a încărcat.</p>
      <p className="mt-1 text-sm text-ink-muted">
        Verifică legătura la internet și încearcă din nou.
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-5 px-4 py-2 rounded-lg border border-edge bg-paper text-sm font-semibold text-ink hover:bg-sunken transition-colors"
      >
        Reîncarcă
      </button>
    </div>
  );
}

/** Nothing digitised for this specialization yet — say what is, and where to go. */
function Empty({ label }: { label: string }) {
  return (
    <div className="border border-edge border-dashed rounded-2xl bg-paper px-6 py-14 text-center">
      <p className="text-ink-strong font-semibold">
        Subiectele de {label} nu sunt încă în arhivă.
      </p>
      <p className="mt-2 text-sm text-ink-muted max-w-md mx-auto">
        Deocamdată am digitizat Mate-Info și Tehnologic — {ARCHIVE_YEARS}, fiecare
        problemă la poziția ei din examen. Urmează și restul.
      </p>
      <Link
        to="/practice"
        className="inline-block mt-6 px-4 py-2 rounded-lg bg-oxblood text-paper text-sm font-semibold hover:bg-oxblood-deep transition-colors"
      >
        Antrenează-te pe {label}
      </Link>
    </div>
  );
}

export function Arhiva() {
  const [params, setParams] = useSearchParams();

  // The URL is shareable, so treat it as untrusted: a hand-edited `?ex=99` should
  // land on a real slot rather than a failed fetch.
  const profile = PROFILES.some((p) => p.code === params.get("profil"))
    ? (params.get("profil") as Profile)
    : "mate-info";
  const subject = SUBJECTS.some((s) => s.num === Number(params.get("subiect")))
    ? Number(params.get("subiect"))
    : 1;
  const maxExercise = SUBJECTS.find((s) => s.num === subject)!.exercises;
  const exercise = Math.min(
    Math.max(Math.trunc(Number(params.get("ex"))) || 1, 1),
    maxExercise,
  );
  const year = params.get("an") ?? "";

  const [index, setIndex] = useState<ArchiveIndex | null>(null);
  const [set, setSet] = useState<ArchiveSet | null>(null);
  const [loading, setLoading] = useState(true);
  // "Couldn't load" and "not in the archive yet" are different things to be told.
  const [failed, setFailed] = useState(false);

  const patch = (next: Record<string, string>) => {
    const p = new URLSearchParams(params);
    Object.entries(next).forEach(([k, v]) => (v ? p.set(k, v) : p.delete(k)));
    setParams(p, { replace: true });
  };

  useEffect(() => {
    fetch("/arhiva/index.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setIndex)
      .catch(() => setFailed(true));
  }, []);

  const key = setKey(profile, subject, exercise);
  const available = !!index?.sets[key];

  useEffect(() => {
    if (!index || !available) {
      setSet(null);
      setLoading(false);
      return;
    }
    let live = true;
    setLoading(true);
    setFailed(false);
    fetch(`/arhiva/${key}.json`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data: ArchiveSet) => {
        if (!live) return;
        setSet(data);
        setLoading(false);
      })
      .catch(() => {
        if (!live) return;
        setSet(null);
        setFailed(true);
        setLoading(false);
      });
    return () => {
      live = false;
    };
  }, [key, index, available]);

  const subjectMeta = SUBJECTS.find((s) => s.num === subject) ?? SUBJECTS[0];

  // Newest first: a student revising wants this year's paper at the top.
  const problems = useMemo(() => {
    const all = (set?.problems ?? []).slice().sort(bySession);
    return year ? all.filter((p) => String(p.year) === year) : all;
  }, [set, year]);

  const years = useMemo(
    () => [...new Set((set?.problems ?? []).map((p) => p.year))].sort((a, b) => b - a),
    [set],
  );

  const pick = (patchArgs: Record<string, string>) => {
    // A year that doesn't exist in the next set would filter the list to nothing.
    patch({ ...patchArgs, an: "" });
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 md:py-14">
      <header className="mb-8">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong">
          Arhiva subiectelor de BAC
        </h1>
        <p className="mt-2 text-ink-muted max-w-2xl">
          Fiecare problemă dată la Bacalaureat între {ARCHIVE_YEARS}, așezată la poziția
          pe care a ocupat-o în examen. Alege specializarea și poziția, apoi citește-le
          la rând.
        </p>
      </header>

      <Picker
        profile={profile}
        subject={subject}
        exercise={exercise}
        onProfile={(p) => pick({ profil: p })}
        onSubject={(n) => {
          const max = SUBJECTS.find((s) => s.num === n)!.exercises;
          pick({ subiect: String(n), ex: String(Math.min(exercise, max)) });
        }}
        onExercise={(n) => pick({ ex: String(n) })}
      />

      <div className="mt-6 mb-8 flex flex-wrap items-center justify-between gap-3 border-t border-edge pt-4">
        <p className="text-sm text-ink-muted">
          {available ? (
            <>
              <span className="font-semibold text-ink-strong">
                {problems.length}
              </span>{" "}
              {problems.length === 1 ? "problemă" : "probleme"} · Subiectul{" "}
              {subjectMeta.num === 1 ? "I" : subjectMeta.label}, exercițiul {exercise}
            </>
          ) : (
            "—"
          )}
        </p>

        {years.length > 0 && (
          <label className="flex items-center gap-2 text-sm">
            <span className="text-ink-muted">An</span>
            <select
              value={year}
              onChange={(e) => patch({ an: e.target.value })}
              className="rounded-lg border border-edge bg-paper px-3 py-1.5 text-sm font-medium text-ink hover:border-oxblood/40 transition-colors"
            >
              <option value="">Toți anii</option>
              {years.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      {failed ? (
        <Failed onRetry={() => window.location.reload()} />
      ) : !index || loading ? (
        <Spinner />
      ) : !available ? (
        <Empty label={PROFILES.find((p) => p.code === profile)?.label ?? ""} />
      ) : (
        <Timeline problems={problems} width={set?.width ?? 500} />
      )}
    </div>
  );
}

function Picker({
  profile,
  subject,
  exercise,
  onProfile,
  onSubject,
  onExercise,
}: {
  profile: Profile;
  subject: number;
  exercise: number;
  onProfile: (p: Profile) => void;
  onSubject: (n: number) => void;
  onExercise: (n: number) => void;
}) {
  const meta = SUBJECTS.find((s) => s.num === subject) ?? SUBJECTS[0];
  const stops = Array.from({ length: meta.exercises }, (_, i) => i + 1);

  return (
    <div className="bg-paper border border-edge rounded-2xl p-5 md:p-7 shadow-sm">
      <fieldset>
        <legend className="text-xs font-semibold uppercase tracking-wider text-ink-muted mb-2.5">
          Specializare
        </legend>
        <div className="flex flex-wrap gap-2">
          {PROFILES.map((p) => {
            const active = profile === p.code;
            return (
              <button
                key={p.code}
                type="button"
                onClick={() => onProfile(p.code)}
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
      </fieldset>

      <div className="mt-6 grid gap-6 md:grid-cols-[auto_1fr] md:gap-8 md:items-start">
        <fieldset>
          <legend className="text-xs font-semibold uppercase tracking-wider text-ink-muted mb-2.5">
            Subiectul
          </legend>
          <div className="inline-flex rounded-lg border border-edge overflow-hidden">
            {SUBJECTS.map((s, i) => {
              const active = subject === s.num;
              return (
                <button
                  key={s.num}
                  type="button"
                  onClick={() => onSubject(s.num)}
                  aria-pressed={active}
                  className={`px-3.5 py-2 text-sm font-semibold transition-colors ${
                    i > 0 ? "border-l border-edge" : ""
                  } ${
                    active
                      ? "bg-oxblood text-paper"
                      : "bg-paper text-ink hover:bg-sunken"
                  }`}
                >
                  {s.num === 1 ? "I" : s.num === 2 ? "al II-lea" : "al III-lea"}
                </button>
              );
            })}
          </div>
        </fieldset>

        <fieldset className="min-w-0">
          <legend className="text-xs font-semibold uppercase tracking-wider text-ink-muted mb-2.5">
            Exercițiul
          </legend>
          <Slider stops={stops} value={exercise} onChange={onExercise} />
        </fieldset>
      </div>
    </div>
  );
}

/** A real range input, painted to show its stops. Keyboard and touch come free. */
function Slider({
  stops,
  value,
  onChange,
}: {
  stops: number[];
  value: number;
  onChange: (n: number) => void;
}) {
  const max = stops.length;
  // With one stop the thumb has nowhere to travel; pin it to the left.
  const pct = max > 1 ? ((value - 1) / (max - 1)) * 100 : 0;

  return (
    // Length tracks the number of exercises, so the control keeps the proportions of
    // the paper itself: Subiectul I is a long run of six, the others a short hop of
    // two. Stretching both to the same width would make two stops read as a fault.
    <div
      className="pt-1 pr-2.5"
      style={{ width: `min(100%, ${(max - 1) * 3.5 + 2}rem)` }}
    >
      <div className="relative h-6">
        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-[3px] rounded-full bg-sunken border border-edge" />
        <div
          className="absolute left-0 top-1/2 -translate-y-1/2 h-[3px] rounded-full bg-oxblood/70"
          style={{ width: `${pct}%` }}
        />
        {stops.map((s, i) => {
          const at = max > 1 ? (i / (max - 1)) * 100 : 0;
          return (
            <span
              key={s}
              aria-hidden
              className={`absolute top-1/2 w-2 h-2 -translate-x-1/2 -translate-y-1/2 rounded-full transition-colors ${
                s <= value ? "bg-oxblood" : "bg-edge"
              }`}
              style={{ left: `${at}%` }}
            />
          );
        })}
        <span
          aria-hidden
          className="absolute top-1/2 w-5 h-5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-oxblood border-2 border-paper shadow ring-1 ring-oxblood/30 transition-[left] duration-150 ease-out-quart"
          style={{ left: `${pct}%` }}
        />
        <input
          type="range"
          min={1}
          max={max}
          step={1}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          aria-label="Exercițiul"
          aria-valuetext={`Exercițiul ${value}`}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
      </div>
      <div className="relative mt-1.5 h-4 select-none">
        {stops.map((s, i) => {
          const at = max > 1 ? (i / (max - 1)) * 100 : 0;
          return (
            <button
              key={s}
              type="button"
              tabIndex={-1}
              onClick={() => onChange(s)}
              style={{ left: `${at}%` }}
              className={`absolute -translate-x-1/2 text-xs tabular-nums transition-colors ${
                s === value
                  ? "font-bold text-oxblood"
                  : "text-ink-faint hover:text-ink-muted"
              }`}
            >
              {s}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * The signature: a spine of years down the left, problems hanging off it. The archive
 * is one slot seen across fourteen years, and reading it that way is the whole point —
 * the same question, asked again every June.
 */
function Timeline({ problems, width }: { problems: ArchiveProblem[]; width: number }) {
  if (!problems.length) {
    return (
      <p className="py-16 text-center text-sm text-ink-muted">
        Niciun subiect pentru filtrele alese.
      </p>
    );
  }

  let last: number | null = null;
  return (
    <div className="relative md:pl-24">
      {/* The spine itself. Decorative on mobile, where years sit inline instead. */}
      <div
        aria-hidden
        className="hidden md:block absolute left-[4.5rem] top-2 bottom-2 w-px bg-edge"
      />
      <ol className="space-y-5">
        {problems.map((p) => {
          const isNew = p.year !== last;
          last = p.year;
          return (
            <li key={p.id} className="relative">
              {isNew && (
                <div className="md:absolute md:-left-24 md:top-4 md:w-16 md:text-right">
                  <span className="md:sticky md:top-24 inline-block text-sm font-bold tabular-nums text-ink-strong">
                    {p.year}
                  </span>
                </div>
              )}
              {isNew && (
                <span
                  aria-hidden
                  className="hidden md:block absolute -left-[1.65rem] top-[1.4rem] w-[7px] h-[7px] rounded-full bg-oxblood ring-4 ring-sunken"
                />
              )}
              <Card problem={p} width={width} />
            </li>
          );
        })}
      </ol>
    </div>
  );
}

function Card({ problem, width }: { problem: ArchiveProblem; width: number }) {
  const [failed, setFailed] = useState(false);

  return (
    <figure className="bg-paper border border-edge rounded-xl overflow-hidden">
      <figcaption className="px-4 pt-3 text-xs text-ink-muted">
        {/* The spine carries the year on desktop; without it, every card says so. */}
        <span className="md:hidden font-bold tabular-nums text-ink-strong">
          {problem.year} ·{" "}
        </span>
        {problem.session}
      </figcaption>
      <div className="px-4 pb-4 pt-2 overflow-x-auto">
        {failed ? (
          <p className="py-6 text-center text-sm text-ink-muted">
            Problema nu a putut fi încărcată.
          </p>
        ) : (
          <img
            src={problem.src}
            alt={`Problemă de BAC, ${problem.session} ${problem.year}`}
            loading="lazy"
            decoding="async"
            onError={() => setFailed(true)}
            style={{
              // Fill the column where there's room; below that hold a legible size
              // and let the card scroll rather than shrink the maths away.
              width: `max(100%, ${Math.round(width * MIN_LEGIBLE_PX_PER_PT)}px)`,
              // The artwork's own ratio holds the space, so the list never jumps as
              // images stream in.
              aspectRatio: String(problem.ratio),
            }}
            className="h-auto block max-w-none"
          />
        )}
      </div>
    </figure>
  );
}
