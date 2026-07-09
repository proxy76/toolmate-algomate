import { CheckCircle, Download, Lightbulb, ListOrdered, Loader2, Play } from "lucide-react";
import { useState } from "react";

import { api, apiErrorMessage } from "../api";
import { TeX } from "../components/TeX";
import type { Profile, SimItem, SimProblem, SimSubItem, SimulateResponse } from "../types";
import { PROFILES } from "../types";

const TOPIC_LABELS: Record<string, string> = {
  matrices: "Matrice",
  algebraic_structures: "Lege de compoziție",
  polynomials: "Polinoame",
  derivatives: "Studiu de funcție",
  integrals: "Integrale",
};

export function Simulate() {
  const [profile, setProfile] = useState<Profile>("mate-info");
  const [data, setData] = useState<SimulateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onRun(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      setData(await api.simulate({ profile }));
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function onExportPdf() {
    if (!data) return;
    setError(null);
    setPdfLoading(true);
    try {
      const blob = await api.exportSimulatePdf(data);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `algomate_${data.profile}_Simulare.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setPdfLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 md:py-14">
      <header className="mb-8 max-w-2xl">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong text-balance">
          Simulare BAC
        </h1>
        <p className="mt-3 text-ink-muted leading-relaxed text-pretty">
          Un subiect complet, cu structura oficială: Subiectul I (6 itemi), II și III (câte 2
          probleme cu punctele a, b, c). Fiecare cerință are 5 puncte; 10 puncte din oficiu.
        </p>
      </header>

      <form
        onSubmit={onRun}
        className="bg-paper border border-edge rounded-2xl p-6 md:p-8 shadow-sm mb-10"
      >
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
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
            {loading ? "Se generează…" : "Generează subiect"}
          </button>
          {data && (
            <button
              type="button"
              onClick={onExportPdf}
              disabled={pdfLoading}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-edge bg-paper text-ink font-semibold hover:bg-sunken hover:border-oxblood/40 transition active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {pdfLoading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Download size={18} />
              )}
              {pdfLoading ? "Se generează PDF…" : "Descarcă PDF"}
            </button>
          )}
        </div>
      </form>

      {data && (
        <div className="space-y-10">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-2">
            <h2 className="text-xl font-bold text-ink-strong">
              Variantă · profil {data.profile}
            </h2>
            <span className="text-xs text-ink-muted">
              {data.officiu_points} puncte din oficiu · total {data.total_points} puncte
            </span>
          </div>

          <Subiect title="Subiectul I" points={data.subiect_I.points}>
            <ol className="space-y-5">
              {data.subiect_I.items.map((it) => (
                <ItemRow key={it.number} item={it} />
              ))}
            </ol>
          </Subiect>

          <Subiect title="Subiectul II" points={data.subiect_II.points}>
            <div className="space-y-8">
              {data.subiect_II.problems.map((p) => (
                <ProblemBlock key={p.number} problem={p} />
              ))}
            </div>
          </Subiect>

          <Subiect title="Subiectul III" points={data.subiect_III.points}>
            <div className="space-y-8">
              {data.subiect_III.problems.map((p) => (
                <ProblemBlock key={p.number} problem={p} />
              ))}
            </div>
          </Subiect>
        </div>
      )}
    </div>
  );
}

function Subiect({
  title,
  points,
  children,
}: {
  title: string;
  points: number;
  children: React.ReactNode;
}) {
  return (
    <section className="bg-paper border border-edge rounded-2xl shadow-sm p-6 md:p-8">
      <div className="flex items-baseline justify-between gap-3 mb-5 pb-4 border-b border-edge">
        <h3 className="text-lg font-bold text-ink-strong uppercase tracking-wide">{title}</h3>
        <span className="text-xs font-semibold text-oxblood-deep bg-oxblood/10 px-2.5 py-1 rounded-full">
          {points} puncte
        </span>
      </div>
      {children}
    </section>
  );
}

function ItemRow({ item }: { item: SimItem }) {
  return (
    <li className="flex gap-3">
      <span className="shrink-0 grid place-items-center w-7 h-7 rounded-lg bg-sunken text-ink-muted text-sm font-bold">
        {item.number}
      </span>
      <div className="min-w-0 flex-1">
        <div className="text-mathink font-medium">
          <TeX source={item.question_latex} />
        </div>
        <Reveals item={item} />
      </div>
    </li>
  );
}

function ProblemBlock({ problem }: { problem: SimProblem }) {
  const label = TOPIC_LABELS[problem.topic_primary];
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <h4 className="font-bold text-ink-strong">Problema {problem.number}</h4>
        {label && (
          <span className="text-xs text-ink-muted bg-sunken border border-edge px-2 py-0.5 rounded-full">
            {label}
          </span>
        )}
      </div>
      {problem.statement_latex && (
        <div className="text-mathink font-medium mb-4">
          <TeX source={problem.statement_latex} />
        </div>
      )}
      <ol className="space-y-4">
        {problem.sub_items.map((sub) => (
          <li key={sub.label} className="flex gap-3">
            <span className="shrink-0 font-bold text-oxblood-deep">{sub.label})</span>
            <div className="min-w-0 flex-1">
              <div className="text-mathink">
                <TeX source={sub.question_latex} />
              </div>
              <Reveals item={sub} />
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

/** Inline hint / answer / steps toggles, shared by items and sub-items. */
function Reveals({ item }: { item: SimItem | SimSubItem }) {
  const [open, setOpen] = useState<"hint" | "answer" | "steps" | null>(null);
  const hasHint = !!item.hint_latex;
  const hasSteps = !!item.steps_latex?.length;
  const toggle = (v: "hint" | "answer" | "steps") => setOpen((cur) => (cur === v ? null : v));

  return (
    <div className="mt-2.5">
      <div className="flex flex-wrap gap-2">
        {hasHint && (
          <RevealButton
            active={open === "hint"}
            activeClass="bg-ochre/15 text-ochre-ink border-ochre/40"
            icon={<Lightbulb size={14} />}
            label="Indiciu"
            onClick={() => toggle("hint")}
          />
        )}
        <RevealButton
          active={open === "answer"}
          activeClass="bg-verified-tint text-verified-ink border-verified-edge"
          icon={<CheckCircle size={14} />}
          label="Răspuns"
          onClick={() => toggle("answer")}
        />
        {hasSteps && (
          <RevealButton
            active={open === "steps"}
            activeClass="bg-sunken text-ink border-ink/20"
            icon={<ListOrdered size={14} />}
            label="Pași"
            onClick={() => toggle("steps")}
          />
        )}
      </div>

      {open === "hint" && hasHint && (
        <div className="mt-2 p-3 bg-ochre/10 border border-ochre/30 rounded-xl text-ink text-sm animate-fadeIn">
          <TeX source={item.hint_latex!} />
        </div>
      )}
      {open === "answer" && (
        <div className="mt-2 p-3 bg-verified-tint border border-verified-edge rounded-xl text-verified-ink font-medium animate-fadeIn">
          <TeX source={item.answer_latex} />
        </div>
      )}
      {open === "steps" && hasSteps && (
        <ol className="mt-2 p-3 bg-sunken border border-edge rounded-xl text-ink text-sm space-y-1.5 animate-fadeIn list-decimal list-inside marker:text-ink-faint marker:font-semibold">
          {item.steps_latex!.map((s, i) => (
            <li key={i} className="pl-1">
              <TeX source={s} />
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function RevealButton({
  active,
  activeClass,
  icon,
  label,
  onClick,
}: {
  active: boolean;
  activeClass: string;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
        active ? activeClass : "bg-paper text-ink-muted border-edge hover:bg-sunken hover:text-ink"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
