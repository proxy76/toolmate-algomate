import { Link } from "react-router-dom";

import { LEGAL } from "../../legal";
import { LegalDoc, List, Section } from "./LegalDoc";

export function Confidentialitate() {
  return (
    <LegalDoc
      title="Politica de Confidențialitate"
      intro={`Această politică explică ce date cu caracter personal colectăm prin platforma Algomate (${LEGAL.domain}), de ce le colectăm, cât timp le păstrăm și ce drepturi ai. Prelucrarea respectă Regulamentul (UE) 2016/679 (GDPR) și Legea nr. 190/2018.`}
    >
      <Section n={1} title="Operatorul datelor">
        <p>
          Operator al datelor cu caracter personal este {LEGAL.operatorName}, persoană fizică. Pentru
          orice solicitare privind datele tale sau pentru exercitarea drepturilor de mai jos, ne poți
          contacta la{" "}
          <a href={`mailto:${LEGAL.contactEmail}`} className="text-oxblood font-semibold hover:underline">
            {LEGAL.contactEmail}
          </a>
          .
        </p>
      </Section>

      <Section n={2} title="Ce date colectăm">
        <List>
          <li>
            <strong>Date de cont:</strong> adresa de email, numele de utilizator, profilul de studiu
            ales și parola (stocată exclusiv sub formă criptată / hashuită — nu o putem citi).
          </li>
          <li>
            <strong>Starea contului:</strong> dacă emailul a fost confirmat și un identificator de
            sesiune care asigură o singură sesiune activă.
          </li>
          <li>
            <strong>Date de utilizare:</strong> statistici agregate despre activitatea ta (număr de
            teste generate, exerciții, PDF-uri descărcate) și progresul marcat în secțiunea Arhivă.
          </li>
          <li>
            <strong>Mesaje de contact:</strong> numele, adresa de email și conținutul mesajelor pe
            care ni le trimiți prin formularul de contact.
          </li>
          <li>
            <strong>Date tehnice minime:</strong> informații necesare funcționării și securității
            (de ex. adresa IP la nivelul jurnalelor serverului și ale serviciului de găzduire).
          </li>
        </List>
        <p>
          Nu îți cerem și nu prelucrăm intenționat categorii speciale de date (de ex. date privind
          sănătatea, opiniile politice etc.).
        </p>
      </Section>

      <Section n={3} title="De ce prelucrăm datele și pe ce temei legal">
        <List>
          <li>
            <strong>Crearea și administrarea contului, furnizarea serviciului</strong> — temei:
            executarea contractului (art. 6 alin. 1 lit. b GDPR).
          </li>
          <li>
            <strong>Confirmarea adresei de email și securitatea contului</strong> — temei: interesul
            legitim de a proteja conturile și de a preveni abuzul (art. 6 alin. 1 lit. f), respectiv
            executarea contractului.
          </li>
          <li>
            <strong>Răspunsul la mesajele de contact</strong> — temei: interesul legitim de a
            răspunde solicitărilor tale (art. 6 alin. 1 lit. f).
          </li>
          <li>
            <strong>Îmbunătățirea platformei prin statistici agregate</strong> — temei: interesul
            legitim de a menține și dezvolta serviciul (art. 6 alin. 1 lit. f).
          </li>
          <li>
            <strong>Respectarea obligațiilor legale</strong> — temei: obligația legală (art. 6 alin.
            1 lit. c), atunci când este cazul.
          </li>
        </List>
      </Section>

      <Section n={4} title="Cât timp păstrăm datele">
        <p>
          Păstrăm datele de cont cât timp contul tău este activ. Dacă îți ștergi contul sau ne
          soliciți ștergerea, eliminăm datele asociate într-un termen rezonabil, cu excepția
          informațiilor pe care trebuie să le păstrăm dintr-o obligație legală sau pentru
          constatarea/apărarea unui drept. Mesajele de contact sunt păstrate atât cât este necesar
          pentru a-ți soluționa solicitarea.
        </p>
      </Section>

      <Section n={5} title="Cui divulgăm datele (persoane împuternicite)">
        <p>
          Nu vindem datele tale și nu le divulgăm în scopuri publicitare. Le putem încredința unor
          furnizori care ne ajută să operăm platforma, care prelucrează datele strict la instrucțiunile
          noastre:
        </p>
        <List>
          <li>
            <strong>Furnizorul de găzduire / infrastructură</strong> pe care rulează platforma și
            baza de date;
          </li>
          <li>
            <strong>Furnizorul de trimitere a emailurilor</strong> (pentru mesajele de confirmare și
            notificările contului).
          </li>
        </List>
        <p>
          Putem divulga date și autorităților competente, atunci când legea ne obligă. În măsura în
          care un furnizor prelucrează date în afara Spațiului Economic European, ne asigurăm că
          există garanții adecvate (de ex. clauze contractuale standard).
        </p>
        <p className="text-sm text-ink-muted">
          Notă pentru operator: completează aici, atunci când îi cunoști, numele concrete ale
          furnizorilor de găzduire și de email (și țara), pentru transparență deplină.
        </p>
      </Section>

      <Section n={6} title="Minori">
        <p>
          Platforma se adresează celor care se pregătesc pentru Bacalaureat. Conform Legii nr.
          190/2018, vârsta de la care un minor își poate da singur consimțământul pentru serviciile
          societății informaționale este de 16 ani. Dacă ai sub 16 ani, îți poți crea și folosi un
          cont numai cu acordul și sub supravegherea unui părinte sau reprezentant legal. Dacă aflăm
          că am colectat date de la un minor sub 16 ani fără un astfel de acord, le vom șterge.
        </p>
      </Section>

      <Section n={7} title="Drepturile tale">
        <p>Conform GDPR, ai următoarele drepturi:</p>
        <List>
          <li>dreptul de acces la datele tale;</li>
          <li>dreptul la rectificarea datelor inexacte sau incomplete;</li>
          <li>dreptul la ștergerea datelor („dreptul de a fi uitat”);</li>
          <li>dreptul la restricționarea prelucrării;</li>
          <li>dreptul la portabilitatea datelor;</li>
          <li>
            dreptul de a te opune prelucrării întemeiate pe interesul legitim, din motive legate de
            situația ta particulară;
          </li>
          <li>
            dreptul de a-ți retrage consimțământul oricând, atunci când prelucrarea se bazează pe
            consimțământ, fără a afecta legalitatea prelucrării anterioare.
          </li>
        </List>
        <p>
          Îți poți exercita aceste drepturi scriindu-ne la{" "}
          <a href={`mailto:${LEGAL.contactEmail}`} className="text-oxblood font-semibold hover:underline">
            {LEGAL.contactEmail}
          </a>
          . Îți vom răspunde în termenele prevăzute de lege (în principiu, în cel mult o lună).
        </p>
      </Section>

      <Section n={8} title="Dreptul de a depune o plângere">
        <p>
          Dacă apreciezi că prelucrarea datelor tale încalcă legea, ai dreptul să depui o plângere la
          autoritatea de supraveghere: {LEGAL.dpa.name},{" "}
          <a
            href={LEGAL.dpa.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-oxblood font-semibold hover:underline"
          >
            {LEGAL.dpa.url.replace("https://", "")}
          </a>
          .
        </p>
      </Section>

      <Section n={9} title="Cookie-uri și stocare locală">
        <p>
          Detaliile despre tehnologiile de stocare pe care le folosim se găsesc în{" "}
          <Link to="/cookies" className="text-oxblood font-semibold hover:underline">
            Politica de Cookies
          </Link>
          .
        </p>
      </Section>

      <Section n={10} title="Modificări ale acestei politici">
        <p>
          Putem actualiza această politică. Versiunea în vigoare este cea publicată pe această pagină,
          cu data „Ultima actualizare” de mai sus. Te încurajăm să o consulți periodic.
        </p>
      </Section>
    </LegalDoc>
  );
}
