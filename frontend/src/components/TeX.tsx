import katex from "katex";
import { useMemo } from "react";

/**
 * Renders text that may contain inline math wrapped in $...$.
 * KaTeX is configured with trust: false so server-supplied LaTeX cannot
 * inject arbitrary HTML even though we use dangerouslySetInnerHTML below.
 */
export function TeX({ source }: { source: string }) {
  const parts = useMemo(() => source.split("$"), [source]);
  return (
    <span className="leading-relaxed">
      {parts.map((part, i) => {
        if (i % 2 === 1) {
          let html: string;
          try {
            html = katex.renderToString(part, {
              throwOnError: false,
              trust: false,
              strict: "ignore",
            });
          } catch {
            return (
              <span key={i} className="text-danger">
                {part}
              </span>
            );
          }
          return (
            <span
              key={i}
              className="mx-0.5"
              dangerouslySetInnerHTML={{ __html: html }}
            />
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}
