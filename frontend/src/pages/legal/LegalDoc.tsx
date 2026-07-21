import { ArrowLeft } from "lucide-react";
import { ReactNode } from "react";
import { Link } from "react-router-dom";

import { LEGAL } from "../../legal";

/** Shared frame for the Terms / Privacy / Cookie pages: back link, title,
 *  last-updated line, and consistent long-form typography. */
export function LegalDoc({ title, intro, children }: { title: string; intro?: string; children: ReactNode }) {
  return (
    <article className="max-w-3xl mx-auto px-6 py-10 md:py-14">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm text-ink-muted font-medium hover:text-oxblood transition-colors"
      >
        <ArrowLeft size={16} /> Înapoi la pagina principală
      </Link>
      <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink-strong text-balance mt-5 mb-2">
        {title}
      </h1>
      <div className="text-sm text-ink-faint mb-8">Ultima actualizare: {LEGAL.lastUpdated}</div>
      {intro && <p className="text-ink-muted leading-relaxed mb-8 text-pretty">{intro}</p>}
      <div className="space-y-8">{children}</div>
    </article>
  );
}

/** A numbered top-level section. */
export function Section({ n, title, children }: { n: number; title: string; children: ReactNode }) {
  return (
    <section>
      <h2 className="text-xl font-bold text-ink-strong mb-3">
        {n}. {title}
      </h2>
      <div className="space-y-3 text-ink leading-relaxed">{children}</div>
    </section>
  );
}

/** A bulleted list styled for the legal prose. */
export function List({ children }: { children: ReactNode }) {
  return <ul className="list-disc pl-5 space-y-1.5 text-ink leading-relaxed">{children}</ul>;
}
