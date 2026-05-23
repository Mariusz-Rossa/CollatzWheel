# Changelog

All notable changes to this project will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-05-23

Initial public release.

### Added
- `src/wheel.py` — Wheel Algebra (Carlström 2004) implementation
  - `WheelElement` class with total operations: `+`, `×`, `-`, `/`, `inv()`
  - Special elements `⊥` (bottom) and `∞` (infinity)
  - Factory functions `W()` and `wheel_from_int()`
- `src/collatz.py` — Collatz sequences and Wheel signatures
  - `collatz_sequence()`, `collatz_metrics()`
  - `wheel_signature()`, `signature_string()`, `signature_transitions()`
- `src/analysis.py` — batch analysis and correlations
  - `batch_analysis()`, `correlate_by_start_mod()`, `correlate_by_dominant_transition()`, `top_records()`
- `src/visualizer.py` — visualisations (heatmaps, scatter plots, path plots)
- `main.py` — non-interactive demo
- `run_analysis.py` — interactive CLI with progress bar
- `tests/test_wheel.py` — 73 unit tests covering Carlström axioms and Collatz properties

### Empirical findings (n ≤ 1,000,000)
- Wheel-12 constant: odd residues mod 6 have ~12 longer paths than even residues
- W4 identified as the sole bifurcation point in Wheel(mod 6)
- Bifurcation ratio ~1.85× between W4→W5 and W4→W2 dominated paths
- All record-length paths have dominant transition (4→5) or (5→4)

---

## [Unreleased]

### Planned
- Analysis for n ≤ 100,000,000
- Wheel(mod 12) and Wheel(mod 30) exploration
- Formal statement of empirical findings
- Preprint (Zenodo / arXiv)