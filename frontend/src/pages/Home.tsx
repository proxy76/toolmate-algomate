import { Activity, ArrowRight, ShieldCheck, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

// Bare profile codes for now. Correct mapping (labels TBD): M1 = mate-info,
// M2 = tehnologic, M3 = pedagogic.
const PROFILES = ["M1", "M2", "M3"];

export function Home() {
  return (
    <div>
      {/* Hero — calm, CTA-first, ink on warm paper. */}
      <section className="border-b border-edge bg-paper">
        <div className="max-w-4xl mx-auto px-6 py-24 md:py-32 text-center">
          <div className="flex flex-wrap justify-center gap-2 mb-7">
            {PROFILES.map((p) => (
              <span
                key={p}
                className="text-xs font-semibold text-oxblood-deep bg-oxblood/10 px-3 py-1 rounded-full"
              >
                {p}
              </span>
            ))}
          </div>

          <div className="mb-6 flex justify-center">
            <p className="inline-flex flex-wrap items-center justify-center gap-1.5 text-xs md:text-sm font-medium text-ink-muted bg-sunken border border-edge rounded-full px-4 py-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-oxblood animate-pulse" aria-hidden />
              <span>
                Această platformă este în{" "}
                <span className="font-semibold text-oxblood-deep">Early Access</span>, așteptăm
                feedback pe{" "}
                <Link
                  to="/contact"
                  className="font-semibold text-oxblood-deep underline underline-offset-2 hover:text-oxblood"
                >
                  pagina de Contact
                </Link>
              </span>
            </p>
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-ink-strong text-balance leading-[1.08]">
            Exerciții de BAC la matematică, cu răspunsuri verificate.
          </h1>

          <p className="mt-6 text-lg text-ink-muted leading-relaxed text-pretty max-w-2xl mx-auto">
            Alege profilul, capitolele și dificultatea, iar Algomate generează un set unic de
            exerciții — fiecare cu indicii și răspunsuri verificate simbolic, nu doar afișate.
          </p>

          <div className="mt-9 flex flex-col sm:flex-row justify-center gap-3">
            <Link
              to="/practice"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99]"
            >
              <Sparkles size={18} /> Generează exerciții
            </Link>
            <Link
              to="/simulate"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-edge bg-paper text-ink font-semibold hover:bg-sunken hover:border-oxblood/40 transition active:scale-[0.99]"
            >
              Simulare BAC <ArrowRight size={18} />
            </Link>
          </div>

          <p className="mt-5 text-sm text-ink-muted">
            Fără cont pentru a începe · indicii și răspunsuri pentru fiecare problemă.
          </p>
        </div>
      </section>

      {/* Value props — a quiet spec strip, hairline-divided, each in its own semantic color. */}
      <section className="max-w-5xl mx-auto px-6 py-20 md:py-24">
        <div className="grid md:grid-cols-3 md:divide-x divide-edge gap-y-10">
          <Value
            tint="bg-oxblood/10 text-oxblood"
            icon={<Sparkles size={20} strokeWidth={2.25} />}
            title="Personalizare totală"
            body="Profil (M1/M2/M3), capitole și dificultate la alegere. Fiecare set este unic, dar reproductibil cu un seed."
          />
          <Value
            tint="bg-verified-tint text-verified-ink"
            icon={<ShieldCheck size={20} strokeWidth={2.25} />}
            title="Răspunsuri verificate"
            body="Motorul folosește sympy pentru a garanta corectitudinea algebrică a fiecărui răspuns — nimic nu este ghicit."
          />
          <Value
            tint="bg-ochre/15 text-ochre-ink"
            icon={<Activity size={20} strokeWidth={2.25} />}
            title="Format BAC autentic"
            body="Modul de simulare urmează structura oficială a subiectelor: Subiectul I (6), II (2) și III (2)."
          />
        </div>
      </section>

      {/* Closing CTA — save progress. */}
      <section className="border-t border-edge bg-sunken">
        <div className="max-w-4xl mx-auto px-6 py-16 flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
          <div>
            <h2 className="text-xl font-bold text-ink-strong">Vrei să-ți salvezi progresul?</h2>
            <p className="mt-1 text-ink-muted">
              Creează un cont gratuit și revizitează seturile generate oricând.
            </p>
          </div>
          <Link
            to="/register"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-oxblood text-paper font-bold hover:bg-oxblood-deep transition active:scale-[0.99] whitespace-nowrap"
          >
            Creează cont <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </div>
  );
}

function Value({
  tint,
  icon,
  title,
  body,
}: {
  tint: string;
  icon: React.ReactNode;
  title: string;
  body: string;
}) {
  return (
    <div className="md:px-8 first:md:pl-0 last:md:pr-0">
      <div className={`inline-flex p-2.5 rounded-xl mb-4 ${tint}`}>{icon}</div>
      <h3 className="text-lg font-bold text-ink-strong mb-1.5">{title}</h3>
      <p className="text-sm text-ink-muted leading-relaxed">{body}</p>
    </div>
  );
}
