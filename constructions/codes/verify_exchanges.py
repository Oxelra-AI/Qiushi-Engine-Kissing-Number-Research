#!/usr/bin/env python3
"""Reproduce the five final support exchanges from their complete parents."""
import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def masks(path):
    return [int(line.strip(), 16) for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "$"))]


def check_supports(code, dimension, size):
    require(len(code) == len(set(code)) == size, "Support cardinality or repeated mask")
    require(all(0 <= b < 1 << dimension and b.bit_count() == 8 for b in code),
            "Invalid support mask")
    require(all((a & b).bit_count() <= 4 for a, b in combinations(code, 2)),
            "Incompatible support pair")


def check():
    ledger = json.loads((ROOT / "data/exchanges/exchanges.json").read_text())
    results = []
    for entry in ledger["exchanges"]:
        n = entry["dimension"]
        for role in ("parent", "final"):
            path = ROOT / entry[role]
            require(hashlib.sha256(path.read_bytes()).hexdigest() == entry[role + "_sha256"],
                    f"Input hash mismatch in dimension {n}: {role}")
        before, after = (masks(ROOT / entry[role]) for role in ("parent", "final"))
        check_supports(before, n, entry["parent_size"])
        check_supports(after, n, entry["final_size"])
        removed = {int(b, 16) for b in entry["removed_hex"]}
        added = {int(b, 16) for b in entry["added_hex"]}
        require(len(removed) == len(entry["removed_hex"]) and
                len(added) == len(entry["added_hex"]), "Repeated exchange mask")
        require(removed <= set(before) and not added.intersection(before),
                "Invalid removed or inserted support")
        require((set(before) - removed) | added == set(after), "Final witness mismatch")
        blockers = {b for b in before if any((b & c).bit_count() > 4 for c in added)}
        require(blockers == removed, "Removed supports differ from the exact conflict union")
        gain = len(after) - len(before)
        require(len(added) - len(removed) == gain and gain > 0, "Wrong exchange gain")
        results.append({"dimension": n, "parent_size": len(before),
                        "removed": len(removed), "inserted": len(added),
                        "final_size": len(after), "gain": gain,
                        "final_set_matches": True, "exact_conflict_union": True,
                        "complete_pair_checks": True})
    require([r["dimension"] for r in results] == [33, 34, 37, 38, 39],
            "Missing or repeated exchange dimension")
    return {"valid": True, "transitions": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = json.dumps(check(), indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    print(result, end="")
