import { CheckCircle, Lightbulb, ListOrdered } from "lucide-react";
import { useState } from "react";

import type { Exercise } from "../types";
import { TeX } from "./TeX";

const DIFFICULTY_LABEL: Record<number, string> = { 1: "Ușor", 2: "Mediu", 3: "Dificil" };

export function ExerciseCard({ exercise, topicLabel }: { exercise: Exercise; topicLabel?: string }) {
  const [showHint, setShowHint] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);
  const [showSteps, setShowSteps] = useState(false);

  const difficultyTag = [DIFFICULTY_LABEL[exercise.difficulty] ?? "—", exercise.bac_context]
    .filter(Boolean)
    .join(" · ");
  const hasSteps = !!exercise.steps_latex?.length;

  return (
    <div className="bg-paper border border-edge rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col h-full">
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

      <div className="space-y-3 mt-auto">
        <div>
          <button
            type="button"
            onClick={() => setShowHint((v) => !v)}
            aria-expanded={showHint}
            className={`flex items-center gap-2 text-sm font-semibold transition-colors rounded ${
              showHint ? "text-ochre-ink" : "text-ink-muted hover:text-ochre-ink"
            }`}
          >
            <Lightbulb size={18} className={showHint ? "fill-ochre/30" : ""} />
            {showHint ? "Ascunde indiciul" : "Arată indiciul"}
          </button>
          {showHint && (
            <div className="mt-2 p-3 bg-ochre/10 border border-ochre/30 rounded-xl text-ink text-sm animate-fadeIn">
              <TeX source={exercise.hint_latex} />
            </div>
          )}
        </div>

        <div>
          <button
            type="button"
            onClick={() => setShowAnswer((v) => !v)}
            aria-expanded={showAnswer}
            className={`flex items-center gap-2 text-sm font-semibold transition-colors rounded ${
              showAnswer ? "text-verified-ink" : "text-ink-muted hover:text-verified-ink"
            }`}
          >
            <CheckCircle size={18} className={showAnswer ? "fill-verified/20" : ""} />
            {showAnswer ? "Ascunde răspunsul" : "Arată răspunsul"}
          </button>
          {showAnswer && (
            <div className="mt-2 p-4 bg-verified-tint border border-verified-edge rounded-xl text-verified-ink font-medium animate-fadeIn text-lg">
              <TeX source={exercise.answer_latex} />
            </div>
          )}
        </div>

        {hasSteps && (
          <div>
            <button
              type="button"
              onClick={() => setShowSteps((v) => !v)}
              aria-expanded={showSteps}
              className={`flex items-center gap-2 text-sm font-semibold transition-colors rounded ${
                showSteps ? "text-ink" : "text-ink-muted hover:text-ink"
              }`}
            >
              <ListOrdered size={18} />
              {showSteps ? "Ascunde pașii" : "Arată pașii rezolvării"}
            </button>
            {showSteps && (
              <ol className="mt-2 p-4 bg-sunken border border-edge rounded-xl text-ink text-sm space-y-2 animate-fadeIn list-decimal list-inside marker:text-ink-faint marker:font-semibold">
                {exercise.steps_latex!.map((step, i) => (
                  <li key={i} className="pl-1">
                    <TeX source={step} />
                  </li>
                ))}
              </ol>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
