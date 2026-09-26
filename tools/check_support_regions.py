#!/usr/bin/env python3
"""Recount twelve-coordinate regions in the published support families."""
import argparse
from functools import lru_cache
import hashlib
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def local_candidates():
    candidates = tuple(sum(1 << i for i in positions)
                       for positions in combinations(range(12), 8))
    forbidden = {}
    for weight in (5, 6):
        for positions in combinations(range(12), weight):
            restriction = sum(1 << i for i in positions)
            forbidden[restriction] = sum(1 << j for j, candidate in enumerate(candidates)
                                         if (restriction & candidate).bit_count() > 4)
    return candidates, forbidden


def check(root, dimension):
    relative = f"constructions/codes/data/d{dimension}_supports_binary.txt"
    path = root / relative
    lines = [line.strip() for line in path.read_text().splitlines()
             if line.strip() and not line.startswith("#")]
    if not all(len(line) == dimension and set(line) <= {"0", "1"} for line in lines):
        raise ValueError("Expected fixed-length binary support strings")
    supports = sorted(int(line, 2) for line in lines)
    family = set(supports)
    if len(family) != len(supports) or not all(a.bit_count() == 8 for a in supports):
        raise ValueError("Expected distinct weight-eight supports")
    triples = []
    for a, b in combinations(supports, 2):
        overlap = (a & b).bit_count()
        if overlap > 4:
            raise ValueError("Incompatible support family")
        # A twelve-coordinate triangle has third support a XOR b.
        c = a ^ b
        if overlap == 4 and c > b and c in family:
            triples.append((a, b, c))

    candidates, forbidden = local_candidates()
    all_candidates = (1 << len(candidates)) - 1
    best = 0
    witness = None
    for triple in triples:
        region = triple[0] | triple[1]
        positions = [i for i in range(dimension) if region >> i & 1]
        assert len(positions) == 12
        local_bit = {1 << position: 1 << i for i, position in enumerate(positions)}
        restrictions = {a & region for a in supports if a not in triple
                        and (a & region).bit_count() > 4}
        available = all_candidates
        for restriction in sorted(restrictions, key=lambda x: (-x.bit_count(), x)):
            # Each region coordinate occurs in two triangle supports. An
            # outside support therefore meets the region in at most six places.
            assert restriction.bit_count() in (5, 6)
            mask = 0
            while restriction:
                bit = restriction & -restriction
                mask |= local_bit[bit]
                restriction ^= bit
            available &= ~forbidden[mask]
            if available.bit_count() <= best:
                break  # Further restrictions cannot improve the current best.
        count = available.bit_count()
        if count > best:
            best = count
            witness = {
                "support_hex": [format(a, "x") for a in triple],
                "coordinates_1indexed": sorted(dimension - i for i in positions),
                "free_supports": count,
            }
    return {
        "dimension": dimension,
        "input": relative,
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "support_count": len(supports),
        "triangle_count": len(triples),
        "candidate_supports_per_region": len(candidates),
        "maximum_free_supports": best,
        "maximizing_region": witness,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "region_rule": "Three weight-eight supports, pairwise intersection four, union twelve.",
        "free_support_rule": "An eight-subset of the region meets every support outside the selected triple in at most four positions.",
        "coordinates": "One-based positions from left to right in the binary support string.",
        "results": [check(args.root, dimension) for dimension in (32, 37)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
