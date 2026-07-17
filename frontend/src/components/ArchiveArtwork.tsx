import { useCallback, useLayoutEffect, useRef, useState } from "react";

import type { ArchiveProblem } from "../types";

/**
 * The floor for how small the exam's own typesetting may be drawn, in CSS px per
 * point of artwork. A problem is ~500pt wide, so fitting one to a 390px phone would
 * render its 11pt maths at about 8px — present, but not readable. Where the column is
 * narrower than that, the card scrolls sideways rather than shrink the maths away.
 */
export const MIN_LEGIBLE_PX_PER_PT = 1.15;

/** Nothing to drag until the artwork overruns its column by a noticeable amount. */
const OVERFLOW_EPSILON = 2;

type Metrics = { left: number; view: number; total: number };

export function ArchiveArtwork({
  problem,
  width,
}: {
  problem: ArchiveProblem;
  width: number;
}) {
  const scroller = useRef<HTMLDivElement>(null);
  const [failed, setFailed] = useState(false);
  const [m, setM] = useState<Metrics>({ left: 0, view: 0, total: 0 });

  const measure = useCallback(() => {
    const el = scroller.current;
    if (!el) return;
    setM({ left: el.scrollLeft, view: el.clientWidth, total: el.scrollWidth });
  }, []);

  useLayoutEffect(() => {
    const el = scroller.current;
    if (!el) return;
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [measure]);

  const overflow = Math.max(0, m.total - m.view);
  const scrollable = overflow > OVERFLOW_EPSILON;
  const atStart = m.left <= 1;
  const atEnd = m.left >= overflow - 1;

  const alt = `Problemă de BAC, ${problem.session} ${problem.year}`;

  if (failed) {
    return (
      <p className="py-6 text-center text-sm text-ink-muted">
        Problema nu a putut fi încărcată.
      </p>
    );
  }

  return (
    <div>
      <div className="relative">
        <div
          ref={scroller}
          onScroll={measure}
          // Focusable so the arrow keys can drive it too — the drag bar below is
          // pointer affordance, not the only way across.
          tabIndex={scrollable ? 0 : -1}
          role={scrollable ? "region" : undefined}
          aria-label={scrollable ? `${alt} (derulează lateral)` : undefined}
          className="overflow-x-auto scrollbar-none rounded"
        >
          <img
            src={problem.src}
            alt={alt}
            loading="lazy"
            decoding="async"
            onLoad={measure}
            onError={() => setFailed(true)}
            style={{
              // Fill the column where there's room; below that hold a legible size
              // and let the card scroll rather than shrink the maths away.
              width: `max(100%, ${Math.round(width * MIN_LEGIBLE_PX_PER_PT)}px)`,
              // The artwork's own ratio holds the space, so the list never jumps as
              // images stream in.
              aspectRatio: String(problem.ratio),
            }}
            className="h-auto block max-w-none"
          />
        </div>

        {/* Edge fades: the line visibly keeps going. Each one is only drawn while
            there is travel left on its side, so the maths it softens is always maths
            you can scroll to — nothing is hidden where it can't be reached. */}
        {scrollable && !atStart && (
          <div
            aria-hidden
            className="pointer-events-none absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-paper to-transparent"
          />
        )}
        {scrollable && !atEnd && (
          <div
            aria-hidden
            className="pointer-events-none absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-paper to-transparent"
          />
        )}
      </div>

      {scrollable && <DragBar scroller={scroller} m={m} overflow={overflow} />}
    </div>
  );
}

/**
 * The scrollbar the platform won't reliably draw. A touch overlay scrollbar fades out
 * a second after it appears, so a problem that runs off the card looks like a problem
 * that is simply cut off. This one is always there while there's anything to reach,
 * and it's a handle in its own right: drag it, or drop the thumb anywhere on the track.
 */
function DragBar({
  scroller,
  m,
  overflow,
}: {
  scroller: React.RefObject<HTMLDivElement>;
  m: Metrics;
  overflow: number;
}) {
  const track = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);

  const progress = overflow > 0 ? Math.min(1, Math.max(0, m.left / overflow)) : 0;
  // The thumb is the share of the problem you can currently see, so its size says how
  // much is left — with a floor, since a very wide problem would otherwise leave a
  // sliver too small to grab.
  const thumbPct = Math.max(18, Math.min(100, (m.view / (m.total || 1)) * 100));

  // Map a point on the track to a scroll offset. The thumb has width, so only
  // `100 - thumbPct` of the track is actually travel — anchor to the thumb's centre.
  const scrollTo = useCallback(
    (clientX: number) => {
      const el = scroller.current;
      const rect = track.current?.getBoundingClientRect();
      if (!el || !rect || rect.width <= 0) return;
      const half = (thumbPct / 100) * rect.width * 0.5;
      const travel = rect.width - half * 2;
      const at = (clientX - rect.left - half) / (travel || 1);
      el.scrollLeft = Math.min(1, Math.max(0, at)) * overflow;
    },
    [scroller, overflow, thumbPct],
  );

  const onPointerDown = (e: React.PointerEvent) => {
    e.preventDefault();
    e.currentTarget.setPointerCapture(e.pointerId);
    setDragging(true);
    scrollTo(e.clientX);
  };

  return (
    <div
      ref={track}
      onPointerDown={onPointerDown}
      onPointerMove={(e) => dragging && scrollTo(e.clientX)}
      onPointerUp={() => setDragging(false)}
      onPointerCancel={() => setDragging(false)}
      aria-hidden
      className="relative mt-2.5 h-4 cursor-grab touch-none select-none active:cursor-grabbing"
    >
      <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-1.5 rounded-full bg-sunken border border-edge" />
      <div
        className={`absolute top-1/2 -translate-y-1/2 h-1.5 rounded-full transition-colors ${
          dragging ? "bg-oxblood" : "bg-oxblood/60"
        }`}
        style={{
          width: `${thumbPct}%`,
          left: `${progress * (100 - thumbPct)}%`,
        }}
      />
    </div>
  );
}
