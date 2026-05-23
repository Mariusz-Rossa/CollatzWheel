# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# src/analysis.py
"""
Wheel × Collatz pattern analysis.

Main functions:
    transition_frequencies(n, mod)     → transition frequencies for a single number
    signature_profile(n, mod)          → signature profile (element distribution)
    batch_analysis(n_max, mod)         → analysis for n = 1..n_max
    find_correlations(results)         → correlation: signature → path length
    top_records(results, k)            → k numbers with the longest paths
"""

from __future__ import annotations
from collections import Counter, defaultdict
from collatz import (
    collatz_metrics,
    wheel_signature,
    signature_transitions,
)


# ------------------------------------------------------------------ #
# Single-number analysis                                             #
# ------------------------------------------------------------------ #

def transition_frequencies(n: int, mod: int = 6) -> Counter:
    """
    Counts transition frequencies (a→b) in the Wheel signature for n.    

    Example: Counter({(4,5): 12, (5,4): 11, ...})
    """
    return Counter(signature_transitions(n, mod))


def signature_profile(n: int, mod: int = 6) -> dict:
    """
    Full signature profile for number n.
    
    Returns:
        start_element   → first signature element (n mod 6)
        element_counts  → how many times each Wheel element appears
        top_transitions → 5 most frequent transitions
        unique_elements → number of distinct Wheel elements that appeared
    """
    sig   = wheel_signature(n, mod)
    trans = signature_transitions(n, mod)

    element_counts  = Counter(str(w) for w in sig)
    top_transitions = Counter(trans).most_common(5)

    return {
        "start_element":   str(sig[0]),
        "element_counts":  dict(element_counts),
        "top_transitions": top_transitions,
        "unique_elements": len(element_counts),
    }


# ------------------------------------------------------------------ #
# Batch analysis                                                     #
# ------------------------------------------------------------------ #

def batch_analysis(n_max: int, mod: int = 6) -> list[dict]:
    """
    Analyses all n = 1..n_max.
    
    Each record contains Collatz metrics + Wheel signature profile.
    """
    results = []
    for n in range(1, n_max + 1):
        metrics = collatz_metrics(n)
        sig     = wheel_signature(n, mod)
        trans   = signature_transitions(n, mod)
        freq    = Counter(trans)

        results.append({
            **metrics,
            "start_mod":        int(sig[0].value) if sig[0].is_regular() else str(sig[0].value),
            "dominant_transition": freq.most_common(1)[0] if freq else None,
            "unique_elements":  len(set(str(w) for w in sig)),
            "top_transitions":  freq.most_common(3),
        })
    return results


# ------------------------------------------------------------------ #
#  Correlations                                                       #
# ------------------------------------------------------------------ #

def correlate_by_start_mod(results: list[dict]) -> dict:
    """
    Groups results by start_mod (n mod 6) and computes average path length.

    Key question: do numbers with the same n mod 6 have similar path lengths?
    """
    groups: dict[str, list[int]] = defaultdict(list)
    for r in results:
        groups[str(r["start_mod"])].append(r["length"])

    return {
        mod_val: {
            "count":   len(lengths),
            "avg_len": round(sum(lengths) / len(lengths), 2),
            "max_len": max(lengths),
            "min_len": min(lengths),
        }
        for mod_val, lengths in sorted(groups.items())
    }


def correlate_by_dominant_transition(results: list[dict]) -> dict:
    """
    Groups by dominant transition and computes average path length.

    Key question: do numbers whose signature is dominated by transition (4→5) have longer paths?
    """
    groups: dict[str, list[int]] = defaultdict(list)
    for r in results:
        if r["dominant_transition"]:
            key = str(r["dominant_transition"][0])
            groups[key].append(r["length"])

    return {
        transition: {
            "count":   len(lengths),
            "avg_len": round(sum(lengths) / len(lengths), 2),
            "max_len": max(lengths),
        }
        for transition, lengths in sorted(groups.items())
    }


# ------------------------------------------------------------------ #
# Record holders                                                     #
# ------------------------------------------------------------------ #

def top_records(results: list[dict], k: int = 10) -> list[dict]:
    """
    Returns the k numbers with the longest Collatz paths.    
    """
    return sorted(results, key=lambda r: r["length"], reverse=True)[:k]


# ------------------------------------------------------------------ #
#  Smoke-test                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("=== Analysis — smoke test (n = 1..1000) ===\n")

    results = batch_analysis(1000)

    print("KCorrelation: start_mod (n mod 6) → path length:")
    corr = correlate_by_start_mod(results)
    for mod_val, stats in corr.items():
        print(f"  mod={mod_val}: avg={stats['avg_len']:6.2f}  "
              f"max={stats['max_len']:4d}  n={stats['count']}")

    print()

    print("Correlation: dominant_transition → path length:")
    corr2 = correlate_by_dominant_transition(results)
    for trans, stats in corr2.items():
        print(f"  {trans:12s}: avg={stats['avg_len']:6.2f}  max={stats['max_len']:4d}  n={stats['count']}")

    print()

    print("Top 10 longest paths (n ≤ 1000):")
    for r in top_records(results, 10):
        print(f"  n={r['start']:5d}  length={r['length']:4d}  "
              f"start_mod={r['start_mod']}  "
              f"dominant={r['dominant_transition']}")