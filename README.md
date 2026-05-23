# CollatzWheel

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20355730.svg)](https://doi.org/10.5281/zenodo.20355730)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)

**Exploring the Collatz conjecture through the lens of Wheel Algebra.**

Instead of the standard mod-2 view (even/odd), this project maps Collatz sequences onto **Wheel(mod 6)** — an algebraic system where `0/0` and `1/0` are valid elements, not errors. The goal is to find algebraic patterns ("Wheel signatures") that correlate with sequence behaviour, particularly path length.

---

## Background

### The Collatz Conjecture

Take any positive integer. If even → divide by 2. If odd → multiply by 3 and add 1. Repeat. The conjecture states you always reach 1 — but no one has proved it. Verified empirically up to 2⁶⁸.

### Wheel Algebra

Wheel Algebra (Carlström 2004) extends the rationals with two special elements:
- `⊥` (bottom) = `0/0` — undefined
- `∞` = `1/0` — infinity

All operations are **total** — no exceptions, no undefined behaviour. This makes it well-suited for algebraic exploration of sequences that pass through zero or diverge.

### Our angle

Mapping Collatz sequences onto Wheel(mod 6) yields 8 possible states: `{0, 1, 2, 3, 4, 5, ⊥, ∞}`. Each step in the sequence becomes a transition between states. We call the resulting sequence of states a **Wheel signature**.

---

## Empirical findings (as of May 2026, n ≤ 1,000,000)

**Finding 1 — The Wheel-12 constant.**
Numbers with `n ≡ 1, 3, 5 (mod 6)` have paths ~12 steps longer on average than `n ≡ 0, 2, 4 (mod 6)`. This gap is stable across all tested ranges.

```
n ≤ 1M:    odd residues: avg ≈ 137   |   even residues: avg ≈ 125   |   Δ ≈ 12
n ≤ 100k:  odd residues: avg ≈ 113   |   even residues: avg ≈ 101   |   Δ ≈ 12
```

**Finding 2 — W4 as the bifurcation point.**
W4 is the only true choice point in the Collatz sequence under Wheel(mod 6). All odd residues (mod 1, 3, 5) deterministically map to W4 (probability = 1.00). From W4, the sequence goes to W2 (~51%) or W5 (~49%).

**Finding 3 — The bifurcation ratio ~1.85.**
Numbers whose signatures are dominated by the W4→W5 transition have paths ~1.85× longer than those dominated by W4→W2:

```
n ≤ 1M:   (4→5): avg = 173   |   (4→2): avg = 94   |   ratio = 1.84×
n ≤ 500k: (4→5): avg = 165   |   (4→2): avg = 88   |   ratio = 1.88×
```

**Finding 4 — Record predictor.**
All top-10 longest paths in every tested range have `dominant = (4→5)` or `(5→4)`.

These are empirical observations. Algebraic proofs are the subject of ongoing work.

---

## Installation

```bash
git clone https://github.com/Mariusz-Rossa/CollatzWheel.git
cd CollatzWheel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

```bash
# Quick demo — runs automatically, no interaction needed
python main.py

# Interactive analysis with progress bar (choose your own range)
python run_analysis.py

# Generate all plots (saves to data/results/)
python src/visualizer.py

# Unit tests
python -m pytest tests/
```

### Demo output

```
────────────────────────────────────────────────────────────
  CollatzWheel — demo
────────────────────────────────────────────────────────────

[1] Wheel Algebra (mod 6)

  a = 3,  b = 5
  a + b = 2        (expected: 2)
  a * b = 3        (expected: 3)
  -a    = 3        (expected: 3)
  /a    = ⊥        (expected: ⊥  — gcd(3,6) ≠ 1)
  /b    = 5        (expected: 5  — 5×5 ≡ 1 mod 6)
  /0    = ∞        (expected: ∞)
  /∞    = 0        (expected: 0)
  ∞ + ∞ = ⊥        (expected: ⊥)
  ∞ × 0 = ⊥        (expected: ⊥)

────────────────────────────────────────────────────────────

[2] Collatz sequence & metrics

  collatz_sequence(6):
  [6, 3, 10, 5, 16, 8, 4, 2, 1]

  collatz_metrics(27):
               start: 27
              length: 111
           max_value: 9232
      max_value_step: 77
          even_steps: 70
           odd_steps: 41
          even_ratio: 0.6306...

────────────────────────────────────────────────────────────

[3] Wheel signatures

  n=  6:  0→3→4→5→4→2→4→2→1
  n= 27:  3→4→5→4→2→1→4→5→4→5→4→5→4→5→4→... (97 więcej)
  n= 97:  1→4→2→1→4→2→1→4→5→4→5→4→2→4→5→... (104 więcej)

────────────────────────────────────────────────────────────

[4] Batch analysis  n = 1..1000

  Correlation: start residue (n mod 6) → path length
    mod=0:  avg= 52.07  max= 144  n=166
    mod=1:  avg= 68.64  max= 178  n=167  ←
    mod=2:  avg= 53.37  max= 142  n=167
    mod=3:  avg= 63.65  max= 147  n=167  ←
    mod=4:  avg= 54.42  max= 142  n=167
    mod=5:  avg= 65.10  max= 142  n=166  ←

  Odd residues (1,3,5) are consistently ~12 steps longer — the Wheel-12 constant.

  Top 5 longest paths (n ≤ 1000):
    n=  871  length= 178  mod=1  dominant=((4, 5), 45)
    n=  937  length= 173  mod=1  dominant=((4, 5), 44)
    n=  703  length= 170  mod=1  dominant=((4, 5), 44)
    n=  763  length= 152  mod=1  dominant=((4, 5), 35)
    n=  775  length= 152  mod=1  dominant=((4, 5), 37)
```

---

## Project structure

```
collatz-wheel/
├── src/
│   ├── wheel.py        # Wheel Algebra — WheelElement class + operations
│   ├── collatz.py      # Sequences, metrics, Wheel signatures
│   ├── analysis.py     # Pattern analysis, correlations, batch processing
│   └── visualizer.py   # Plots: heatmaps, scatter, path visualisation
├── tests/
│   └── test_wheel.py   # Unit tests — Carlström axioms + Collatz properties
├── main.py             # Quick demo — no interaction required
├── run_analysis.py     # Interactive CLI with progress bar
├── data/results/       # Output plots (PNG)
├── requirements.txt
└── README.md
```

---

## Roadmap

- [x] Wheel Algebra implementation (Carlström 2004)
- [x] Collatz sequences, metrics, Wheel signatures
- [x] Batch analysis and correlation discovery (n ≤ 1,000,000)
- [x] Visualisation (heatmaps, scatter plots, path plots)
- [x] Unit tests (73 tests, Carlström axioms)
- [ ] Analysis for n ≤ 100,000,000
- [ ] Wheel(mod 12) and Wheel(mod 30) exploration
- [ ] Formal statement of empirical findings
- [ ] Preprint (Zenodo)

---

## References

- Carlström, J. (2004). *Wheels — On Division by Zero*. Mathematical Structures in Computer Science, 14(1), 143–184.
- Tao, T. (2019). *Almost all orbits of the Collatz map attain almost bounded values*. arXiv:1909.03562.
- OEIS A006577 — Number of halving and tripling steps to reach 1. https://oeis.org/A006577

---

## 🔗 Related Projects

- [WheelPhysics](https://github.com/Mariusz-Rossa/WheelPhysics) — Wheel Algebra applied to singularities in theoretical physics (DOI: [10.5281/zenodo.20305458](https://doi.org/10.5281/zenodo.20305458))
- [ThreeBody](https://github.com/Mariusz-Rossa/ThreeBody) — Framework for numerical simulation and statistical analysis of hierarchical three-body gravitational system (DOI: [10.5281/zenodo.20356331](https://doi.org/10.5281/zenodo.20356331))

---

## 👤 Author

**Mariusz Rossa** — independent researcher  
ORCID: [0009-0006-1060-2883](https://orcid.org/0009-0006-1060-2883)

---

## License

MIT — see [LICENSE](LICENSE).

---

*Independent research project.*