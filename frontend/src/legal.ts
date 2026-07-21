// ─────────────────────────────────────────────────────────────────────────────
//  Legal identity — single source of truth for the Terms, Privacy and Cookie
//  pages, the register consent line, and the footer.
//
//  ⚠️  EDIT THE FOUR VALUES BELOW BEFORE GOING LIVE. They are currently
//      placeholders. Everything legal reads from here, so you only change them
//      in one spot.
//
//  As an *individual* operator (not a registered company) you are not required
//  to publish a full postal address the way an SRL must — a name + a working
//  contact email is the practical minimum. `county` is shown only as the place
//  whose courts/DPA apply; keep it to your județ (e.g. "București").
// ─────────────────────────────────────────────────────────────────────────────

export const LEGAL = {
  /** The person named as operator / data controller ("operator de date"). */
  operatorName: "Răzvan Rădulescu", // ← confirm exact spelling / diacritics

  /** Public contact + GDPR requests inbox. */
  contactEmail: "algomate.razvan@gmail.com", // ← your real public address

  /** County/city whose jurisdiction applies (for governing-law + DPA). */
  county: "România", // ← e.g. "București" or your județ

  /** Bare domain the site is served on, no protocol. Also the canonical host
   *  for SEO (see SITE.url in seo.tsx). */
  domain: "laborator.algomate.ro",

  /** Shown as "Ultima actualizare" on every legal page. Bump when you edit. */
  lastUpdated: "20 iulie 2026",

  /** Romania's Data Protection Authority — fixed, don't change. */
  dpa: {
    name: "Autoritatea Națională de Supraveghere a Prelucrării Datelor cu Caracter Personal (ANSPDCP)",
    url: "https://www.dataprotection.ro",
  },

  /**
   * Flip to `true` once you actually launch paid plans. The Terms already
   * contain the payment / refund / 14-day-withdrawal section; while this is
   * `false` that section renders a short "serviciul este gratuit" note instead.
   */
  paymentsActive: false,
} as const;
