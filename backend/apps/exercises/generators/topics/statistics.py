"""Statistics — single-item class (spec §7.3 statistics). M3 only.

  d1: arithmetic mean / median of given data.
  d2: determine a value so a small data set has a target mean.
All values computed exactly with sympy (Rational), never floats (§13.3).
"""
from __future__ import annotations

import sympy as sp

from ..base import ExerciseGenerator

a = sp.Symbol("a", real=True)


def _l(expr) -> str:
    return sp.latex(expr)


class StatisticsGenerator(ExerciseGenerator):
    TOPIC_CODE = "statistics"
    SUPPORTED_PROFILES = ["pedagogic"]

    def _generate_params(self) -> dict:
        rng = self.rng
        if self.difficulty == 1:
            pool = [self._st_mean, self._st_median, self._st_mode, self._st_range]
        elif self.difficulty == 2:
            pool = [self._st_find_for_mean, self._st_mean, self._st_freq_mean, self._st_mode]
        else:
            pool = [self._st_find_for_mean, self._st_freq_mean, self._st_range, self._st_median]
        return rng.choice(pool)()

    def _compute_answer(self, params):
        return params.get("answer")

    def _validate(self, params, answer) -> bool:
        return params.get("ok", True) and len(params["answer_latex"]) < 200

    def _build_question(self, params):
        return params["question"]

    def _build_answer_latex(self, params, answer):
        return params["answer_latex"]

    def _build_hint(self, params):
        return params.get("hint", "")

    def _build_steps(self, params):
        return params.get("steps", [])

    # --- subtypes ------------------------------------------------------------
    def _st_mean(self):
        rng = self.rng
        count = rng.choice([5, 6])
        data = [rng.randint(1, 12) for _ in range(count)]
        mean = sp.Rational(sum(data), count)
        data_l = ",\\ ".join(str(d) for d in data)
        return {
            "question": rf"Se consideră valorile ${data_l}$. Calculați media aritmetică a "
                        rf"acestor valori.",
            "answer_latex": rf"$\overline{{x}} = {_l(mean)}$",
            "answer": mean,
            "hint": r"Media aritmetică este suma valorilor împărțită la numărul lor.",
            "steps": [rf"$\overline{{x}} = \dfrac{{{sum(data)}}}{{{count}}} = {_l(mean)}$"],
            "ok": True,
        }

    def _st_median(self):
        rng = self.rng
        count = rng.choice([5, 7])           # odd → median is a single middle value
        data = sorted(rng.randint(1, 15) for _ in range(count))
        med = data[count // 2]
        data_l = ",\\ ".join(str(d) for d in data)
        return {
            "question": rf"Se consideră valorile ordonate crescător ${data_l}$. Determinați "
                        rf"mediana acestui set de date.",
            "answer_latex": rf"$M_e = {med}$",
            "answer": sp.Integer(med),
            "hint": r"Mediana unui set ordonat cu un număr impar de valori este valoarea "
                    r"din mijloc.",
            "steps": [rf"$M_e = {med}$"],
            "ok": True,
        }

    def _st_mode(self):
        rng = self.rng
        m = rng.randint(2, 9)
        others = rng.sample([v for v in range(1, 13) if v != m], rng.choice([3, 4]))
        data = [m, m, m] + others                     # m appears 3× ⇒ unique mode
        rng.shuffle(data)
        data_l = ",\\ ".join(str(d) for d in data)
        return {
            "question": rf"Se consideră valorile ${data_l}$. Determinați modulul (valoarea "
                        rf"cu cea mai mare frecvență) al acestui set de date.",
            "answer_latex": rf"$M_o = {m}$",
            "answer": sp.Integer(m),
            "hint": r"Modulul este valoarea care apare de cele mai multe ori.",
            "steps": [rf"$M_o = {m}$"],
            "ok": True,
        }

    def _st_range(self):
        rng = self.rng
        data = [rng.randint(1, 20) for _ in range(rng.choice([5, 6]))]
        if len(set(data)) < 2:
            raise ValueError("degenerate")
        amp = max(data) - min(data)
        data_l = ",\\ ".join(str(d) for d in data)
        return {
            "question": rf"Se consideră valorile ${data_l}$. Determinați amplitudinea "
                        rf"acestui set de date.",
            "answer_latex": rf"$A = {amp}$",
            "answer": sp.Integer(amp),
            "hint": r"Amplitudinea este diferența dintre valoarea maximă și cea minimă.",
            "steps": [rf"$A = {max(data)} - {min(data)} = {amp}$"],
            "ok": True,
        }

    def _st_freq_mean(self):
        rng = self.rng
        vals = sorted(rng.sample(range(1, 10), 3))
        freqs = [rng.randint(1, 4) for _ in vals]
        total = sum(freqs)
        s = sum(v * f for v, f in zip(vals, freqs))
        mean = sp.Rational(s, total)
        tbl = ",\\ ".join(rf"{v}\ (\text{{de }} {f}\ \text{{ori}})" for v, f in zip(vals, freqs))
        return {
            "question": rf"Într-un set de date valorile apar astfel: ${tbl}$. Calculați media "
                        rf"aritmetică a datelor.",
            "answer_latex": rf"$\overline{{x}} = {_l(mean)}$",
            "answer": mean,
            "hint": r"Media ponderată: $\overline{x} = \dfrac{\sum v_i n_i}{\sum n_i}$.",
            "steps": [rf"$\overline{{x}} = \dfrac{{{s}}}{{{total}}} = {_l(mean)}$"],
            "ok": True,
        }

    def _st_find_for_mean(self):
        rng = self.rng
        k1, k2 = rng.randint(1, 5), rng.randint(2, 6)
        target = rng.randint(3, 9)
        # mean of a, a+k1, a+k2 equals target → solve for a
        sol = sp.solve(sp.Eq((a + (a + k1) + (a + k2)) / 3, target), a)[0]
        return {
            "question": rf"Determinați numărul real $a$ pentru care media aritmetică a "
                        rf"numerelor $a$, $a + {k1}$ și $a + {k2}$ este egală cu ${target}$.",
            "answer_latex": rf"$a = {_l(sol)}$",
            "answer": sol,
            "hint": r"Scrieți media celor trei numere și egalați-o cu valoarea dată.",
            "steps": [rf"$\dfrac{{a + (a+{k1}) + (a+{k2})}}{{3}} = {target}$",
                      rf"$a = {_l(sol)}$"],
            "ok": True,
        }
