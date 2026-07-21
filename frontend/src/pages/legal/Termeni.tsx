import { Link } from "react-router-dom";

import { LEGAL } from "../../legal";
import { LegalDoc, List, Section } from "./LegalDoc";

export function Termeni() {
  return (
    <LegalDoc
      title="Termeni și Condiții"
      intro={`Acești termeni reglementează utilizarea platformei Algomate (${LEGAL.domain}). Prin crearea unui cont sau prin utilizarea platformei, confirmi că ai citit și accepți acești termeni. Dacă nu ești de acord cu ei, te rugăm să nu folosești platforma.`}
    >
      <Section n={1} title="Cine suntem">
        <p>
          Platforma Algomate („platforma”, „serviciul”) este operată de {LEGAL.operatorName}, în
          calitate de operator individual („noi”, „operatorul”). Ne poți contacta la adresa{" "}
          <a href={`mailto:${LEGAL.contactEmail}`} className="text-oxblood font-semibold hover:underline">
            {LEGAL.contactEmail}
          </a>
          .
        </p>
      </Section>

      <Section n={2} title="Ce oferă platforma">
        <p>
          Algomate este o platformă educațională care generează exerciții și simulări de
          matematică pentru examenul de Bacalaureat, pe profiluri de studiu, împreună cu materiale
          de arhivă și articole. Exercițiile sunt generate automat și verificate simbolic, însă
          platforma reprezintă un <strong>instrument de antrenament</strong>, nu o sursă oficială și
          nu garantează un anumit rezultat la examen.
        </p>
      </Section>

      <Section n={3} title="Conturi și eligibilitate">
        <List>
          <li>
            Pentru a folosi anumite funcții trebuie să îți creezi un cont cu o adresă de email
            validă, pe care o confirmi printr-un link primit prin email.
          </li>
          <li>
            Ești responsabil pentru păstrarea confidențialității parolei și pentru toate activitățile
            desfășurate prin contul tău. Un cont poate avea o singură sesiune activă la un moment dat.
          </li>
          <li>
            Platforma se adresează elevilor și persoanelor interesate de pregătirea pentru
            Bacalaureat. Dacă ai <strong>sub 16 ani</strong>, îți poți crea un cont numai cu acordul
            și sub supravegherea unui părinte sau reprezentant legal, în conformitate cu{" "}
            <Link to="/confidentialitate" className="text-oxblood font-semibold hover:underline">
              Politica de Confidențialitate
            </Link>
            .
          </li>
          <li>Furnizezi informații reale și îți menții datele de contact actualizate.</li>
        </List>
      </Section>

      <Section n={4} title="Utilizare acceptabilă">
        <p>Te obligi să nu:</p>
        <List>
          <li>
            folosești platforma în scopuri ilegale sau care încalcă drepturile altor persoane;
          </li>
          <li>
            încerci să accesezi neautorizat sistemele, să le suprasoliciti, să extragi automat
            conținutul în masă (scraping) sau să ocolești măsurile de securitate;
          </li>
          <li>
            revinzi, redistribui sau exploatezi comercial conținutul generat fără acordul nostru
            scris;
          </li>
          <li>partajezi contul cu terți sau creezi conturi multiple în mod abuziv.</li>
        </List>
        <p>
          Putem suspenda sau închide conturile care încalcă acești termeni, cu sau fără notificare
          prealabilă, în funcție de gravitatea încălcării.
        </p>
      </Section>

      <Section n={5} title="Proprietate intelectuală">
        <p>
          Platforma, codul, designul, textele, arhitectura generatoarelor și materialele proprii
          sunt protejate de drepturile de proprietate intelectuală și ne aparțin. Îți acordăm un
          drept limitat, neexclusiv și netransferabil de a folosi platforma și materialele generate
          în scop personal, educativ, necomercial.
        </p>
        <p>
          Subiectele de Bacalaureat din secțiunea Arhivă sunt documente publice, reproduse în scop
          educativ; drepturile asupra lor aparțin autorilor / instituțiilor emitente.
        </p>
      </Section>

      <Section n={6} title={LEGAL.paymentsActive ? "Plăți, abonamente și retragere" : "Costuri"}>
        {LEGAL.paymentsActive ? (
          <>
            <p>
              Anumite funcții pot fi oferite contra cost, sub formă de plată unică sau abonament.
              Prețurile, ceea ce include fiecare plan și modalitatea de plată sunt afișate în
              platformă înainte de finalizarea comenzii. Prin plasarea comenzii accepți prețul
              afișat.
            </p>
            <p>
              <strong>Dreptul de retragere.</strong> În calitate de consumator ai, în principiu,
              dreptul de a te retrage dintr-un contract la distanță în termen de 14 zile, conform
              OUG nr. 34/2014. În cazul conținutului digital și al serviciilor începute cu acordul
              tău expres înainte de expirarea acestui termen, îți poți pierde dreptul de retragere;
              vei fi informat despre acest lucru înainte de plată.
            </p>
            <p>
              Rambursările, atunci când se aplică, se fac prin aceeași metodă de plată folosită la
              achiziție. Pentru orice solicitare legată de plăți ne poți scrie la{" "}
              <a href={`mailto:${LEGAL.contactEmail}`} className="text-oxblood font-semibold hover:underline">
                {LEGAL.contactEmail}
              </a>
              .
            </p>
          </>
        ) : (
          <p>
            În prezent utilizarea platformei este <strong>gratuită</strong>. Dacă vom introduce
            funcții cu plată în viitor, condițiile comerciale (prețuri, abonamente și dreptul legal
            de retragere de 14 zile) vor fi afișate clar înainte de orice plată, iar acești termeni
            vor fi actualizați în consecință.
          </p>
        )}
      </Section>

      <Section n={7} title="Disponibilitate și modificări ale serviciului">
        <p>
          Depunem eforturi rezonabile pentru ca platforma să fie disponibilă și corectă, dar o
          oferim „ca atare” și „în măsura disponibilității”. Putem modifica, suspenda temporar sau
          întrerupe funcții pentru mentenanță, îmbunătățiri sau din motive tehnice, fără a fi
          răspunzători pentru eventualele indisponibilități.
        </p>
      </Section>

      <Section n={8} title="Limitarea răspunderii">
        <p>
          Conținutul are scop educativ. Nu garantăm că exercițiile, soluțiile sau simulările sunt
          lipsite de erori ori că reflectă întocmai cerințele oficiale de examen și nu garantăm un
          anumit rezultat academic. În limitele permise de lege, nu răspundem pentru daune indirecte
          rezultate din utilizarea sau imposibilitatea de a utiliza platforma. Nimic din acești
          termeni nu limitează răspunderea care nu poate fi limitată legal.
        </p>
      </Section>

      <Section n={9} title="Prelucrarea datelor cu caracter personal">
        <p>
          Modul în care colectăm și prelucrăm datele tale este descris în{" "}
          <Link to="/confidentialitate" className="text-oxblood font-semibold hover:underline">
            Politica de Confidențialitate
          </Link>
          , iar utilizarea stocării locale și a cookie-urilor în{" "}
          <Link to="/cookies" className="text-oxblood font-semibold hover:underline">
            Politica de Cookies
          </Link>
          . Ambele fac parte integrantă din acești termeni.
        </p>
      </Section>

      <Section n={10} title="Modificarea termenilor">
        <p>
          Putem actualiza acești termeni pentru a reflecta schimbări legale sau ale serviciului. Vom
          publica versiunea actualizată pe această pagină și vom modifica data „Ultima actualizare”.
          Continuarea utilizării platformei după publicare înseamnă acceptarea noii versiuni.
        </p>
      </Section>

      <Section n={11} title="Legea aplicabilă și soluționarea litigiilor">
        <p>
          Acești termeni sunt guvernați de legea română. Eventualele litigii se soluționează, pe cât
          posibil, pe cale amiabilă; în caz contrar, sunt de competența instanțelor din {LEGAL.county}.
          În calitate de consumator, poți folosi și platforma europeană de soluționare online a
          litigiilor:{" "}
          <a
            href="https://ec.europa.eu/consumers/odr"
            target="_blank"
            rel="noopener noreferrer"
            className="text-oxblood font-semibold hover:underline"
          >
            ec.europa.eu/consumers/odr
          </a>
          .
        </p>
      </Section>

      <Section n={12} title="Contact">
        <p>
          Pentru orice întrebare legată de acești termeni, scrie-ne la{" "}
          <a href={`mailto:${LEGAL.contactEmail}`} className="text-oxblood font-semibold hover:underline">
            {LEGAL.contactEmail}
          </a>{" "}
          sau prin{" "}
          <Link to="/contact" className="text-oxblood font-semibold hover:underline">
            formularul de contact
          </Link>
          .
        </p>
      </Section>
    </LegalDoc>
  );
}
