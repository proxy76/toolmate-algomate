import { CheckCircle, Lightbulb, ListOrdered } from "lucide-react";

import type { Exercise } from "../types";
import { TeX } from "./TeX";

export type SolutionView = "hint" | "answer" | "steps";

const DIFFICULTY_LABEL: Record<number, string> = { 1: "Ușor", 2: "Mediu", 3: "Dificil" };

/**
 * A problem on the worksheet. It no longer reveals anything inline — its three
 * triggers open the shared SolutionPanel, so cards keep a uniform height and a
 * row never grows when one answer is shown.
 */
export function ProblemCard({
  exercise,
  topicLabel,
  activeView,
  onOpen,
}: {
  exercise: Exercise;
  topicLabel?: string;
  /** Which view is currently open for *this* card, or null if it isn't active. */
  activeView: SolutionView | null;
  onOpen: (view: SolutionView) => void;
}) {
  const difficultyTag = [DIFFICULTY_LABEL[exercise.difficulty] ?? "—", exercise.bac_context]
    .filter(Boolean)
    .join(" · ");
  const hasSteps = !!exercise.steps_latex?.length;
  const isActive = activeView !== null;

  return (
    <div
      className={`bg-paper rounded-2xl p-6 shadow-sm transition flex flex-col h-full border ${
        isActive
          ? "border-oxblood ring-1 ring-oxblood/30"
          : "border-edge hover:shadow-md"
      }`}
    >
      <div className="flex justify-between items-center mb-5 gap-2 flex-wrap">
        <span className="bg-oxblood/10 text-oxblood-deep text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
          Exercițiul {exercise.index}
        </span>
        <div className="flex gap-2 text-xs">
          {topicLabel && (
            <span className="bg-sunken text-ink-muted px-2.5 py-1 rounded-full border border-edge">
              {topicLabel}
            </span>
          )}
          <span className="bg-ochre/15 text-ochre-ink px-2.5 py-1 rounded-full font-semibold">
            {difficultyTag}
          </span>
        </div>
      </div>

      <div className="text-lg text-mathink mb-6 flex-grow font-medium leading-relaxed">
        <TeX source={exercise.question_latex} />
      </div>

      <div className={`mt-auto grid gap-2 ${hasSteps ? "grid-cols-3" : "grid-cols-2"}`}>
        <Trigger
          label="Indiciu"
          icon={<Lightbulb size={16} />}
          active={activeView === "hint"}
          activeClass="bg-ochre/15 text-ochre-ink border-ochre/40"
          onClick={() => onOpen("hint")}
        />
        <Trigger
          label="Răspuns"
          icon={<CheckCircle size={16} />}
          active={activeView === "answer"}
          activeClass="bg-verified-tint text-verified-ink border-verified-edge"
          onClick={() => onOpen("answer")}
        />
        {hasSteps && (
          <Trigger
            label="Pași"
            icon={<ListOrdered size={16} />}
            active={activeView === "steps"}
            activeClass="bg-sunken text-ink border-ink/20"
            onClick={() => onOpen("steps")}
          />
        )}
      </div>
    </div>
  );
}

function Trigger({
  label,
  icon,
  active,
  activeClass,
  onClick,
}: {
  label: string;
  icon: React.ReactNode;
  active: boolean;
  activeClass: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`inline-flex items-center justify-center gap-1.5 px-2.5 py-2 rounded-lg text-xs font-semibold border transition-colors ${
        active ? activeClass : "bg-paper text-ink-muted border-edge hover:bg-sunken hover:text-ink"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
