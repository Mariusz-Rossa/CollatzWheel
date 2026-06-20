# Changelog

All notable changes to this project will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- Wheel(mod 30) analysis - Phase 1+2 (issue #3)
- Algebraic explanation for Wheel constants (issue #4, update)
- Jupyter notebook: exploration.ipynb (issue #8)
- Option C: ⊥ and ∞ as active sequence elements (v2.0, issue #5)
- Formal statement of empirical findings
- Preprint (Zenodo / arXiv)

---

## [1.1.0-rc1] - 2026-06-20

### Analysis Extended

#### Wheel(mod 12) Analysis Complete (issue #2)
- Completed analysis up to n ≤ 250,000,000
- **Discovered Wheel-25 constant:** Numbers show ~25-step delta between shortest and longest paths
  - Residues {0,4,8} (multiples of 4): avg = 176.31 steps (shortest)
  - Residues {3,7,11}: avg = 201.24 steps (longest)
  - Delta = 24.93 ≈ 2× mod 6's Wheel-12 constant (~12.5)
- **Delta stability confirmed:** Δ ≈ 24.7–24.9 across all scales (1M → 250M)
- **Bifurcation point W10 identified:** Different from W4 in mod 6
  - (10→11): avg = 242.67 steps, n = 79.4M paths (67.4%)
  - (10→5): avg = 185.01 steps, n = 21.5M paths (18.3%)
  - (4→2): avg = 190.32 steps (secondary transition)
  - (4→8): avg = 120.88 steps (new equal branch, ~equal to (4→2))
- **Bifurcation asymptote differs:** Converges to ~1.27-1.28× (vs mod 6's ~1.612×)
  - Ratio decreases as scales grow: 1.303× → 1.281× → 1.275×
  - Suggests convergence to different asymptote than mod 6
- **Top 10 record holders:** All dominated by (10→11)/(11→10)
  - 5 records with (10→11), 5 with (11→10)
  - **Zero** (4→5)/(5→4) representation (contrast: mod 6 had all)
  - Max length: 956 steps (n=226,588,897)
- **Pattern discovered:** Multiples of 4 are systematically shortest
  - {0,4,8} ≡ 0 (mod 4) correlates with shortest paths
  - Suggests algebraic structure related to divisibility by 4 (mod 12 = 2²×3)

#### Computational Performance
- Confirmed chunked processing efficiency
  - 50 chunks of 5M each
  - Total runtime: ~152,625 seconds (~42 hours wall-clock)
  - Memory: Stable, no OOM
- Validated for large-scale analysis (n > 100M)

#### Research Direction
- **Scaling hypothesis proposed:** Δ(mod m) ≈ Δ(mod 6) × (m/6)
  - Mod 6: Δ ≈ 12.5 (verified to 250M) ✓
  - Mod 12: Δ ≈ 25.0 (verified to 250M) ✓
  - Mod 30: Δ ≈ 62.5 (predicted, to be tested in issue #3)
- **Bifurcation asymptote decreases:** Mod 6 ~1.612× → Mod 12 ~1.275×
  - Pattern suggests further decrease for mod 30
  - Possible convergence toward 1.0 as mod increases

### Documentation
- Updated `instrukcja.md` (v1.3) with mod 12 findings and comparative tables
- Updated `issues.md` (v2.1) with closed/open/updated issue status
- Expanded "Wyniki badawcze" section with complete mod 12 data tables
- Added comparison tables: mod 6 vs mod 12 at all scales

### GitHub Issues
- **Closed:** Issue #2 (Wheel mod 12 exploration) - 2026-06-20
  - Full analysis up to 250M with all findings documented
- **Opened:** Issue #3 (Wheel mod 30 exploration) - 2026-06-20
  - Outlined scaling hypothesis and research plan
  - Three-phase approach: Phase 1 (10M, ~3h), Phase 2 (100M, ~20h), Phase 3 (250M, ~50h)
- **Updated:** Issue #4 (Algebraic explanation) - 2026-06-20
  - Scope expanded: original Wheel-12 + bifurcation ratio now complemented by Wheel-25 and different asymptote
  - Remains open for continued investigation after issue #3 results

---

## [1.0.0] - 2026-05-23

Initial public release.

### Added
- `src/wheel.py` - Wheel Algebra (Carlström 2004) implementation
  - `WheelElement` class with total operations: `+`, `×`, `-`, `/`, `inv()`
  - Special elements `⊥` (bottom) and `∞` (infinity)
  - Factory functions `W()` and `wheel_from_int()`
- `src/collatz.py` - Collatz sequences and Wheel signatures
  - `collatz_sequence()`, `collatz_metrics()`
  - `wheel_signature()`, `signature_string()`, `signature_transitions()`
  - Support for configurable modulus (mod parameter)
- `src/analysis.py` - batch analysis and correlations
  - `batch_analysis()`, `correlate_by_start_mod()`, `correlate_by_dominant_transition()`, `top_records()`
  - Support for configurable modulus
- `src/visualizer.py` - visualisations (heatmaps, scatter plots, path plots)
  - Dark theme for accessibility
  - Support for configurable modulus
- `main.py` - non-interactive demo
- `run_analysis.py` - interactive CLI with progress bar
  - Chunked processing for n > 5M (no OOM)
  - Support for configurable modulus
- `tests/test_wheel.py` - 73 unit tests covering Carlström axioms and Collatz properties
- `CONTRIBUTING.md` - contribution guidelines (JOSS requirement)
- `CHANGELOG.md` - version history (JOSS requirement)
- `README.md` - English documentation with DOI badge
- `LICENSE` (MIT)
- `.gitignore`

### Empirical findings (n ≤ 250,000,000)

#### Wheel(mod 6)
- **Wheel-12 constant:** Odd residues mod 6 have ~12.5 longer paths than even residues
  - Verified stable from n≤100M to n≤250M
- **W4 bifurcation point:** Only true choice point in Collatz sequence under mod 6
  - All odd residues {1,3,5} deterministically map to W4
  - W4 splits ~51% to W2, ~49% to W5
- **Bifurcation ratio ~1.612×:** (4→5) vs (4→2) transitions
  - Converges to asymptote: ~2.04× (100k) → 1.612× (250M)
  - Visible asymptote from n ≤ 200M
- **Record-length predictor:** All top-10 paths dominated by (4→5)/(5→4)
  - Confirmed across all 8 tested scales

#### Wheel(mod 12) [NEW]
- **Wheel-25 constant:** ~25-step delta between longest and shortest residues
  - {0,4,8} shortest: 176.31 avg
  - {3,7,11} longest: 201.24 avg
  - Exactly 2× mod 6's delta
- **W10 bifurcation point:** Different topology than W4
  - (10→11) dominates with 242.67 avg
  - (4→8) is now equal to (4→2) (unlike mod 6)
- **Bifurcation ratio ~1.275×:** Different asymptote than mod 6
  - Decreases with scale: 1.303× → 1.275×
  - Suggests convergence to different limit
- **Top records:** 100% (10→11)/(11→10), no (4→5)/(5→4)
- **Pattern:** Multiples of 4 are shortest (algebraic structure)

### Architecture & Code Quality
- Clean modular design: wheel.py, collatz.py, analysis.py, visualizer.py
- Type hints throughout
- Comprehensive docstrings
- 73 unit tests with 100% pass rate
- Tested on Python 3.12+ (Mac M4)
- No external dependencies beyond numpy, matplotlib, networkx

### Project Management
- Public GitHub repository
- Zenodo DOI: 10.5281/zenodo.20355730
- arXiv account prepared (submission Oct 2026)
- JOSS submission planned: Jan 2027
- Semantic versioning from day one
- Clean commit history with descriptive messages

---

## Version History Summary

| Version | Date | Focus | Scale | Status |
|---------|------|-------|-------|--------|
| 1.0.0 | 2026-05-23 | Foundation, mod 6 | 1M–250M | Release |
| 1.1.0-rc1 | 2026-06-20 | Mod 12 exploration, mod 30 planning | 250M (mod 6+12) | RC |
| 1.1.0 | 2026-07 (planned) | Mod 30 Phase 1+2 complete | 100M (mod 30) | TBD |
| 1.2.0 | 2026-09 (planned) | Algebraic insights, preprint | All mods | TBD |
| 2.0.0 | 2027-01 (planned) | JOSS release | Complete | TBD |

---

## Key Milestones

- **2026-05-23:** Initial public release (v1.0.0)
- **2026-06-10:** Issue #1 closed (250M analysis), Issue #7 closed (configurable modulus)
- **2026-06-20:** Issue #2 closed (mod 12 to 250M), Issue #3 opened (mod 30), Issue #4 updated
- **2026-07:** Target - Wheel(mod 30) Phase 1+2 complete (issue #3)
- **2026-09:** Target - Algebraic explanation draft (issue #4 update), preprint v0.1
- **2026-10:** Target - paper.md skeleton for JOSS
- **2027-01:** Target - JOSS submission

---

## Breaking Changes

None in this release. Backward compatibility maintained throughout.

---

## Security

No known security issues. MIT licensed, open source.

---

## Credits

- **Author:** Mariusz "Vidi" Rossa (independent researcher)
- **ORCID:** 0009-0006-1060-2883
- **Mathematical foundation:** Carlström, J. (2004) "Wheels - On Division by Zero"
- **AI assistance:** Claude (Anthropic) for code structure, documentation, and technical writing

---

## References

- Carlström, J. (2004). *Wheels - On Division by Zero*. Mathematical Structures in Computer Science, 14(1), 143–184.
- Tao, T. (2019). *Almost all orbits of the Collatz map attain almost bounded values*. arXiv:1909.03562.
- OEIS A006577 - Number of halving and tripling steps to reach 1.
- Meyenburg (2025). *Meyenburg Algebra and the Mass Gap*. IJMTT 71(10), 29–35.

---

*Last updated: 2026-06-20 | Maintained by Mariusz Rossa*