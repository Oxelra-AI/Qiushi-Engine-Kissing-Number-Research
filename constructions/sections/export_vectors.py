#!/usr/bin/env python3
"""Stream exact integer Cartesian coordinates for the 43D and 45D sections.

SageMath is needed for integer-kernel and lattice-basis preparation. The
enumeration itself uses Python integers and fractions, without tolerances.
See VECTORS.md for coordinate conventions, commands and computational scope.
"""
import argparse
import csv
from fractions import Fraction
import gzip
import json
from math import isqrt
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


class NodeLimit(Exception):
    """A bounded enumeration stopped before exhausting the search tree."""


def nearest_integers(first, last, numerator, denominator):
    """Visit an integer interval by distance from an exact rational centre."""
    left = min(last, numerator // denominator)
    right = max(first, left + 1)
    while left >= first or right <= last:
        if right > last or (left >= first and
                            abs(left * denominator - numerator) <=
                            abs(right * denominator - numerator)):
            yield left
            left -= 1
        else:
            yield right
            right += 1


def exact_shell(gram, center, radius_squared, stats=None, max_nodes=None):
    """Yield all integer rows a with (a-center) Q (a-center)^t = radius.

    Q is symmetric positive definite. Exact LDL bounds are applied from the
    last coordinate to the first; each integer row is visited at most once.
    """
    n = len(gram)
    q = [[Fraction(x) for x in row] for row in gram]
    center = [Fraction(x) for x in center]
    if not n or len(center) != n or any(len(row) != n for row in q):
        raise ValueError("Inconsistent quadratic-form dimensions")
    if any(q[i][j] != q[j][i] for i in range(n) for j in range(n)):
        raise ValueError("The Gram matrix must be symmetric")
    lower = [[Fraction(i == j) for j in range(n)] for i in range(n)]
    diagonal = [Fraction(0) for _ in range(n)]
    for i in range(n):
        diagonal[i] = q[i][i] - sum(lower[i][k] ** 2 * diagonal[k]
                                   for k in range(i))
        if diagonal[i] <= 0:
            raise ValueError("The Gram matrix must be positive definite")
        for j in range(i + 1, n):
            lower[j][i] = (q[j][i] - sum(lower[j][k] * lower[i][k] * diagonal[k]
                                        for k in range(i))) / diagonal[i]
    stats = stats if stats is not None else {}
    stats.setdefault("nodes", 0)
    row = [0] * n
    shifted = [Fraction(0)] * n

    def visit(i, remaining):
        if i < 0:
            if remaining == 0:
                yield tuple(row)
            return
        midpoint = center[i] - sum(lower[j][i] * shifted[j]
                                   for j in range(i + 1, n))
        numerator, denominator = midpoint.numerator, midpoint.denominator
        bound = remaining * denominator ** 2 / diagonal[i]
        delta = isqrt(bound.numerator // bound.denominator)
        first = -((delta - numerator) // denominator)
        last = (numerator + delta) // denominator
        for value in nearest_integers(first, last, numerator, denominator):
            if max_nodes is not None and stats["nodes"] >= max_nodes:
                raise NodeLimit
            stats["nodes"] += 1
            row[i] = value
            shifted[i] = value - center[i]
            term = value - midpoint
            yield from visit(i - 1, remaining - diagonal[i] * term * term)

    radius_squared = Fraction(radius_squared)
    if radius_squared >= 0:
        yield from visit(n - 1, radius_squared)


def text_matrix(text, marker, count, width):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(marker)) + 1
    rows = [[int(x) for x in re.findall(r"-?\d+", line)]
            for line in lines[start:start + count]]
    if len(rows) != count or any(len(row) != width for row in rows):
        raise ValueError("Invalid input matrix: " + marker)
    return rows


def prepare(dimension):
    """Build saturated section coordinates and an exact reduced Gram form."""
    from sage.all import ZZ, QQ, matrix, vector

    read = lambda path: json.loads(path.read_text())
    if dimension == 43:
        text = (ROOT / "d43/data/parent-section.txt").read_text()
        g = matrix(ZZ, text_matrix(text, "ambient Gram G", 48, 48))
        t = matrix(ZZ, text_matrix(text, "coefficient rows w.r.t.", 8, 48))[:5]
        b = matrix(ZZ, read(ROOT / "d43/data/euclidean-basis.json")["basis_B"])
        scale, squared_norm, expected = 96, 576, 2553792
        starts = [vector(ZZ, 48)]
        signatures = [[0] * 5]
    elif dimension == 45:
        g = matrix(ZZ, read(ROOT / "d45/data/gram.json")["ambient_G"])
        compact = read(ROOT / "d45/data/compact.json")
        t = matrix(ZZ, compact["section_basis_T_rows"])
        starts = matrix(ZZ, compact["projection_witness_rows_W"]).rows()
        b = matrix(ZZ, read(ROOT / "d45/data/parent.json")["basis_scaled_by_sqrt12"])
        scale, squared_norm, expected = 12, 4416, 7380090
        signatures = [[int(i == j) for j in range(3)] for i in range(3)]
    else:
        raise ValueError("Dimension must be 43 or 45")
    if b * b.transpose() != scale * g:
        raise ValueError("Cartesian basis and ambient Gram matrix disagree")
    m = t * g
    k = m.right_kernel_matrix(algorithm="pari", basis="LLL")
    if k.nrows() != dimension or m * k.transpose() != 0:
        raise ValueError("Incorrect section kernel")
    if any(abs(x) != 1 for x in k.elementary_divisors()):
        raise ValueError("The integer section kernel is not saturated")
    q = k * g * k.transpose()
    u = q.LLL_gram()
    if abs(u.det()) != 1:
        raise ValueError("The reduction must be unimodular")
    k = u.transpose() * k
    q = k * g * k.transpose()
    if q.det() != {43: 972, 45: 128}[dimension]:
        raise ValueError("Unexpected section determinant")
    q_inverse = q.inverse()
    components = []
    for w, signature in zip(starts, signatures):
        if list(m * w) != signature:
            raise ValueError("The affine representative has the wrong signature")
        linear = k * g * w
        center = -q_inverse * linear
        radius = QQ(6) - w * g * w + linear * q_inverse * linear
        if radius != {43: QQ(6), 45: QQ(23) / 4}[dimension]:
            raise ValueError("Incorrect projected shell radius")
        # For 45D, 8 times the orthogonal projection is integral.
        projected = w if dimension == 43 else 8 * w - vector(ZZ, [x + 1 for x in signature]) * t
        components.append({
            "center": [Fraction(str(x)) for x in center],
            "radius_squared": Fraction(str(radius)),
            "offset": [int(x) for x in projected * b],
        })
    transform = (1 if dimension == 43 else 8) * k * b
    return {
        "dimension": dimension, "coordinate_columns": 48,
        "squared_norm": squared_norm, "maximum_inner_product": squared_norm // 2,
        "expected_rows": expected,
        "gram": [[int(x) for x in row] for row in q.rows()],
        "transform": [[int(x) for x in row] for row in transform.rows()],
        "components": components,
        "orthogonal_to_rows": [[int(x) for x in row] for row in (t * b).rows()],
    }


def cartesian(a, transform, offset):
    out = offset.copy()
    for value, row in zip(a, transform):
        if value:
            for j, x in enumerate(row):
                out[j] += value * x
    return out


def export(geometry, output, limit=None, max_nodes=None):
    """Write gzip CSV and an explicit complete/partial enumeration receipt."""
    output = Path(output)
    receipt = output.with_name(output.name + ".json")
    if output.exists() or receipt.exists():
        raise FileExistsError("Choose new output paths; existing exports are retained")
    stats = {"nodes": 0}
    count, exhausted, reason = 0, False, "interrupted"
    metadata = {name: geometry[name] for name in (
        "dimension", "coordinate_columns", "squared_norm", "maximum_inner_product",
        "expected_rows", "orthogonal_to_rows")}
    metadata.update({"format": "gzip CSV; no header; 48 integer Cartesian coordinates",
                     "unit_normalization": "divide by sqrt(squared_norm)"})
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with gzip.open(output, "xt", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            for component in geometry["components"]:
                for a in exact_shell(geometry["gram"], component["center"],
                                     component["radius_squared"], stats, max_nodes):
                    point = cartesian(a, geometry["transform"], component["offset"])
                    if sum(x * x for x in point) != geometry["squared_norm"]:
                        raise ValueError("Exported point has incorrect squared norm")
                    writer.writerow(point)
                    count += 1
                    if limit is not None and count >= limit:
                        reason = "row limit"
                        return
            exhausted, reason = True, "exhausted search tree"
    except NodeLimit:
        reason = "node limit"
    except KeyboardInterrupt:
        reason = "interrupted"
    except Exception:
        reason = "error"
        raise
    finally:
        metadata.update({"rows": count, "nodes": stats["nodes"], "stop_reason": reason,
                         "exhausted": exhausted,
                         "complete": exhausted and count == geometry["expected_rows"]})
        receipt.write_text(json.dumps(metadata, indent=2) + "\n")
        print(json.dumps({k: v for k, v in metadata.items() if k != "orthogonal_to_rows"}, indent=2))
    if exhausted and count != geometry["expected_rows"]:
        raise ValueError("Enumeration count differs from the proved cardinality")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", required=True, type=int, choices=(43, 45))
    parser.add_argument("--output", required=True, type=Path, help="new .csv.gz file")
    parser.add_argument("--limit", type=int, help="stop after this many rows (partial export)")
    parser.add_argument("--max-nodes", type=int, help="stop after this many tree nodes (partial export)")
    args = parser.parse_args()
    if any(value is not None and value <= 0 for value in (args.limit, args.max_nodes)):
        parser.error("limits must be positive")
    export(prepare(args.dimension), args.output, args.limit, args.max_nodes)


if __name__ == "__main__":
    main()
