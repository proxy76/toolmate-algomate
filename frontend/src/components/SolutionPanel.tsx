import { CheckCircle, Lightbulb, ListOrdered, PanelRight, X } from "lucide-react";
import { useEffect } from "react";

import type { Exercise } from "../types";
import type { SolutionView } from "./ProblemCard";
import { SolutionBody } from "./SolutionBody";
import { TeX } from "./TeX";

/**
 * The desktop solution pane — a full-height right column tiled beside the
 * worksheet. On mobile (< lg) it is not rendered at all; the solution unfolds
 * inline inside the ProblemCard instead (see ProblemCard), which avoids a
 * fixed-overlay modal and its scroll-bleed problems on phones.
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
      className="hidden lg:flex flex-col bg-paper
        lg:h-full lg:w-[var(--pane-w,28rem)] lg:shrink-0
        border-edge lg:border-l overflow-hidden"
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

            <div className="mt-4" key={view}>
              <SolutionBody exercise={exercise} view={view} />
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
