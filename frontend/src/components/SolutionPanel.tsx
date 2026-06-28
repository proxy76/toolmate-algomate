import { CheckCircle, Lightbulb, ListOrdered, PanelRight, X } from "lucide-react";
import { useEffect } from "react";

import type { Exercise } from "../types";
import type { SolutionView } from "./ProblemCard";
import { TeX } from "./TeX";

/**
 * The solution pane. On desktop it's a full-height right column — a second
 * tiled window beside the worksheet. On mobile it slides up as a full-screen
 * modal. One pane serves the whole set; nothing reflows when it opens.
 */
export function SolutionPanel({
  exercise,
  topicLabel,
  view,
  onView,
  onClose,
}: {
  exercise: Exercise | null;
  topicLabel?: string;
  view: SolutionView;
  onView: (view: SolutionView) => void;
  onClose: () => void;
}) {
  const open = !!exercise;

  // Escape closes the pane (clears it back to the resting state on desktop).
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <aside
      className={`${open ? "flex" : "hidden"} lg:flex flex-col bg-paper
        fixed inset-0 z-50 lg:static lg:z-auto lg:inset-auto
        lg:h-full lg:w-[var(--pane-w,28rem)] lg:shrink-0
        border-edge lg:border-l overflow-hidden`}
      aria-label="Soluție"
    >
      {exercise ? (
        <>
          <div className="flex items-center justify-between gap-3 px-5 py-4 border-b border-edge shrink-0">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="bg-oxblood/10 text-oxblood-deep font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                Exercițiul {exercise.index}
              </span>
              {topicLabel && (
                <span className="bg-sunken text-ink-muted px-2.5 py-1 rounded-full border border-edge">
                  {topicLabel}
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Închide soluția"
              className="-mr-1 p-1.5 rounded-lg text-ink-muted hover:bg-sunken hover:text-ink transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-5 py-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-ink-faint mb-1.5">
              Întrebarea
            </div>
            <div className="text-mathink font-medium leading-relaxed">
              <TeX source={exercise.question_latex} />
            </div>

            <div className="mt-5 grid grid-cols-3 gap-2">
              <Tab
                label="Indiciu"
                icon={<Lightbulb size={15} />}
                active={view === "hint"}
                activeClass="bg-ochre/15 text-ochre-ink border-ochre/40"
                onClick={() => onView("hint")}
              />
              <Tab
                label="Răspuns"
                icon={<CheckCircle size={15} />}
                active={view === "answer"}
                activeClass="bg-verified-tint text-verified-ink border-verified-edge"
                onClick={() => onView("answer")}
              />
              <Tab
                label="Pași"
                icon={<ListOrdered size={15} />}
                active={view === "steps"}
                activeClass="bg-sunken text-ink border-ink/20"
                disabled={!exercise.steps_latex?.length}
                onClick={() => onView("steps")}
              />
            </div>

            <div className="mt-4">
              {view === "hint" && (
                <div className="p-4 bg-ochre/10 border border-ochre/30 rounded-xl text-ink animate-fadeIn">
                  <TeX source={exercise.hint_latex} />
                </div>
              )}
              {view === "answer" && (
                <div className="p-4 bg-verified-tint border border-verified-edge rounded-xl text-verified-ink font-medium text-lg animate-fadeIn">
                  <TeX source={exercise.answer_latex} />
                </div>
              )}
              {view === "steps" &&
                (exercise.steps_latex?.length ? (
                  <ol className="p-4 bg-sunken border border-edge rounded-xl text-ink text-sm space-y-2 animate-fadeIn list-decimal list-inside marker:text-ink-faint marker:font-semibold">
                    {exercise.steps_latex.map((step, i) => (
                      <li key={i} className="pl-1">
                        <TeX source={step} />
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="text-sm text-ink-muted">Această problemă nu are pașii rezolvării.</p>
                ))}
            </div>
          </div>
        </>
      ) : (
        // Desktop resting state — the pane is always present beside the worksheet.
        <div className="m-auto px-8 py-12 text-center max-w-xs">
          <span className="inline-flex p-3 rounded-xl bg-sunken text-ink-muted mb-4">
            <PanelRight size={22} />
          </span>
          <p className="font-semibold text-ink">Soluțiile apar aici</p>
          <p className="mt-1.5 text-sm text-ink-muted leading-relaxed">
            Alege <span className="font-semibold text-ochre-ink">Indiciu</span>,{" "}
            <span className="font-semibold text-verified-ink">Răspuns</span> sau{" "}
            <span className="font-semibold text-ink">Pași</span> la o problemă, iar rezolvarea se
            deschide în acest panou.
          </p>
        </div>
      )}
    </aside>
  );
}

function Tab({
  label,
  icon,
  active,
  activeClass,
  disabled,
  onClick,
}: {
  label: string;
  icon: React.ReactNode;
  active: boolean;
  activeClass: string;
  disabled?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-pressed={active}
      className={`inline-flex items-center justify-center gap-1.5 px-2.5 py-2 rounded-lg text-xs font-semibold border transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
        active
          ? activeClass
          : "bg-paper text-ink-muted border-edge enabled:hover:bg-sunken enabled:hover:text-ink"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
