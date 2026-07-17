/** Romanian-language helpers for copy that counts things. */

/**
 * Count a noun the way Romanian does.
 *
 * Two rules, both of which the naive `n === 1 ? sg : pl` gets wrong:
 *  - 1 takes the singular — "1 problemă rezolvată".
 *  - from 20 up, the noun needs `de` — "2350 de probleme" — except where the last two
 *    digits land in 1–19, which stay bare: "116 probleme", but "120 de probleme".
 */
export function roCount(n: number, singular: string, plural: string): string {
  if (n === 1) return `1 ${singular}`;
  const tail = n % 100;
  const needsDe = n >= 20 && !(tail >= 1 && tail <= 19);
  return `${n} ${needsDe ? "de " : ""}${plural}`;
}
