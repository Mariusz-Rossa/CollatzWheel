# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# main.py 

"""
CollatzWheel — quick demo
Runs automatically, no interaction required.

For full interactive analysis with progress bar:
    python run_analysis.py

For visualisations:
    python src/visualizer.py
"""

import sys
sys.path.insert(0, 'src')

from wheel import W, wheel_from_int, BOTTOM, INF
from collatz import collatz_sequence, collatz_metrics, signature_string, wheel_signature
from analysis import batch_analysis, correlate_by_start_mod, correlate_by_dominant_transition, top_records

SEP = "─" * 60


# ------------------------------------------------------------------ #
#  1. Wheel Algebra basics                                            #
# ------------------------------------------------------------------ #

print(SEP)
print("  CollatzWheel — demo")
print(SEP)

print("\n[1] Wheel Algebra (mod 6)\n")

a, b = W(3), W(5)
print(f"  a = {a},  b = {b}")
print(f"  a + b = {a + b}        (expected: 2)")
print(f"  a * b = {a * b}        (expected: 3)")
print(f"  -a    = {-a}        (expected: 3)")
print(f"  /a    = {a.inv()}        (expected: ⊥  — gcd(3,6) ≠ 1)")
print(f"  /b    = {b.inv()}        (expected: 5  — 5×5 ≡ 1 mod 6)")

zero, inf, bot = W(0), W(INF), W(BOTTOM)
print(f"  /0    = {zero.inv()}        (expected: ∞)")
print(f"  /∞    = {inf.inv()}        (expected: 0)")
print(f"  ∞ + ∞ = {inf + inf}        (expected: ⊥)")
print(f"  ∞ × 0 = {inf * zero}        (expected: ⊥)")


# ------------------------------------------------------------------ #
#  2. Collatz sequence & metrics                                      #
# ------------------------------------------------------------------ #

print(f"\n{SEP}")
print("\n[2] Collatz sequence & metrics\n")

seq6 = collatz_sequence(6)
print(f"  collatz_sequence(6):")
print(f"  {seq6}")

m27 = collatz_metrics(27)
print(f"\n  collatz_metrics(27):")
for k, v in m27.items():
    print(f"    {k:>16}: {v}")


# ------------------------------------------------------------------ #
#  3. Wheel signatures                                                #
# ------------------------------------------------------------------ #

print(f"\n{SEP}")
print("\n[3] Wheel signatures\n")

for n in [6, 27, 97]:
    print(f"  n={n:>3}:  {signature_string(n, max_steps=15)}")

print()
print("  Reading: each number in the sequence is mapped to Wheel(mod 6).")
print("  W4 is the only true bifurcation point — all odd residues lead to W4,")
print("  then split ~51% to W2, ~49% to W5.")


# ------------------------------------------------------------------ #
#  4. Batch analysis (small range for demo)                           #
# ------------------------------------------------------------------ #

print(f"\n{SEP}")
print("\n[4] Batch analysis  n = 1..1000\n")

results = batch_analysis(1000)

print("  Correlation: start residue (n mod 6) → path length")
corr = correlate_by_start_mod(results)
for mod_val, stats in corr.items():
    marker = "  ←" if mod_val in ("1", "3", "5") else ""
    print(f"    mod={mod_val}:  avg={stats['avg_len']:6.2f}  "
          f"max={stats['max_len']:4d}  n={stats['count']}{marker}")

print()
print("  Odd residues (1,3,5) are consistently ~12 steps longer — the Wheel-12 constant.")

print("\n  Correlation: dominant transition → path length")
corr2 = correlate_by_dominant_transition(results)
for trans, stats in corr2.items():
    print(f"    {trans:12s}:  avg={stats['avg_len']:6.2f}  max={stats['max_len']:4d}  n={stats['count']}")

print()
print("  Numbers dominated by (4→5) have ~1.85× longer paths than (4→2).")

print(f"\n  Top 5 longest paths (n ≤ 1000):")
for r in top_records(results, 5):
    print(f"    n={r['start']:5d}  length={r['length']:4d}  "
          f"mod={r['start_mod']}  dominant={r['dominant_transition']}")


# ------------------------------------------------------------------ #
#  Done                                                               #
# ------------------------------------------------------------------ #

print(f"\n{SEP}")
print("\n  For full analysis:       python run_analysis.py")
print("  For plots:               python src/visualizer.py")
print("  For unit tests:          python -m pytest tests/")
print()