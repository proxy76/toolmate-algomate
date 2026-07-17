import { useLayoutEffect, useMemo, useRef, useState } from "react";

import type { ArchiveProblem, ArchiveSegment } from "../types";

/**
 * The floor for how small the exam's own typesetting may be drawn, in CSS px per
 * point of artwork. A problem is ~500pt wide, so fitting one to a 390px phone would
 * render its 11pt maths at about 8px — present, but not readable.
 *
 * It doubles as the wrap budget (`available ÷ this`), so raising it buys larger type
 * at the cost of more rows. At 1.35 an 11pt formula lands at ~15px, the size of the
 * prose around it.
 */
export const MIN_LEGIBLE_PX_PER_PT = 1.35;

/** Past this the maths just looks oversized on a narrow screen. */
const MAX_PX_PER_PT = 1.7;

/** Indent on a carried-over row, in points — the signal that a line continued. */
const CONTINUATION_INDENT_PT = 10;

/** Vertical rhythm when wrapped, in points: within one line, and between lines. */
const ROW_GAP_PT = 2;
const LINE_GAP_PT = 5;

type Row = { x0: number; x1: number; top: number; height: number; carried: boolean };

/**
 * Pack a line's segments into rows that fit the budget — the same greedy rule a text
 * engine uses, over chunks the extractor proved are separated by whitespace. A row
 * takes the union of its segments' boxes, so it is only as tall as what it holds.
 *
 * The first row starts at the problem's shared left edge to keep the `5p` gutter
 * aligned; carried rows start at their own ink and are indented instead.
 */
function packLine(
  segs: ArchiveSegment[],
  left: number,
  budget: number,
  indent: number,
): Row[] {
  const rows: Row[] = [];
  let cur: ArchiveSegment[] = [];
  let start = left;

  const flush = (carried: boolean) => {
    if (!cur.length) return;
    const top = Math.min(...cur.map((s) => s[2]));
    const bottom = Math.max(...cur.map((s) => s[2] + s[3]));
    rows.push({ x0: start, x1: cur[cur.length - 1][1], top, height: bottom - top, carried });
  };

  for (const seg of segs) {
    const room = rows.length ? budget - indent : budget;
    if (cur.length && seg[1] - start > room) {
      flush(rows.length > 0);
      cur = [];
      start = seg[0]; // a carried row begins at its own ink, not the gutter
    }
    cur.push(seg);
  }
  flush(rows.length > 0);
  return rows;
}

/**
 * A problem, wrapped to fit rather than scrolled.
 *
 * A picture cannot reflow: on a phone a ~500pt-wide problem either shrinks below
 * reading size or runs off the side. So where it doesn't fit, the artwork is cut at
 * pre-measured whitespace and the pieces are stacked — each row a CSS window onto the
 * same PNG, so this costs no extra asset and no extra request. Where it does fit, the
 * plain image is used untouched.
 */
export function ArchiveArtwork({
  problem,
  width,
}: {
  problem: ArchiveProblem;
  width: number;
}) {
  const box = useRef<HTMLDivElement>(null);
  const [avail, setAvail] = useState(0);
  const [failed, setFailed] = useState(false);

  useLayoutEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => setAvail(entry.contentRect.width));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const height = width / problem.ratio;

  const layout = useMemo(() => {
    const lines = problem.lines ?? [];
    if (!avail || !lines.length) return null;

    const right = Math.max(...lines.map((segs) => segs[segs.length - 1][1]));
    const content = right - problem.x0;
    if (content <= 0) return null;
    // Room to show it whole and still read it? Then don't touch it.
    if (avail / content >= MIN_LEGIBLE_PX_PER_PT) return null;

    const budget = avail / MIN_LEGIBLE_PX_PER_PT;
    const rows: Array<Row & { firstOfLine: boolean }> = [];
    let widest = 0;
    for (const segs of lines) {
      const packed = packLine(segs, problem.x0, budget, CONTINUATION_INDENT_PT);
      packed.forEach((r, i) => {
        widest = Math.max(widest, r.x1 - r.x0 + (r.carried ? CONTINUATION_INDENT_PT : 0));
        rows.push({ ...r, firstOfLine: i === 0 });
      });
    }
    if (!rows.length) return null;
    // Every row now fits inside the budget, so grow the type back up until the widest
    // one fills the column — wrapping bought room; spend it on legibility.
    const scale = Math.min(MAX_PX_PER_PT, Math.max(MIN_LEGIBLE_PX_PER_PT, avail / widest));
    return { rows, scale };
  }, [problem, avail]);

  if (failed) {
    return (
      <p className="py-6 text-center text-sm text-ink-muted">
        Problema nu a putut fi încărcată.
      </p>
    );
  }

  const alt = `Problemă de BAC, ${problem.session} ${problem.year}`;

  return (
    <div ref={box}>
      {layout ? (
        <div role="img" aria-label={alt}>
          {layout.rows.map((r, i) => (
            <div
              key={i}
              aria-hidden
              style={{
                width: (r.x1 - r.x0) * layout.scale,
                height: r.height * layout.scale,
                marginTop:
                  i === 0 ? 0 : (r.firstOfLine ? LINE_GAP_PT : ROW_GAP_PT) * layout.scale,
                marginLeft: r.carried ? CONTINUATION_INDENT_PT * layout.scale : 0,
                backgroundImage: `url(${problem.src})`,
                backgroundSize: `${width * layout.scale}px ${height * layout.scale}px`,
                backgroundPosition: `${-r.x0 * layout.scale}px ${-r.top * layout.scale}px`,
                backgroundRepeat: "no-repeat",
              }}
            />
          ))}
        </div>
      ) : (
        <img
          src={problem.src}
          alt={alt}
          loading="lazy"
          decoding="async"
          onError={() => setFailed(true)}
          // The artwork's own ratio holds the space, so the list never jumps as
          // images stream in.
          style={{ aspectRatio: String(problem.ratio) }}
          className="w-full h-auto block"
        />
      )}
    </div>
  );
}
