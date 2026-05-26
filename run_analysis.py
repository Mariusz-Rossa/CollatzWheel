# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# run_analysis.py

import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, 'src')
from collatz import collatz_metrics, wheel_signature, signature_transitions
from analysis import correlate_by_start_mod, correlate_by_dominant_transition, top_records

# Numbers above this threshold use chunk mode to avoid OOM
LARGE_N_THRESHOLD = 5_000_000
CHUNK_SIZE        = 5_000_000

SEP = "─" * 60


# ------------------------------------------------------------------ #
#  Progress bar                                                       #
# ------------------------------------------------------------------ #

def _progress(n: int, n_max: int, start_time: float):
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


# ------------------------------------------------------------------ #
#  Small-n mode — full results in memory                              #
# ------------------------------------------------------------------ #

def run_in_memory(n_max: int) -> list[dict]:
    results    = []
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
            _progress(n, n_max, start_time)

    elapsed = time.time() - start_time
    sys.stdout.write(f"\r  [{'█'*40}] 100.0%  {n_max}/{n_max}  "
                     f"done in {elapsed:.1f}s{' '*20}\n")
    sys.stdout.flush()
    return results


# ------------------------------------------------------------------ #
#  Large-n mode — chunk by chunk, no CSV, no RAM explosion            #
# ------------------------------------------------------------------ #

def run_chunked(n_max: int) -> dict:
    """
    Processes n=1..n_max in chunks of CHUNK_SIZE.
    Never stores more than one chunk in RAM.
    Accumulates only what's needed for the final summary:
      - per-mod path length lists  (for avg/max)
      - per-transition length lists
      - rolling top-20 by length
    """
    mod_lengths:   dict[str, list[int]] = defaultdict(list)
    trans_lengths: dict[str, list[int]] = defaultdict(list)
    top_list: list[dict] = []

    global_start = time.time()
    chunk_num    = 0

    for chunk_start in range(1, n_max + 1, CHUNK_SIZE):
        chunk_end = min(chunk_start + CHUNK_SIZE - 1, n_max)
        chunk_num += 1
        print(f"\n  Chunk {chunk_num}: n = {chunk_start:,} – {chunk_end:,}")
        chunk_time = time.time()

        for n in range(chunk_start, chunk_end + 1):
            metrics  = collatz_metrics(n)
            sig      = wheel_signature(n)
            freq     = Counter(signature_transitions(n))

            start_mod = int(sig[0].value) if sig[0].is_regular() else str(sig[0].value)
            dominant  = freq.most_common(1)[0] if freq else None
            length    = metrics["length"]

            mod_lengths[str(start_mod)].append(length)
            if dominant:
                trans_lengths[str(dominant[0])].append(length)

            # Rolling top-20 (keeps RAM bounded)
            top_list.append({
                "start":               n,
                "length":              length,
                "start_mod":           start_mod,
                "dominant_transition": dominant,
            })
            if len(top_list) > 20:
                top_list.sort(key=lambda r: r["length"], reverse=True)
                top_list = top_list[:20]

            if n % max(1, (chunk_end - chunk_start + 1) // 200) == 0 or n == chunk_end:
                _progress(n, n_max, global_start)

        chunk_elapsed = time.time() - chunk_time
        print(f"\n    chunk done in {chunk_elapsed:.1f}s")

    total_elapsed = time.time() - global_start
    sys.stdout.write(f"\r  [{'█'*40}] 100.0%  {n_max:,}/{n_max:,}  "
                     f"done in {total_elapsed:.1f}s{' '*20}\n")
    sys.stdout.flush()

    return {
        "mod_lengths":   mod_lengths,
        "trans_lengths": trans_lengths,
        "top_list":      sorted(top_list, key=lambda r: r["length"], reverse=True)[:10],
    }


def print_summary(summary: dict, n_max: int):
    print("\nCorrelation: start_mod → path length:")
    for mod_val, lengths in sorted(summary["mod_lengths"].items()):
        avg = sum(lengths) / len(lengths)
        print(f"  mod={mod_val}: avg={avg:7.2f}  max={max(lengths):5d}  n={len(lengths)}")

    print("\nCorrelation: dominant_transition → path length:")
    for trans, lengths in sorted(summary["trans_lengths"].items()):
        avg = sum(lengths) / len(lengths)
        print(f"  {trans:12s}: avg={avg:7.2f}  max={max(lengths):5d}  n={len(lengths)}")

    print(f"\nTop 10 longest paths (n ≤ {n_max:,}):")
    for r in summary["top_list"]:
        print(f"  n={r['start']:10,}  length={r['length']:4d}  "
              f"start_mod={r['start_mod']}  dominant={r['dominant_transition']}")


# ------------------------------------------------------------------ #
#  Main loop                                                          #
# ------------------------------------------------------------------ #

print("=== Collatz × Wheel — Analysis ===\n")
print(f"  Chunk mode kicks in for n > {LARGE_N_THRESHOLD:,}  (no CSV, no RAM explosion)\n")

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

    print(f"\n  Computing for n = 1..{n_max:,}...\n")

    if n_max <= LARGE_N_THRESHOLD:
        results = run_in_memory(n_max)

        print("\nCorrelation: start_mod → path length:")
        for mod_val, stats in correlate_by_start_mod(results).items():
            print(f"  mod={mod_val}: avg={stats['avg_len']:7.2f}  "
                  f"max={stats['max_len']:5d}  n={stats['count']}")

        print("\nCorrelation: dominant_transition → path length:")
        for trans, stats in correlate_by_dominant_transition(results).items():
            print(f"  {trans:12s}: avg={stats['avg_len']:7.2f}  "
                  f"max={stats['max_len']:5d}  n={stats['count']}")

        print(f"\nTop 10 longest paths (n ≤ {n_max:,}):")
        for r in top_records(results, 10):
            print(f"  n={r['start']:7,}  length={r['length']:4d}  "
                  f"start_mod={r['start_mod']}  dominant={r['dominant_transition']}")

    else:
        summary = run_chunked(n_max)
        print_summary(summary, n_max)

    print("\n" + SEP + "\n")