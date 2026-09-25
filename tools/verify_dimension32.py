#!/usr/bin/env python3
"""Verify the 347,584-point construction using integer arithmetic."""
import argparse
from collections import Counter
from pathlib import Path

from package_files import sha256, write_json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(data):
    data = Path(data)
    rows = [s.strip() for s in (data / "d33_kernel.txt").read_text().splitlines()
            if s.strip() and not s.startswith("#")]
    generators = [int(s, 16) for s in rows]
    require(len(generators) == 17 and all(0 <= x < 2**32 for x in generators),
            "Expected seventeen length-32 binary generators")
    words = [0]
    for row in generators:
        words += [word ^ row for word in words]
    require(len(set(words)) == 2**17, "The generator rank is not seventeen")
    weights = Counter(word.bit_count() for word in words)
    require(min(w for w in weights if w) == 8, "The minimum code distance is not eight")
    binary = [s.strip() for s in (data / "d32_supports_binary.txt").read_text().splitlines()
              if s.strip() and not s.startswith("#")]
    require(all(len(s) == 32 and set(s) <= {"0", "1"} for s in binary),
            "Invalid binary support")
    supports = [int(s, 2) for s in binary]
    require(len(supports) == len(set(supports)) == 1676, "Support count or uniqueness")
    require(all(x.bit_count() == 8 for x in supports), "Support weight")
    histogram = Counter()
    for i, x in enumerate(supports):
        for y in supports[:i]:
            overlap = (x & y).bit_count()
            require(overlap <= 4, "Incompatible supports")
            histogram[overlap] += 1
    count = len(words) + 128 * len(supports) + 2 * 32 * 31
    require(count == 347584, "Construction count")
    return {"passed": True, "dimension": 32, "points": count,
            "code_rank": 17, "code_size": len(words), "minimum_distance": 8,
            "code_weight_distribution": dict(sorted(weights.items())),
            "supports": len(supports), "support_pairs": sum(histogram.values()),
            "intersection_histogram": dict(sorted(histogram.items())),
            "input_hashes": {name: sha256(data / name) for name in
                             ("d33_kernel.txt", "d32_supports_binary.txt")},
            "arithmetic": "Python integers",
            "geometric_reduction": "Three-layer ERS construction in the accompanying report"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = check(args.data)
    write_json(args.output, report)
    print(f"Verified K(32) >= {report['points']}; {report['support_pairs']} support pairs")


if __name__ == "__main__":
    main()
