#!/usr/bin/env python3
"""Recompute a 591,900-point construction from its frozen coordinate data.

The public base construction supplies a Golay basis, a partition of minimal
lines, and fourteen-dimensional directions. The added antipodal lines are
checked against that exact coordinate convention. No external verifier is run.
"""
import argparse
from collections import Counter
from itertools import combinations
import json
from math import isqrt
from pathlib import Path

import numpy as np
from package_files import sha256, write_json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def golay_words(data):
    rows = [line.strip() for line in (data / "golay_basis.txt").read_text().splitlines() if line.strip()]
    require(len(rows) == 12 and all(len(row) == 24 and set(row) <= {"0", "1"} for row in rows), "Golay generator format")
    basis = np.array([[int(c) for c in row] for row in rows], dtype=np.uint8)
    messages = ((np.arange(4096)[:, None] >> np.arange(12)) & 1).astype(np.uint8)
    code = (messages @ basis) & 1
    require(len({row.tobytes() for row in code}) == 4096, "Golay generator rank")
    require(dict(Counter(code.sum(1).tolist())) == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}, "Golay weight enumerator")
    return code


def leech_membership(vector, codewords):
    """Golay congruences for the integer Leech model of minimum norm 32."""
    if not isinstance(codewords, (set, frozenset)):
        raise TypeError("Expected a set of complete Golay words")
    values = tuple(int(x) for x in vector)
    if len(values) != 24:
        return False
    parity = values[0] % 2
    return (all(x % 2 == parity for x in values)
            and tuple(((x - parity) // 2) % 2 for x in values) in codewords
            and sum(values) % 8 == 4 * parity)


def shell(data):
    code = golay_words(data)
    vectors = []
    for i, j in combinations(range(24), 2):
        for si in (-4, 4):
            for sj in (-4, 4):
                v = np.zeros(24, dtype=np.int16)
                v[i], v[j] = si, sj
                vectors.append(v)
    signs = [m for m in range(256) if m.bit_count() % 2 == 0]
    for row in code[code.sum(1) == 8]:
        indices = np.flatnonzero(row)
        for mask in signs:
            v = np.zeros(24, dtype=np.int16)
            v[indices] = [-2 if (mask >> i) & 1 else 2 for i in range(8)]
            vectors.append(v)
    for row in code:
        base = np.where(row, -1, 1).astype(np.int16)
        for i in range(24):
            v = base.copy()
            v[i] = 3 if row[i] else -3
            vectors.append(v)
    vectors = np.array(vectors, dtype=np.int64)
    require(vectors.shape == (196560, 24) and np.all((vectors * vectors).sum(1) == 32), "Leech shell norm or size")
    require(len({row.tobytes() for row in vectors}) == len(vectors), "Repeated Leech vector")
    lines = vectors.copy()
    first = np.argmax(lines != 0, axis=1)
    lines[lines[np.arange(len(lines)), first] < 0] *= -1
    lines = np.unique(lines, axis=0)
    require(lines.shape == (98280, 24), "Leech line count")
    return vectors, lines


def load_small_integers(path, shape, delimiter=None, bound=64):
    values = np.loadtxt(path, dtype=np.int64, delimiter=delimiter)
    require(values.shape == shape and int(values.min()) >= -bound and int(values.max()) <= bound,
            "Unexpected input shape or coordinate bound: " + path.name)
    return values


def check(data, added_path):
    vectors, lines = shell(data)
    directions = load_small_integers(data / "dim14_directions.txt", (1932, 14), delimiter=",")
    triples = load_small_integers(data / "triples.txt", (644, 3), bound=1931)
    keep = load_small_integers(data / "axis_keep.txt", (1932,), bound=1931)
    labels = load_small_integers(data / "class_labels.txt", (98280,), bound=643)
    require(np.array_equal(np.sort(triples.ravel()), np.arange(1932)), "Triples must partition the direction indices")
    require(np.array_equal(np.sort(keep), np.arange(1932)), "Axis selection must be a permutation")
    require(np.all(labels >= 0), "Negative class label")
    require(np.all((directions * directions).sum(1) == 8), "Direction norm")
    require(len({row.tobytes() for row in directions}) == 1932, "Repeated direction")
    gram = directions @ directions.T
    np.fill_diagonal(gram, -8)
    require(int(gram.max()) <= 4, "Direction angle")
    for a, b, c in triples:
        require(np.all(directions[a] + directions[b] + directions[c] == 0), "Triangle sum")
        require(all(int(directions[i] @ directions[j]) == -4 for i, j in ((a, b), (a, c), (b, c))), "Triangle angle")
    for label in range(644):
        selected = lines[labels == label]
        inner = selected @ selected.T
        np.fill_diagonal(inner, 0)
        require(not inner.size or int(np.abs(inner).max()) <= 8, "Head class angle")

    raw_rotation = (data / "axis_rotation.txt").read_text().splitlines()
    rotation = np.array([[int(v) for v in row.split()] for row in raw_rotation if row.strip()], dtype=object)
    denominator = int((data / "axis_rotation_D.txt").read_text())
    require(rotation.shape == (14, 14) and denominator > 0, "Rational rotation format")
    gram_rotation = rotation @ rotation.T
    require(all(gram_rotation[i, j] == (denominator * denominator if i == j else 0)
                for i in range(14) for j in range(14)), "Rational rotation is not orthogonal")
    threshold = isqrt(48 * denominator * denominator)
    rotated = directions.astype(object) @ rotation.T
    max_axis_product = 0
    for i in keep:
        products = rotated[i] @ directions.astype(object).T
        max_axis_product = max(max_axis_product, max(abs(int(v)) for v in products))
    require(max_axis_product <= threshold, "Rotated axis and cap directions are incompatible")

    added = load_small_integers(added_path, (144, 24))
    require(np.all((added * added).sum(1) == 48), "Added line norm")
    codewords = {tuple(int(x) for x in row) for row in golay_words(data)}
    require(all(leech_membership(row, codewords) for row in added), "Added vector is outside the specified Leech lattice")
    canonical_added = {min(tuple(row), tuple(-row)) for row in added}
    require(len(canonical_added) == 144, "Repeated antipodal line")
    inner = added @ added.T
    np.fill_diagonal(inner, 0)
    max_new = int(np.abs(inner).max())
    max_shell = max(int(np.abs(vectors[start:start + 4096] @ added.T).max())
                    for start in range(0, len(vectors), 4096))
    require(max_new <= 24 and max_shell <= 24, "Added line compatibility")
    # Caps use all minimal lines; there are no old equatorial points.
    # A new unit equatorial vector s/sqrt(48) against a cap has product
    # sqrt(2/3) * <s,u>/sqrt(48*32) = <s,u>/48 <= 1/2.
    cap_count = 6 * len(lines)
    axis_count = len(keep)
    base = cap_count + axis_count
    total = base + 2 * len(added)
    require(base == 591612 and total == 591900, "Unexpected construction cardinality")
    return {"passed": True, "dimension": 38, "points": total,
            "base": {"equator": 0, "caps": cap_count, "axis": axis_count, "total": base},
            "added_antipodal_lines": len(added), "added_points": 2 * len(added),
            "leech_membership_checked": len(added),
            "max_abs_added_pair_product": max_new,
            "max_abs_added_shell_product": max_shell,
            "axis_product_maximum": max_axis_product, "axis_product_threshold": threshold,
            "data_hashes": {p.name: sha256(p) for p in sorted(data.iterdir()) if p.is_file()},
            "added_lines_sha256": sha256(added_path),
            "coordinate_convention": "The shipped Golay basis and lexicographically sorted canonical Leech lines",
            "premise": "The standard Golay construction has Leech minimum squared norm 32 and shell size 196560.",
            "arithmetic": "bounded int64 products; arbitrary-precision rational rotation products",
            "external_verifiers_run": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-data", type=Path, required=True)
    parser.add_argument("--lines", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = check(args.base_data.resolve(), args.lines.resolve())
    write_json(args.output, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
