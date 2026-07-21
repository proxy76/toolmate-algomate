// ─────────────────────────────────────────────────────────────────────────────
//  SEO — per-route <title>, meta description, canonical URL, Open Graph /
//  Twitter cards, and JSON-LD structured data.
//
//  The site is a client-rendered SPA, so this sets the tags imperatively on
//  navigation. Static routes are driven by the ROUTE_SEO table below (via
//  <SeoManager>, mounted once); dynamic pages (a blog post) set their own tags
//  with the <Seo> component, which runs after the manager and wins.
// ─────────────────────────────────────────────────────────────────────────────
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

import { LEGAL } from "./legal";

/** The public origin used for canonical + Open Graph URLs. Reuses the domain
 *  from legal.ts. ⚠️ Confirm this is the exact host you serve (and pick one of
 *  www / non-www as canonical — mixing them splits ranking). */
export const SITE = {
  url: `https://${LEGAL.domain}`,
  name: "Algomate",
  defaultTitle: "Algomate — Antrenament BAC Matematică",
  defaultDescription:
    "Generator de exerciții și simulări pentru Bacalaureatul la matematică, pe profiluri, cu indicii și răspunsuri verificate. Plus o arhivă de subiecte din anii anteriori.",
  /** 1200×630 PNG for link previews. Leave "" until you add one at
   *  frontend/public/og-cover.png — og:image is skipped while empty. */
  defaultImage: "",
  locale: "ro_RO",
} as const;

export interface SeoMeta {
  /** Page-specific title; the brand is appended automatically. */
  title?: string;
  description?: string;
  /** Canonical path, e.g. "/practice". Defaults to the current pathname. */
  path?: string;
  image?: string;
  noindex?: boolean;
  jsonLd?: unknown;
}

// ── DOM helpers ──────────────────────────────────────────────────────────────

function upsertMeta(attr: "name" | "property", key: string, content: string) {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`);
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function upsertLink(rel: string, href: string) {
  let el = document.head.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`);
  if (!el) {
    el = document.createElement("link");
    el.setAttribute("rel", rel);
    document.head.appendChild(el);
  }
  el.setAttribute("href", href);
}

function absolute(url: string) {
  return url.startsWith("http") ? url : SITE.url + url;
}

/** Apply a page's SEO tags to <head>. Idempotent — safe to call on every route. */
export function applySeo(meta: SeoMeta) {
  if (typeof document === "undefined") return;

  const fullTitle = meta.title ? `${meta.title} · ${SITE.name}` : SITE.defaultTitle;
  const description = meta.description ?? SITE.defaultDescription;
  const url = absolute(meta.path ?? window.location.pathname);
  const image = meta.image ?? SITE.defaultImage;

  document.title = fullTitle;
  upsertMeta("name", "description", description);
  upsertLink("canonical", url);

  upsertMeta("name", "robots", meta.noindex ? "noindex, nofollow" : "index, follow");

  // Open Graph
  upsertMeta("property", "og:title", fullTitle);
  upsertMeta("property", "og:description", description);
  upsertMeta("property", "og:url", url);
  upsertMeta("property", "og:type", "website");
  upsertMeta("property", "og:site_name", SITE.name);
  upsertMeta("property", "og:locale", SITE.locale);

  // Twitter
  upsertMeta("name", "twitter:card", image ? "summary_large_image" : "summary");
  upsertMeta("name", "twitter:title", fullTitle);
  upsertMeta("name", "twitter:description", description);

  if (image) {
    upsertMeta("property", "og:image", absolute(image));
    upsertMeta("name", "twitter:image", absolute(image));
  }

  // JSON-LD: one managed <script>, replaced or removed each navigation.
  const existing = document.head.querySelector('script[data-seo-jsonld="true"]');
  if (meta.jsonLd) {
    const script = existing ?? document.createElement("script");
    script.setAttribute("type", "application/ld+json");
    script.setAttribute("data-seo-jsonld", "true");
    script.textContent = JSON.stringify(meta.jsonLd);
    if (!existing) document.head.appendChild(script);
  } else if (existing) {
    existing.remove();
  }
}

// ── Structured data ──────────────────────────────────────────────────────────

const ORG_JSONLD = [
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: SITE.name,
    url: SITE.url,
    inLanguage: "ro-RO",
  },
  {
    "@context": "https://schema.org",
    "@type": "EducationalOrganization",
    name: SITE.name,
    url: SITE.url,
    email: LEGAL.contactEmail,
    description: SITE.defaultDescription,
  },
];

// ── Static-route table ───────────────────────────────────────────────────────
//  Titles/descriptions written for the queries a BAC student actually types.

export const ROUTE_SEO: Record<string, SeoMeta> = {
  "/": {
    description: SITE.defaultDescription,
    jsonLd: ORG_JSONLD,
  },
  "/practice": {
    title: "Exerciții BAC Matematică — Antrenament",
    description:
      "Generează exerciții de bacalaureat la matematică pe capitole și nivel de dificultate, fiecare cu indicii și răspunsuri verificate simbolic.",
  },
  "/simulate": {
    title: "Simulare BAC Matematică",
    description:
      "Simulează un subiect complet de Bacalaureat la matematică în format oficial (Subiectul I, II și III) și exportă-l ca PDF.",
  },
  "/arhiva": {
    title: "Arhivă subiecte BAC Matematică (2013–2026)",
    description:
      "Subiecte de Bacalaureat la matematică din anii anteriori, organizate pe profil, subiect și an — sesiuni principale, variante și modele.",
  },
  "/blog": {
    title: "Blog — Pregătire Bacalaureat Matematică",
    description:
      "Sfaturi de pregătire, analize de subiecte oficiale și ghiduri pentru Bacalaureatul la matematică.",
  },
  "/contact": {
    title: "Contact",
    description: "Întrebări, erori raportate sau sugestii? Scrie-ne prin pagina de contact Algomate.",
  },
  "/termeni": { title: "Termeni și Condiții" },
  "/confidentialitate": { title: "Politica de Confidențialitate" },
  "/cookies": { title: "Politica de Cookies" },

  // App / auth pages: keep them out of the index.
  "/login": { title: "Autentificare", noindex: true },
  "/register": { title: "Înregistrare", noindex: true },
  "/verify": { title: "Confirmare email", noindex: true },
  "/dashboard": { title: "Contul meu", noindex: true },
  "/admin": { title: "Administrare", noindex: true },
};

/** Mounted once, near the top of the tree. Applies the static-route meta on
 *  every navigation; dynamic pages override afterwards with <Seo>. */
export function SeoManager() {
  const { pathname } = useLocation();
  useEffect(() => {
    applySeo({ ...(ROUTE_SEO[pathname] ?? {}), path: pathname });
  }, [pathname]);
  return null;
}

/** Per-page override for routes whose meta depends on fetched data (blog posts). */
export function Seo(props: SeoMeta) {
  useEffect(() => {
    applySeo(props);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.title, props.description, props.path, props.image, props.noindex, JSON.stringify(props.jsonLd)]);
  return null;
}
