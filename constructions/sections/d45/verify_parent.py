#!/usr/bin/env python3
"""Verify the signed anchor graph and recover its optimal 298-vector fibre.

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


def anchor_moments():
    """Exact filtered moments; the second coefficient is for a unit z in p-perp."""
    def shell_moment(k):
        return Fraction(52416000 * 48**k * prod(range(1, 2*k, 2)),
                        prod(48 + 2*j for j in range(k)))

    def mixed_moment(k):
        return Fraction(52416000 * 6**(k+1) * 8**k * prod(range(1, 2*k, 2)),
                        prod(48 + 2*j for j in range(k+1)))

    def filtered(moment):
        return moment(4) - 14*moment(3) + 49*moment(2) - 36*moment(1)

    polynomial_sum = filtered(shell_moment)
    denominator = 2 * (16 * 15 * 12 * 7)
    endpoints = polynomial_sum / denominator
    second_coefficient = filtered(mixed_moment) / denominator
    require(polynomial_sum == 90961920 and endpoints == 2256,
            "Eighth moment does not certify the endpoint count")
    require(second_coefficient == 192, "Tenth moment does not certify the tight frame")
    return polynomial_sum, endpoints, second_coefficient


def check_negative_four_cliques(signed):
    """Reject every switching-equivalent all-negative K4, using exact bitsets.

    For a<b<c<d, the four-clique is of this type exactly when the three
    triangles through a have negative sign product. Negative triangles are
    permitted; in the lattice only the sum of an even number of centred
    endpoints is necessarily a lattice vector.
    """
    positive = [sum(1 << int(j) for j in np.flatnonzero(row == 1)) for row in signed]
    negative = [sum(1 << int(j) for j in np.flatnonzero(row == -1)) for row in signed]
    negative_triangles = 0
    for a in range(len(signed)):
        above_a = ~((1 << (a+1)) - 1)
        pos_a, neg_a = positive[a] & above_a, negative[a] & above_a
        neighbours = pos_a | neg_a
        while neighbours:
            b_bit = neighbours & -neighbours
            b = b_bit.bit_length() - 1
            neighbours ^= b_bit
            if pos_a & b_bit:
                candidates = (pos_a & negative[b]) | (neg_a & positive[b])
            else:
                candidates = (pos_a & positive[b]) | (neg_a & negative[b])
            candidates &= ~((1 << (b+1)) - 1)
            negative_triangles += candidates.bit_count()
            while candidates:
                c_bit = candidates & -candidates
                c = c_bit.bit_length() - 1
                candidates ^= c_bit
                if pos_a & c_bit:
                    closing = (pos_a & negative[c]) | (neg_a & positive[c])
                else:
                    closing = (pos_a & positive[c]) | (neg_a & negative[c])
                require(not (candidates & closing), "Switching-equivalent negative four-clique")
    return negative_triangles


def check_signed_graph(signed):
    """Check the full signed spectrum and all codegrees without eigensolvers."""
    signed = np.asarray(signed)
    require(signed.shape == (1128, 1128) and signed.dtype.kind in "iu",
            "Signed matrix must be an integer 1128 by 1128 array")
    require(np.array_equal(signed, signed.T) and not np.any(signed.diagonal()),
            "Signed matrix symmetry or diagonal")
    require(np.all((signed >= -1) & (signed <= 1)), "Signed adjacency entries")
    # Each product is a sum of 1128 terms of absolute value at most one.
    # int32 is exact here; int8 and uint8 would silently overflow codegrees.
    signed = signed.astype(np.int32)
    identity = np.eye(len(signed), dtype=np.int32)
    square = signed @ signed
    require(np.array_equal(square, 88*signed + 368*identity),
            "Signed quadratic identity")
    multiplicity = Fraction(int(np.trace(signed)) + 4*len(signed), 96)
    require(multiplicity == 47, "Signed spectrum multiplicity")
    adjacency = (signed != 0).astype(np.int32)
    require(np.all(adjacency.sum(axis=1) == 368), "Parent graph degree")
    codegrees = adjacency @ adjacency
    upper = np.triu(np.ones(signed.shape, dtype=bool), 1)
    require(np.all(codegrees[upper] % 2 == 0), "Odd common-neighbour count")
    # Each common neighbour contributes +1 or -1 to S^2. Thus these
    # nonnegative integers count the two signs, not just their parity.
    require(np.all((codegrees + square) % 2 == 0)
            and np.all(codegrees >= np.abs(square)), "Signed common-neighbour balance")
    nonadjacent = upper & (adjacency == 0)
    adjacent = upper & (adjacency == 1)
    require(np.all(square[nonadjacent] == 0), "Nonadjacent signed balance")
    require(np.all(square[adjacent] * signed[adjacent] == 88),
            "Adjacent signed triangle balance")
    require(np.array_equal((signed + 4*identity)**2, adjacency + 16*identity),
            "Unsigned tensor Gram identity")

    def histogram(mask):
        return dict(sorted(Counter(int(v) for v in codegrees[mask]).items()))

    adjacent_histogram = histogram(adjacent)
    nonadjacent_histogram = histogram(nonadjacent)
    triangles_numerator = sum(c*n for c, n in adjacent_histogram.items())
    require(triangles_numerator % 3 == 0, "Triangle count is not integral")
    triangles = triangles_numerator // 3
    signed_difference = 88 * 368 * len(signed) // 6
    require((triangles - signed_difference) % 2 == 0, "Signed triangle count parity")
    negative_triangles = check_negative_four_cliques(signed)
    require(negative_triangles == (triangles-signed_difference)//2,
            "Independent negative-triangle count")
    report = {
        "signed_quadratic_identity": "S^2 = 88 S + 368 I",
        "signed_spectrum": [{"eigenvalue": -4, "multiplicity": len(signed)-int(multiplicity)},
                            {"eigenvalue": 92, "multiplicity": int(multiplicity)}],
        "signed_spectrum_method": "exact quadratic identity and zero trace",
        "unsigned_eigenvalue_lower_bound": -16,
        "unsigned_tensor_gram_identity": "(4 I + S) entrywise-squared = 16 I + A",
        "all_codegrees_even": True,
        "signed_common_neighbour_balances_checked": True,
        "adjacent_pairs": int(np.count_nonzero(adjacent)),
        "nonadjacent_pairs": int(np.count_nonzero(nonadjacent)),
        "adjacent_codegree_histogram": adjacent_histogram,
        "nonadjacent_codegree_histogram": nonadjacent_histogram,
        "negative_four_cliques": 0,
        "positive_triangles": triangles-negative_triangles,
        "negative_triangles": negative_triangles,
        "nonadjacent_codegree_minimum": min(nonadjacent_histogram),
        "nonadjacent_codegree_minimum_multiplicity": nonadjacent_histogram[min(nonadjacent_histogram)],
        "nonadjacent_codegree_maximum": max(nonadjacent_histogram),
    }
    return report, adjacency.astype(bool), codegrees


def check(data=DATA):
    parent = json.loads((data / "parent.json").read_text())
    G = integers(json.loads((data / "gram.json").read_text())["ambient_G"], (48, 48))
    B = integers(parent["basis_scaled_by_sqrt12"], (48, 48))
    p = integers(parent["parent_coeff"], (48,))
    y = integers(parent["y"], (48,))
    r = integers(parent["selected_endpoints"]["r"], (48,))
    s = integers(parent["selected_endpoints"]["s"], (48,))
    rows = [json.loads(line) for line in (data / "parent-vectors.jsonl").read_text().splitlines()
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
    polynomial_sum, endpoint_count, second_coefficient = anchor_moments()
    require(endpoint_count == len(R),
            "Eighth moment does not certify the endpoint count")

    # The unit-z moment gives the frame; its value at z=r-p/2 gives
    # 32+2*degree because z^2=4.
    endpoint_second_moment = 4*second_coefficient
    require(endpoint_second_moment == 768 and (endpoint_second_moment-32)/2 == 368,
            "Mixed moment does not certify the graph degree")

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
    centred_gram = gram - 2
    signed = centred_gram - 4*np.eye(len(U), dtype=np.int64)
    # V = 2 sqrt(12) u in physical integer coordinates. The right side
    # is 48*96 times the orthogonal projector I - yy^T/96 onto p-perp.
    V = (2*U-p) @ B
    require(int(np.abs(V).max()) <= 14, "Centred physical coordinate range")
    require(np.array_equal(V.T @ V, 4608*np.eye(48, dtype=np.int64)-48*np.outer(y, y)),
            "Physical tight-frame identity")
    graph_report, adjacency, codegrees = check_signed_graph(signed)
    require(tuple(r.tolist()) in endpoint_set and tuple(s.tolist()) in endpoint_set,
            "Selected endpoints are absent")
    canonical = lambda x: min(tuple(x.tolist()), tuple((p-x).tolist()))
    i, j = reps.index(canonical(r)), reps.index(canonical(s))
    require(i != j and not adjacency[i, j], "Selected pair must be nonadjacent")
    common = int(codegrees[i, j])
    require(common == 70, "Selected common-neighbour count")
    require(graph_report["nonadjacent_pairs"] == 428076,
            "Incomplete nonadjacent-pair enumeration")
    require(graph_report["nonadjacent_codegree_minimum"] == common
            and graph_report["nonadjacent_codegree_minimum_multiplicity"] == 1,
            "Selected pair is not the unique fixed-anchor optimum")
    selected = np.flatnonzero(adjacency[i] & ~adjacency[j])
    require(len(selected) == 368 - common == 298, "Selected fibre size")

    T = np.array([-s, s-p, p-r], dtype=np.int64)
    compact = json.loads((data / "compact.json").read_text())
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
    final = json.loads((data / "record.json").read_text())["t_witness_vectors"]
    require(len(witnesses) == len(set(witnesses)) == len(final) == 298,
            "Repeated or missing fibre witness")
    require(set(witnesses) == {tuple(row) for row in final}, "Final witness set differs")
    # The target signature implies w.p=4, so every vector in that
    # fibre belongs to the complete parent. Check the reverse inclusion.
    signatures = R @ G @ T.T
    full_fibre = R[np.all(signatures == [-2, -2, 3], axis=1)]
    require({tuple(row) for row in full_fibre.tolist()} == set(witnesses),
            "The extracted witness set is not the complete fibre")
    inputs = ("gram.json", "parent.json", "parent-vectors.jsonl", "compact.json", "record.json")
    return {"passed": True, "parent_squared_norm": 8,
            "parent_shape_absolute_counts": {"1": 42, "3": 6},
            "coordinate_basis_matches": True, "parent_endpoint_count": len(R),
            "eighth_moment_polynomial_sum": int(polynomial_sum),
            "parent_complete_by_eighth_moment": True,
            "anchor_second_moment": int(endpoint_second_moment),
            "anchor_unit_second_moment": int(second_coefficient),
            "one_endpoint_frame_constant": int(second_coefficient/2),
            "frame_dimension": 47, "physical_tight_frame_checked": True,
            "graph_degree_certified_by_tenth_moment": True,
            "pairing": "{x,p-x}, centred at p/2", "parent_pairs": len(reps),
            "graph_degree": 368, "selected_pair_common_neighbours": common,
            "graph_structure": graph_report,
            "selected_pair_canonical_indices": sorted([i, j]),
            "fixed_anchor_maximum_projected_count": 7380720-9*common,
            "all_section_counts_divisible_by": 18,
            "recovered_witness_count": len(witnesses), "section_matches": True,
            "fibre_complete": True, "exact_fibre_count": len(full_fibre),
            "final_witness_set_matches": True, "projection_lower_bound": 7377408+9*len(witnesses),
            "projection_count_verifier": "verify.py",
            "premises": ["Specified QR neighbour has minimum squared norm 6",
                         "Its 52416000-vector minimal shell is an 11-design"],
            "input_sha256": {name: hashlib.sha256((data/name).read_bytes()).hexdigest()
                             for name in inputs}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.dumps(check(), indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(report, end="")
