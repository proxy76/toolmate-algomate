import type { Exercise } from "../types";
import type { SolutionView } from "./ProblemCard";
import { TeX } from "./TeX";

/**
 * One solution view (hint / answer / steps) as a color-coded box. Shared by the
 * desktop SolutionPanel and the mobile inline reveal so both look identical.
 */
export function SolutionBody({ exercise, view }: { exercise: Exercise; view: SolutionView }) {
  if (view === "hint") {
    return (
      <div className="p-4 bg-ochre/10 border border-ochre/30 rounded-xl text-ink animate-fadeIn">
        <TeX source={exercise.hint_latex} />
      </div>
    );
  }

  if (view === "answer") {
    return (
      <div className="p-4 bg-verified-tint border border-verified-edge rounded-xl text-verified-ink font-medium text-lg animate-fadeIn">
        <TeX source={exercise.answer_latex} />
      </div>
    );
  }

  return exercise.steps_latex?.length ? (
    <ol className="p-4 bg-sunken border border-edge rounded-xl text-ink text-sm space-y-2 animate-fadeIn list-decimal list-inside marker:text-ink-faint marker:font-semibold">
      {exercise.steps_latex.map((step, i) => (
        <li key={i} className="pl-1">
          <TeX source={step} />
        </li>
      ))}
    </ol>
  ) : (
    <p className="p-4 text-sm text-ink-muted animate-fadeIn">
      Această problemă nu are pașii rezolvării.
    </p>
  );
}
