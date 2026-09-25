#!/usr/bin/env python3
"""Recover the 298-vector fibre from the complete norm-eight parent graph.

All coordinates use the supplied QR-neighbour Gram basis. The ambient
minimum six, shell size 52416000 and 11-design property are the premises
established by the accompanying lattice argument.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import prod
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent / "data"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integers(values, shape):
    result = np.asarray(values)
    require(result.shape == shape and result.dtype.kind in "iu", "Integer array shape or type")
    require(int(result.min()) >= -65536 and int(result.max()) <= 65536,
            "Coordinates exceed the checked integer range")
    return result.astype(np.int64)


def check():
    parent = json.loads((DATA / "parent.json").read_text())
    G = integers(json.loads((DATA / "gram.json").read_text())["ambient_G"], (48, 48))
    B = integers(parent["basis_scaled_by_sqrt12"], (48, 48))
    p = integers(parent["parent_coeff"], (48,))
    y = integers(parent["y"], (48,))
    r = integers(parent["selected_endpoints"]["r"], (48,))
    s = integers(parent["selected_endpoints"]["s"], (48,))
    rows = [json.loads(line) for line in (DATA / "parent-vectors.jsonl").read_text().splitlines()
            if line.strip()]
    R = integers(rows, (2256, 48))
    coefficient_max = max(int(np.abs(a).max()) for a in (R, p, r, s))
    product_bound = 48**2 * (2 * coefficient_max)**2 * int(np.abs(G).max())
    require(product_bound < np.iinfo(np.int64).max, "Inner products exceed int64 range")
    require(np.array_equal(B @ B.T, 12 * G), "Physical basis differs from the Gram basis")
    require(np.array_equal(p @ B, y), "Parent numerator and coefficient row differ")
    require(int(p @ G @ p) == 8 and int(y @ y) == 96, "Parent squared norm")
    require(Counter(abs(int(a)) for a in y) == {1: 42, 3: 6}, "Odd-sector parent shape")
    endpoint_set = {tuple(row) for row in R.tolist()}
    require(len(endpoint_set) == 2256, "Repeated parent endpoint")
    RG = R @ G
    require(np.all(np.sum(RG * R, axis=1) == 6), "Endpoint squared norm")
    require(np.all(RG @ p == 4), "Endpoint-parent inner product")

    # On a minimum-six shell, the integral product with a norm-eight parent
    # lies in [-4,4].  P(t) vanishes at 0,+/-1,+/-2,+/-3.  Its eighth moment
    # counts the two antipodal fibres t=+/-4, proving completeness of R.
    def shell_moment(k):
        return Fraction(52416000 * 48**k * prod(range(1, 2*k, 2)),
                        prod(48 + 2*j for j in range(k)))
    polynomial_sum = (shell_moment(4) - 14*shell_moment(3)
                      + 49*shell_moment(2) - 36*shell_moment(1))
    p_at_four = 16 * 15 * 12 * 7
    require(polynomial_sum == 90961920 and polynomial_sum / (2*p_at_four) == len(R),
            "Eighth moment does not certify the endpoint count")

    # These are {x,p-x} pairs, centred at p/2; they are not {x,-x}.
    representatives = set()
    for x in endpoint_set:
        partner = tuple(int(p[i]) - x[i] for i in range(48))
        require(partner in endpoint_set and partner != x, "Unpaired parent endpoint")
        representatives.add(min(x, partner))
    reps = sorted(representatives)
    require(len(reps) == 1128, "Parent pair count")
    U = np.asarray(reps, dtype=np.int64)
    gram = U @ G @ U.T
    off_diagonal = ~np.eye(len(U), dtype=bool)
    require(set(gram[off_diagonal].tolist()) <= {1, 2, 3}, "Parent pair inner products")
    adjacency = (gram == 1) | (gram == 3)
    require(np.all(adjacency.sum(axis=1) == 368), "Parent graph degree")
    require(tuple(r.tolist()) in endpoint_set and tuple(s.tolist()) in endpoint_set,
            "Selected endpoints are absent")
    canonical = lambda x: min(tuple(x.tolist()), tuple((p-x).tolist()))
    i, j = reps.index(canonical(r)), reps.index(canonical(s))
    require(i != j and not adjacency[i, j], "Selected pair must be nonadjacent")
    common = int(np.count_nonzero(adjacency[i] & adjacency[j]))
    require(common == 70, "Selected common-neighbour count")
    selected = np.flatnonzero(adjacency[i] & ~adjacency[j])
    require(len(selected) == 368 - common == 298, "Selected fibre size")

    T = np.array([-s, s-p, p-r], dtype=np.int64)
    compact = json.loads((DATA / "compact.json").read_text())
    require(np.array_equal(T, integers(compact["section_basis_T_rows"], (3, 48))),
            "Recovered section differs from the final certificate")
    require(np.array_equal(T @ G @ T.T, np.array([[6, -2, -2], [-2, 6, -2], [-2, -2, 6]])),
            "Recovered section Gram")
    witnesses = []
    for index in selected:
        a = U[index]
        endpoint = a if int(r @ G @ a) == 3 else p-a
        require(int(r @ G @ endpoint) == 3 and int(s @ G @ endpoint) == 2,
                "Selected endpoint orientation")
        w = p-endpoint
        require(int(w @ G @ w) == 6 and np.array_equal(T @ G @ w, [-2, -2, 3]),
                "Recovered fibre witness")
        witnesses.append(tuple(w.tolist()))
    final = json.loads((DATA / "record.json").read_text())["t_witness_vectors"]
    require(len(witnesses) == len(set(witnesses)) == len(final) == 298,
            "Repeated or missing fibre witness")
    require(set(witnesses) == {tuple(row) for row in final}, "Final witness set differs")
    inputs = ("gram.json", "parent.json", "parent-vectors.jsonl", "compact.json", "record.json")
    return {"passed": True, "parent_squared_norm": 8,
            "parent_shape_absolute_counts": {"1": 42, "3": 6},
            "coordinate_basis_matches": True, "parent_endpoint_count": len(R),
            "eighth_moment_polynomial_sum": int(polynomial_sum),
            "parent_complete_by_eighth_moment": True,
            "pairing": "{x,p-x}, centred at p/2", "parent_pairs": len(reps),
            "graph_degree": 368, "selected_pair_common_neighbours": common,
            "recovered_witness_count": len(witnesses), "section_matches": True,
            "final_witness_set_matches": True, "projection_lower_bound": 7377408+9*len(witnesses),
            "projection_count_verifier": "verify.py",
            "premises": ["Specified QR neighbour has minimum squared norm 6",
                         "Its 52416000-vector minimal shell is an 11-design"],
            "input_sha256": {name: hashlib.sha256((DATA/name).read_bytes()).hexdigest()
                             for name in inputs}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.dumps(check(), indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(report, end="")
