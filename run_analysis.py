# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# run_analysis.py

import sys
import time
sys.path.insert(0, 'src')

from collections import Counter
from collatz import collatz_metrics, wheel_signature, signature_transitions
from analysis import correlate_by_start_mod, correlate_by_dominant_transition, top_records


def batch_analysis_progress(n_max: int) -> list[dict]:
    """batch_analysis with progress bar."""
    results = []
    start_time = time.time()

    for n in range(1, n_max + 1):
        metrics = collatz_metrics(n)
        sig     = wheel_signature(n)
        trans   = signature_transitions(n)
        freq    = Counter(trans)

        results.append({
            **metrics,
            "start_mod":           int(sig[0].value) if sig[0].is_regular() else str(sig[0].value),
            "dominant_transition": freq.most_common(1)[0] if freq else None,
            "unique_elements":     len(set(str(w) for w in sig)),
            "top_transitions":     freq.most_common(3),
        })

        if n % max(1, n_max // 200) == 0 or n == n_max:
            elapsed  = time.time() - start_time
            pct      = n / n_max
            eta      = (elapsed / pct) * (1 - pct) if pct > 0 else 0
            bar_done = int(pct * 40)
            bar      = "█" * bar_done + "░" * (40 - bar_done)
            speed    = n / elapsed if elapsed > 0 else 0

            sys.stdout.write(
                f"\r  [{bar}] {pct*100:5.1f}%  "
                f"{n:>{len(str(n_max))}}/{n_max}  "
                f"{speed:,.0f} n/s  "
                f"ETA: {eta:4.0f}s  "
            )
            sys.stdout.flush()

    elapsed = time.time() - start_time
    sys.stdout.write(f"\r  [{'█'*40}] 100.0%  {n_max}/{n_max}  "
                     f"done in {elapsed:.1f}s{' '*20}\n")
    sys.stdout.flush()
    return results


print("=== Collatz × Wheel — Analysis ===\n")

while True:
    try:
        n_max = int(input("Enter range n (e.g. 100000, 0 = quit): "))
    except ValueError:
        print("  Please enter an integer.\n")
        continue

    if n_max == 0:
        print("Goodbye!")
        break

    if n_max < 1:
        print("  n must be > 0.\n")
        continue

    print(f"\nLComputing for n = 1..{n_max:,}...\n")
    results = batch_analysis_progress(n_max)

    print("\nCorrelation: start_mod → path length:")
    corr = correlate_by_start_mod(results)
    for mod_val, stats in corr.items():
        print(f"  mod={mod_val}: avg={stats['avg_len']:7.2f}  max={stats['max_len']:5d}  n={stats['count']}")

    print("\nKCorrelation: dominant_transition → path length:")
    corr2 = correlate_by_dominant_transition(results)
    for trans, stats in corr2.items():
        print(f"  {trans:12s}: avg={stats['avg_len']:7.2f}  max={stats['max_len']:5d}  n={stats['count']}")

    print(f"\nTop 10 longest paths (n ≤ {n_max:,}):")
    for r in top_records(results, 10):
        print(f"  n={r['start']:7d}  length={r['length']:4d}  "
              f"start_mod={r['start_mod']}  dominant={r['dominant_transition']}")

    print("\n" + "─" * 60 + "\n")