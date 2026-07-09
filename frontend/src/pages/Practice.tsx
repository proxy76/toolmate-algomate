import { GripVertical, Loader2, Save, Sparkles } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { api, apiErrorMessage } from "../api";
import { useAuth } from "../auth";
import { ProblemCard, type SolutionView } from "../components/ProblemCard";
import { SolutionPanel } from "../components/SolutionPanel";
import type { Exercise, Profile, TopicsResponse } from "../types";

// Bare profile codes for now. Correct mapping (labels TBD): M1 = mate-info,
// M2 = tehnologic, M3 = pedagogic.
const PROFILES: { code: Profile; label: string }[] = [
  { code: "M1", label: "M1" },
  { code: "M2", label: "M2" },
  { code: "M3", label: "M3" },
];

const DIFFICULTIES = [
  { value: 1, label: "Ușor" },
  { value: 2, label: "Mediu" },
  { value: 3, label: "Dificil" },
];

// Solution-pane width is user-adjustable (drag the divider). Clamp so neither
// side collapses: the pane stays usable and the worksheet keeps room to breathe.
const PANE_MIN = 320;
const WORKSPACE_MIN = 440;
const PANE_DEFAULT = 460;
const PANE_STORAGE_KEY = "algomate:solution-pane-w";

export function Practice() {
  const { user } = useAuth();
  const [topicsData, setTopicsData] = useState<TopicsResponse | null>(null);

  const [profile, setProfile] = useState<Profile>("M1");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [difficulty, setDifficulty] = useState(2);
  const [count, setCount] = useState(10);
  const [seed, setSeed] = useState("");

  const [items, setItems] = useState<Exercise[]>([]);
  const [active, setActive] = useState<{ id: string; view: SolutionView } | null>(null);
  const [lastSeed, setLastSeed] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  const splitRef = useRef<HTMLDivElement>(null);
  const [paneWidth, setPaneWidth] = useState<number>(() => {
    const saved = Number(localStorage.getItem(PANE_STORAGE_KEY));
    return saved >= PANE_MIN ? saved : PANE_DEFAULT;
  });
  const paneWidthRef = useRef(paneWidth);

  const applyPaneWidth = useCallback((next: number) => {
    const rect = splitRef.current?.getBoundingClientRect();
    const max = rect ? Math.max(PANE_MIN, rect.width - WORKSPACE_MIN) : 720;
    const clamped = Math.min(max, Math.max(PANE_MIN, Math.round(next)));
    paneWidthRef.current = clamped;
    setPaneWidth(clamped);
  }, []);

  // Re-clamp if the window (and so the split container) gets narrower.
  useEffect(() => {
    const onResize = () => applyPaneWidth(paneWidthRef.current);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [applyPaneWidth]);

  function onResizeStart(e: React.PointerEvent) {
    e.preventDefault();
    const move = (ev: PointerEvent) => {
      const rect = splitRef.current?.getBoundingClientRect();
      if (rect) applyPaneWidth(rect.right - ev.clientX);
    };
    const stop = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", stop);
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
      localStorage.setItem(PANE_STORAGE_KEY, String(paneWidthRef.current));
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", stop);
    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";
  }

  function onResizeKey(e: React.KeyboardEvent) {
    const step = e.shiftKey ? 48 : 16;
    if (e.key === "ArrowLeft") applyPaneWidth(paneWidthRef.current + step);
    else if (e.key === "ArrowRight") applyPaneWidth(paneWidthRef.current - step);
    else return;
    e.preventDefault();
    localStorage.setItem(PANE_STORAGE_KEY, String(paneWidthRef.current));
  }

  useEffect(() => {
    api.topics().then(setTopicsData).catch(() => setError("Nu am putut încărca lista de capitole."));
  }, []);

  useEffect(() => {
    if (!topicsData) return;
    const available = topicsData.by_profile[profile]?.map((t) => t.code) ?? [];
    setSelectedTopics((prev) => {
      const filtered = prev.filter((t) => available.includes(t));
      return filtered.length ? filtered : available.slice(0, 2);
    });
  }, [profile, topicsData]);

  const availableTopics = useMemo(
    () => topicsData?.by_profile[profile] ?? [],
    [topicsData, profile],
  );

  function toggleTopic(code: string) {
    setSelectedTopics((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    );
  }

  // Clicking the open view again closes the panel; otherwise it swaps content.
  function openSolution(id: string, view: SolutionView) {
    setActive((prev) => (prev?.id === id && prev.view === view ? null : { id, view }));
  }

  const activeExercise = active ? items.find((ex) => ex.id === active.id) ?? null : null;

  async function onGenerate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSavedMsg(null);
    if (!selectedTopics.length) {
      setError("Selectează cel puțin un capitol.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.generate({
        profile,
        topics: selectedTopics,
        difficulty,
        count,
        seed: seed.trim() || undefined,
      });
      setItems(res.items);
      setActive(null);
      setLastSeed(res.seed);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function onSaveSession() {
    if (!lastSeed || !items.length) return;
    setSaving(true);
    setError(null);
    try {
      await api.saveSession({
        profile,
        topics: selectedTopics,
        difficulty,
        seed: lastSeed,
        items,
      });
      setSavedMsg("Sesiunea a fost salvată în contul tău.");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  const intro = (
    <header className="mb-8 max-w-2xl">
      <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong text-balance">
        Generator de exerciții
      </h1>
      <p className="mt-3 text-ink-muted leading-relaxed text-pretty">
        Configurează profilul, capitolele și dificultatea. Lasă seed-ul gol pentru un set nou sau
        introdu unul cunoscut pentru a regenera exact același set.
      </p>
    </header>
  );

  const formCard = (
    <form
        onSubmit={onGenerate}
        className="bg-paper border border-edge rounded-2xl p-6 md:p-8 shadow-sm mb-10"
      >
        <div className="grid md:grid-cols-2 gap-x-8 gap-y-7">
          <Field label="Profil">
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
          </Field>

          <Field label="Dificultate">
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
          </Field>

          <Field label="Capitole" full>
            {topicsData ? (
              <div className="flex flex-wrap gap-2">
                {availableTopics.map((t) => {
                  const active = selectedTopics.includes(t.code);
                  return (
                    <button
                      key={t.code}
                      type="button"
                      onClick={() => toggleTopic(t.code)}
                      aria-pressed={active}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                        active
                          ? "bg-oxblood text-paper border-oxblood"
                          : "bg-sunken text-ink-muted border-edge hover:text-ink hover:border-oxblood/40"
                      }`}
                    >
                      {t.label}
                    </button>
                  );
                })}
              </div>
            ) : (
              <span className="text-ink-faint text-sm">Se încarcă…</span>
            )}
          </Field>

          <Field label={`Număr de exerciții (${count})`}>
            <input
              type="range"
              min={1}
              max={50}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full accent-oxblood"
              aria-label="Număr de exerciții"
            />
          </Field>

          <Field label="Seed (opțional)">
            <input
              type="text"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              placeholder="ex.: 7a3b1f"
              maxLength={64}
              className="w-full px-3 py-2 rounded-lg bg-paper text-ink border border-edge placeholder:text-ink-faint focus:border-oxblood transition-colors"
            />
          </Field>
        </div>

        {error && (
          <div
            role="alert"
            className="mt-6 px-4 py-3 rounded-xl bg-danger-tint border border-danger-edge text-danger-ink text-sm"
          >
            {error}
          </div>
        )}

        <div className="mt-7 flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
            {loading ? "Se generează…" : "Generează"}
          </button>
          {lastSeed && (
            <span className="text-xs text-ink-muted">
              Seed folosit:{" "}
              <code className="bg-sunken text-ink px-2 py-1 rounded border border-edge">
                {lastSeed}
              </code>
            </span>
          )}
        </div>
      </form>
  );

  // Before any set exists, the page is a single calm column.
  if (items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-10 md:py-14">
        {intro}
        {formCard}
        <div className="rounded-2xl border border-dashed border-edge bg-paper/50 px-6 py-14 text-center">
          <p className="text-ink font-semibold">Niciun set generat încă</p>
          <p className="mt-1 text-sm text-ink-muted max-w-md mx-auto">
            Alege profilul și capitolele de mai sus, apoi apasă{" "}
            <span className="font-semibold text-ink">Generează</span> pentru a primi exerciții cu
            indicii și răspunsuri verificate.
          </p>
        </div>
      </div>
    );
  }

  // Working view: two tiled panes filling the viewport — worksheet on the
  // left, the solution as a full-height window on the right.
  return (
    <div
      ref={splitRef}
      style={{ "--pane-w": `${paneWidth}px` } as React.CSSProperties}
      className="lg:flex lg:h-[calc(100dvh-65px)] lg:overflow-hidden"
    >
      <div className="lg:flex-1 lg:min-w-0 lg:overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-10">
          {intro}
          {formCard}
          <section>
            <div className="flex items-center justify-between gap-3 mb-5 flex-wrap">
              <h2 className="text-xl font-bold text-ink-strong">
                {items.length} {items.length === 1 ? "exercițiu generat" : "exerciții generate"}
              </h2>
              {user && (
                <button
                  onClick={onSaveSession}
                  disabled={saving}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-edge bg-paper text-ink text-sm font-semibold hover:bg-sunken transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Save size={16} /> {saving ? "Se salvează…" : "Salvează sesiunea"}
                </button>
              )}
            </div>
            {savedMsg && (
              <div
                role="status"
                className="mb-5 px-4 py-3 rounded-xl bg-verified-tint border border-verified-edge text-verified-ink text-sm"
              >
                {savedMsg}
              </div>
            )}
            <div className="grid gap-6 grid-cols-[repeat(auto-fill,minmax(17rem,1fr))]">
              {items.map((ex) => (
                <ProblemCard
                  key={ex.id}
                  exercise={ex}
                  topicLabel={topicsData?.labels[ex.topic]}
                  activeView={active?.id === ex.id ? active.view : null}
                  onOpen={(view) => openSolution(ex.id, view)}
                />
              ))}
            </div>
          </section>
        </div>
      </div>

      {activeExercise && (
        <>
          <div
            role="separator"
            aria-orientation="vertical"
            aria-label="Redimensionează panoul de soluții"
            aria-valuenow={Math.round(paneWidth)}
            aria-valuemin={PANE_MIN}
            tabIndex={0}
            onPointerDown={onResizeStart}
            onKeyDown={onResizeKey}
            className="hidden lg:flex w-2 shrink-0 cursor-col-resize items-center justify-center bg-edge/40 hover:bg-oxblood/30 focus-visible:bg-oxblood/40 transition-colors group"
            title="Trage pentru a redimensiona"
          >
            <GripVertical
              size={16}
              className="text-ink-faint group-hover:text-oxblood transition-colors"
            />
          </div>

          <SolutionPanel
            exercise={activeExercise}
            topicLabel={topicsData?.labels[activeExercise.topic]}
            view={active?.view ?? "answer"}
            onView={(view) => setActive({ id: activeExercise.id, view })}
            onClose={() => setActive(null)}
          />
        </>
      )}
    </div>
  );
}

function Field({
  label,
  children,
  full,
}: {
  label: string;
  children: React.ReactNode;
  full?: boolean;
}) {
  return (
    <div className={full ? "md:col-span-2" : ""}>
      <div className="text-sm font-semibold text-ink mb-2">{label}</div>
      {children}
    </div>
  );
}
