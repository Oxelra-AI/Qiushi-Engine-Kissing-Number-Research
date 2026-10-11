#!/usr/bin/env python3
"""Prepare an exactly certified BKZ basis for section-vector enumeration.

Run with a SageMath Python that provides fpylll. BKZ uses floating-point
Gram--Schmidt data to choose integer row operations, but the resulting
unimodular basis change and all geometric identities are checked exactly.
No vector enumeration is performed here.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
import json
import math
from pathlib import Path
import time

try:
    from .export_vectors import prepare
except ImportError:
    from export_vectors import prepare


def tail_volume_estimate(diagonal, radius):
    """Heuristic node-cost indicator, not an enumeration bound or proof."""
    n = len(diagonal)
    return sum(math.exp((n - i) / 2 * math.log(math.pi * radius)
                        - math.lgamma((n - i) / 2 + 1)
                        - sum(math.log(d) for d in diagonal[i:]) / 2)
               for i in range(n))


def prepare_reduced(dimension, blocks=(20, 30), loops=2):
    import fpylll
    from fpylll import BKZ, GSO, IntegerMatrix, LLL
    from sage.all import QQ, ZZ, matrix, vector

    if loops <= 0:
        raise ValueError("loops must be positive")
    if any(not 2 <= block <= dimension for block in blocks):
        raise ValueError("Each BKZ block size must lie in [2, dimension]")
    started = time.monotonic()
    geometry = prepare(dimension)
    original_q = matrix(ZZ, geometry["gram"])
    original_transform = matrix(ZZ, geometry["transform"])
    q_fplll = IntegerMatrix.from_matrix(geometry["gram"])
    u_fplll = IntegerMatrix.identity(dimension)
    gso = GSO.Mat(q_fplll, U=u_fplll, gram=True, flags=GSO.INT_GRAM)
    gso.update_gso()
    radius = float(geometry["components"][0]["radius_squared"])
    trials = []
    best = None

    def assess(label):
        nonlocal best
        diagonal = [gso.get_r(i, i) for i in range(dimension)]
        score = tail_volume_estimate(diagonal, radius)
        u = matrix(ZZ, u_fplll)
        q = matrix(ZZ, q_fplll)
        if abs(u.det()) != 1 or q != u * original_q * u.transpose():
            raise ValueError("BKZ did not return the claimed unimodular Gram change")
        record = {"label": label, "elapsed_seconds": time.monotonic() - started,
                  "tail_volume_estimate": score,
                  "gram_schmidt_squared_lengths": diagonal}
        trials.append(record)
        if best is None or score < best[0]:
            best = (score, u, q, label)

    assess("original LLL_gram")
    lll = LLL.Reduction(gso)
    lll()
    assess("fplll LLL")
    for block in blocks:
        reducer = BKZ.Reduction(gso, lll, BKZ.Param(block_size=block, max_loops=loops))
        reducer()
        assess("BKZ-%d; at most %d loops" % (block, loops))

    _, u, q, label = best
    transform = u * original_transform
    inverse = u.inverse()
    components = deepcopy(geometry["components"])
    for component in components:
        center = vector(QQ, [str(x) for x in component["center"]]) * inverse
        component["center"] = [Fraction(str(x)) for x in center]
        if center * transform + vector(ZZ, component["offset"]) != 0:
            raise ValueError("Transformed affine center does not give the origin")
    orthogonal = matrix(ZZ, geometry["orthogonal_to_rows"])
    scale = {43: 96, 45: 768}[dimension]
    if transform * transform.transpose() != scale * q:
        raise ValueError("Transformed Cartesian basis and Gram matrix disagree")
    if transform * orthogonal.transpose() != 0:
        raise ValueError("Transformed Cartesian basis left the section")
    if q.det() != original_q.det():
        raise ValueError("Gram determinant changed")
    geometry.update({
        "gram": [[int(x) for x in row] for row in q.rows()],
        "transform": [[int(x) for x in row] for row in transform.rows()],
        "components": components,
        "basis_preparation": {
            "method": "exactly checked integer Gram BKZ via fpylll",
            "fpylll_version": fpylll.__version__,
            "blocks_in_sequence": list(blocks), "maximum_loops_per_block": loops,
            "selected": label,
            "selection": "smallest heuristic sum of projected-ball volumes; not a proof",
            "basis_change_U": [[int(x) for x in row] for row in u.rows()],
            "determinant_U": int(u.det()),
            "gram_determinant": int(q.det()),
            "exact_identities_checked": [
                "det(U) = +1 or -1", "Q_new = U Q_old U^t",
                "T_new = U T_old", "c_new = c_old U^-1",
                "c_new T_new + offset = 0", "T_new T_new^t = scale Q_new",
                "T_new orthogonal_to_rows^t = 0"],
            "trials": trials,
        },
    })
    return geometry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", required=True, type=int, choices=(43, 45))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--blocks", type=int, nargs="+", default=[20, 30])
    parser.add_argument("--loops", type=int, default=2)
    args = parser.parse_args()
    if args.loops <= 0:
        parser.error("loops must be positive")
    if args.output.exists():
        parser.error("choose a new output path; existing geometry is retained")
    geometry = prepare_reduced(args.dimension, tuple(args.blocks), args.loops)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(geometry, stream, indent=2, default=str)
        stream.write("\n")
    print(json.dumps({"dimension": args.dimension, "output": str(args.output),
                      "selected": geometry["basis_preparation"]["selected"],
                      "trials": [{k: v for k, v in trial.items()
                                  if k != "gram_schmidt_squared_lengths"}
                                 for trial in geometry["basis_preparation"]["trials"]]},
                     indent=2))


if __name__ == "__main__":
    main()
