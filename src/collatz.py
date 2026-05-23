# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# src/collatz.py

"""
Collatz sequences + dynamic Wheel signatures.

Main functions:
    collatz_sequence(n)      → full sequence from n to 1
    collatz_metrics(n)       → metrics dictionary
    wheel_signature(n, mod)  → Wheel signature (list of WheelElement)
    signature_string(n, mod) → signature as a readable string ex. "3→4→5→2"
"""

from __future__ import annotations
from wheel import WheelElement, wheel_from_int


# ------------------------------------------------------------------ #
# Collatz sequence                                                   #
# ------------------------------------------------------------------ #

def collatz_sequence(n: int) -> list[int]:
    """
    Returns the full Collatz sequence from n down to 1 (inclusive).    
    
    Example: collatz_sequence(6) → [6, 3, 10, 5, 16, 8, 4, 2, 1]
    """
    if n < 1:
        raise ValueError(f"n must be a positive integer, got: {n}")

    seq = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        seq.append(n)
    return seq


# ------------------------------------------------------------------ #
# Metrics                                                            #
# ------------------------------------------------------------------ #

def collatz_metrics(n: int) -> dict:
    """
    Returns a metrics dictionary for starting number n.    
    
    Keys::
        start          → starting number
        length         → path length (number of steps to reach 1)
        max_value      → maximum value in the sequence
        max_value_step → step at which the maximum occurs
        even_steps     → number of even steps n → n/2
        odd_steps      → number of odd steps n → 3n+1
        even_ratio     → fraction of even steps (0.0 – 1.0)
    """
    seq = collatz_sequence(n)
    steps = len(seq) - 1 

    even_steps = sum(1 for x in seq[:-1] if x % 2 == 0)
    odd_steps  = steps - even_steps

    max_val  = max(seq)
    max_step = seq.index(max_val)

    return {
        "start":          n,
        "length":         steps,
        "max_value":      max_val,
        "max_value_step": max_step,
        "even_steps":     even_steps,
        "odd_steps":      odd_steps,
        "even_ratio":     even_steps / steps if steps > 0 else 0.0,
    }


# ------------------------------------------------------------------ #
# Dynamic Wheel signature ← core of the project                      #
# ------------------------------------------------------------------ #

def wheel_signature(n: int, mod: int = 6) -> list[WheelElement]:
    """
    Maps each element of the Collatz sequence onto Wheel(mod).    
    
    Example for n=27, mod=6:
        sequence:  [27, 82, 41, 124, ...]
        signature:  [W3, W4, W5, W4, ...]
    """
    seq = collatz_sequence(n)
    return [wheel_from_int(x, mod) for x in seq]


def signature_string(n: int, mod: int = 6, max_steps: int = 20) -> str:
    """
    Signature as a readable string, optionally truncated.      
    
    Example: "3→4→5→4→2→0→1→2→1"
    """
    sig = wheel_signature(n, mod)
    truncated = sig[:max_steps]
    result = "→".join(str(w) for w in truncated)
    if len(sig) > max_steps:
        result += f"→... ({len(sig) - max_steps} more)"
    return result


def signature_transitions(n: int, mod: int = 6) -> list[tuple[int | str, int | str]]:
    """
    Returns a list of transitions (a → b) in the Wheel signature.
    Useful for pattern search: which transitions occur most often?
    
    Example: [(3,4), (4,5), (5,4), ...]
    """
    sig = wheel_signature(n, mod)
    return [(sig[i].value, sig[i+1].value) for i in range(len(sig)-1)]


# ------------------------------------------------------------------ #
#  Smoke-test                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("=== Collatz + Wheel Signatures — smoke test ===\n")

    print("Sequence for n=6:")
    print(collatz_sequence(6))
    print()

    print("Metrics for n=27 (a well-known hard case):")
    m = collatz_metrics(27)
    for k, v in m.items():
        print(f"  {k:>16}: {v}")
    print()

    print("Wheel signature for n=27 (mod 6, first 20 steps):")
    print(" ", signature_string(27))
    print()

    print("Wheel signature for n=6:")
    print(" ", signature_string(6))
    print()

    print("Transitions in signature for n=27 (first 10):")
    trans = signature_transitions(27)[:10]
    print(" ", trans)