import { Link } from "react-router-dom";

import { LEGAL } from "../../legal";
import { LegalDoc, Section } from "./LegalDoc";

export function Cookies() {
  return (
    <LegalDoc
      title="Politica de Cookies"
      intro="Această pagină explică ce tehnologii de stocare folosim în browserul tău și de ce. Pe scurt: folosim doar stocare strict necesară pentru autentificare — nu folosim cookie-uri de urmărire sau de publicitate."
    >
      <Section n={1} title="Ce folosim">
        <p>
          Pentru a te menține autentificat, platforma salvează în{" "}
          <strong>stocarea locală a browserului</strong> (localStorage) tokenurile tale de sesiune,
          după ce te conectezi. Acestea sunt necesare pentru funcționarea contului și nu sunt folosite
          pentru a te urmări pe alte site-uri.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border border-edge rounded-lg overflow-hidden">
            <thead className="bg-sunken text-left">
              <tr>
                <th className="px-3 py-2 font-semibold text-ink-strong">Cheie</th>
                <th className="px-3 py-2 font-semibold text-ink-strong">Scop</th>
                <th className="px-3 py-2 font-semibold text-ink-strong">Tip</th>
              </tr>
            </thead>
            <tbody className="text-ink">
              <tr className="border-t border-edge">
                <td className="px-3 py-2 font-mono text-xs">algomate.access</td>
                <td className="px-3 py-2">Token de acces pentru sesiunea autentificată</td>
                <td className="px-3 py-2">Strict necesar</td>
              </tr>
              <tr className="border-t border-edge">
                <td className="px-3 py-2 font-mono text-xs">algomate.refresh</td>
                <td className="px-3 py-2">Token de reînnoire a sesiunii, ca să nu te deconecteze des</td>
                <td className="px-3 py-2">Strict necesar</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Section>

      <Section n={2} title="De ce nu îți cerem consimțământ pentru un banner">
        <p>
          Tehnologiile strict necesare — cele fără de care serviciul pe care l-ai solicitat (contul
          tău) nu poate funcționa — nu necesită consimțământ prealabil, conform legislației privind
          confidențialitatea în comunicații electronice. Întrucât momentan folosim exclusiv astfel de
          stocare, nu afișăm un banner de cookies.
        </p>
      </Section>

      <Section n={3} title="Nu folosim urmărire sau publicitate">
        <p>
          În prezent <strong>nu</strong> folosim cookie-uri de analiză (de ex. Google Analytics),
          pixeli de publicitate sau alte tehnologii de urmărire între site-uri. Dacă vom introduce în
          viitor astfel de tehnologii, îți vom cere consimțământul explicit printr-un banner de
          cookies înainte de a le activa, iar această pagină va fi actualizată în consecință.
        </p>
      </Section>

      <Section n={4} title="Cum controlezi stocarea">
        <p>
          Poți șterge oricând datele salvate de platformă folosind opțiunile browserului („Ștergere
          date de navigare” / „Cookies și date site-uri”). Reține că, dacă ștergi tokenurile de mai
          sus, vei fi deconectat și va trebui să te autentifici din nou. Deconectarea din platformă
          („Ieșire”) elimină, de asemenea, aceste tokenuri.
        </p>
      </Section>

      <Section n={5} title="Legătură cu datele tale">
        <p>
          Pentru modul în care prelucrăm datele cu caracter personal, vezi{" "}
          <Link to="/confidentialitate" className="text-oxblood font-semibold hover:underline">
            Politica de Confidențialitate
          </Link>
          . Pentru întrebări, scrie-ne la{" "}
          <a href={`mailto:${LEGAL.contactEmail}`} className="text-oxblood font-semibold hover:underline">
            {LEGAL.contactEmail}
          </a>
          .
        </p>
      </Section>
    </LegalDoc>
  );
}
