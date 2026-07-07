# BAC Matematică M2 (M_tehnologic) 2020–2026 — Kit de descărcare

## De ce nu ți-am trimis direct un .zip cu PDF-urile?

Am indexat integral pro-matematica.ro pentru anii 2020–2026 și am identificat toate
cele **136 de fișiere oficiale** (subiecte + bareme) pentru profilul **M_tehnologic**:
sesiuni oficiale, rezerve, sesiune specială, simulări clasa a XII-a, modele, și
seturile de teste de antrenament din 2020/2021 (singurii ani cu teste publicate
pe acel site; 2022 nu are teste).

Mediul meu de lucru poate accesa internetul doar printr-un instrument de căutare/citire
web care extrage *textul* dintr-un PDF, nu fișierul original — și nu are voie să se
conecteze direct la pro-matematica.ro pentru a descărca fișiere brute. Din acest motiv
nu pot genera eu însumi un .zip cu PDF-urile originale.

## Ce conține acest kit
- **`download_bac_m2_tehnologic.sh`** — script bash care descarcă toate cele 136 de
  fișiere direct de pe pro-matematica.ro, le organizează pe ani/sesiuni, și le
  arhivează automat într-un singur `.zip`.
- **`LINKS_BAC_M2_Tehnologic_2020-2026.md`** — lista completă a linkurilor directe,
  organizată pe ani, pentru descărcare manuală (click cu click) dacă preferi asta.

## Cum rulezi scriptul

**Mac / Linux:**
```bash
chmod +x download_bac_m2_tehnologic.sh
./download_bac_m2_tehnologic.sh
```

**Windows:** instalează Git Bash (vine cu Git for Windows) sau folosește WSL, apoi
rulează comenzile de mai sus. Scriptul are nevoie de `curl` și `zip` (ambele incluse
în Git Bash / WSL).

La final vei avea `BAC_Matematica_M2_Tehnologic_2020-2026.zip` cu tot conținutul,
organizat astfel:
```
BAC_Matematica_M2_Tehnologic/
  2020/Sesiunea_I_24_iunie/...
  2020/Sesiunea_Speciala_7_iulie/...
  2020/Sesiunea_II_25_august/...
  2020/Teste/...
  2020/Model/...
  2021/... (+ Sesiunea_I_Rezerva, Simulare_XII)
  2022/...
  2023/... (+ Sesiunea_II_Rezerva)
  2024/... (+ Sesiunea_II_Rezerva)
  2025/...
  2026/... (+ Sesiunea_I_Rezerva)
```

Dacă vreo descărcare eșuează (server temporar indisponibil), rulează scriptul din nou —
fișierele deja descărcate sunt sărite automat, deci va relua doar ce a lipsit.
