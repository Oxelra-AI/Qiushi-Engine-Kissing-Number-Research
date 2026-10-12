#!/usr/bin/env python3
"""Prepare a certified integer BKZ basis for the complete P48p minimal shell."""
import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parent


def prepare(blocks=(20, 30), loops=2):
    from fpylll import BKZ, GSO, IntegerMatrix, LLL
    from sage.all import ZZ, matrix
    sys.path.insert(0, str(ROOT.parent / "sections"))
    from prepare_fast import tail_volume_estimate

    started = time.monotonic()
    original = matrix(ZZ, np.load(ROOT / "data/p48p_gram.npy", allow_pickle=False).tolist())
    if original.det() != 1 or not original.is_positive_definite():
        raise ValueError("Invalid P48p Gram")
    q = IntegerMatrix.from_matrix([[int(x) for x in row] for row in original.rows()])
    u = IntegerMatrix.identity(48)
    gso = GSO.Mat(q, U=u, gram=True, flags=GSO.INT_GRAM)
    gso.update_gso()
    trials = []
    best = None

    def assess(label):
        nonlocal best
        transform = matrix(ZZ, u)
        gram = matrix(ZZ, q)
        if abs(transform.det()) != 1 or gram != transform * original * transform.transpose():
            raise ValueError("Invalid BKZ basis change")
        diagonal = [gso.get_r(i, i) for i in range(48)]
        score = tail_volume_estimate(diagonal, 6)
        trials.append({"label": label, "elapsed_seconds": time.monotonic() - started,
                       "tail_volume_estimate": score, "gso_diagonal": diagonal})
        if best is None or score < best[0]:
            best = (score, transform, gram, label)

    assess("catalogue")
    lll = LLL.Reduction(gso)
    lll()
    assess("LLL")
    for block in blocks:
        BKZ.Reduction(gso, lll, BKZ.Param(block_size=block, max_loops=loops))()
        assess("BKZ-%d" % block)
    _, transform, gram, selected = best
    coefficient_bound = 6 * max(original.inverse().diagonal())
    if coefficient_bound >= 128 ** 2:
        raise ValueError("Signed-int8 coefficient bound failed")
    rows = lambda a: [[int(x) for x in row] for row in a.rows()]
    return {"dimension": 48, "coordinate_columns": 48, "squared_norm": 6,
            "expected_rows": 52416000, "coefficient_output": True, "antipodal_output": True,
            "gram": rows(gram), "output_gram": rows(original), "transform": rows(transform),
            "components": [{"center": [0] * 48, "offset": [0] * 48, "radius_squared": 6}],
            "coefficient_bound_squared": str(coefficient_bound),
            "basis_preparation": {"selected": selected, "trials": trials,
                                  "determinant_U": int(transform.det()),
                                  "exact_identity": "Q = U G U^t; det(U) = +/-1"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--blocks", nargs="+", type=int, default=[20, 30])
    parser.add_argument("--loops", type=int, default=2)
    args = parser.parse_args()
    if args.output.exists() or args.loops <= 0 or any(not 2 <= b <= 48 for b in args.blocks):
        parser.error("Choose a new output path and valid reduction controls")
    geometry = prepare(args.blocks, args.loops)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(geometry, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(args.output), "preparation": geometry["basis_preparation"]}, indent=2))


if __name__ == "__main__":
    main()
