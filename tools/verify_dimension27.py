#!/usr/bin/env python3
"""Check the frozen two-layer 201,567-point construction with exact inequalities.

The public Golay/Leech generator fixes the input coordinate convention. All
layer and deletion checks below are performed here, without an external verifier.
Coordinates are normalized to squared norm 4 and pairwise inner product <= 2.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import sympy as sp
from package_files import sha256, write_json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integers(path, shape):
    array = np.load(path, allow_pickle=False)
    require(array.shape == shape and array.dtype.kind in "iu", "Unexpected integer-array shape or type")
    require(int(array.min()) >= -512 and int(array.max()) <= 512, "Integer entries exceed checked arithmetic range")
    return array.astype(np.int64)


def geometry():
    triangles = [
        [(1, 1, 0), (-1, 0, -1), (0, -1, 1)],
        [(1, -1, 0), (-1, 0, 1), (0, 1, -1)],
        [(-1, -1, 0), (1, 0, -1), (0, 1, 1)],
        [(-1, 1, 0), (1, 0, 1), (0, -1, -1)],
    ]
    triangles = [[sp.Matrix(v) / sp.sqrt(2) for v in tri] for tri in triangles]
    axis = [sp.Matrix(v) for v in [(2, 0, 0), (-2, 0, 0), (0, 2, 0), (0, -2, 0)]]
    axis += [sp.Matrix([s, t, u * sp.sqrt(2)])
             for s in (-1, 1) for t in (-1, 1) for u in (-1, 1)]
    lines = [sp.eye(3).col(i) for i in range(3)]
    return triangles, axis, lines


def check(data, library):
    paths = {name: data / filename for name, filename in {
        "Y": "heads27_Y.npy", "side": "heads27_side.npy",
        "U": "heads27_layer2_u.npy", "line": "heads27_layer2_line.npy"}.items()}
    Y = integers(paths["Y"], (2258, 24))
    side = integers(paths["side"], (2258,))
    U = integers(paths["U"], (311, 24))
    line = integers(paths["line"], (311,))
    sys.path.insert(0, str(library))
    spec = importlib.util.spec_from_file_location("input_leech_generator", library / "leech.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    M = generator.build().astype(np.int64)
    require(M.shape == (196560, 24) and np.all((M * M).sum(1) == 32), "Invalid Leech shell")
    position = {row.tobytes(): i for i, row in enumerate(M)}
    require(len(position) == len(M), "Repeated shell vector")
    require(np.all((Y * Y).sum(1) == 192), "First-layer norm")
    require(np.all((U * U).sum(1) == 32), "Second-layer norm")
    require(set(side.tolist()) <= {0, 1, 2, 3} and set(line.tolist()) <= {0, 1, 2}, "Invalid tail label")
    require(len({row.tobytes() for row in Y}) == len(Y), "Repeated first-layer head")

    deleted = []
    for start in range(0, len(Y), 64):
        products = Y[start:start + 64] @ M.T
        for row in products:
            hit = np.flatnonzero(row > 48)
            require(len(hit) <= 1, "A first-layer head deletes multiple shell points")
            deleted.extend(hit.tolist())
    require(len(deleted) == len(set(deleted)) == 2090, "First-layer deletions")
    owners = [position.get(row.tobytes(), -1) for row in U]
    require(min(owners) >= 0 and len(set(owners)) == 311, "Second-layer shell membership or repeated owner")
    require(not set(owners).intersection(deleted), "Deletion sets intersect")
    maximum_off_owner = -32
    for start in range(0, len(U), 48):
        products = M @ U[start:start + 48].T
        for j, owner in enumerate(owners[start:start + 48]):
            require(products[owner, j] == 32 and np.count_nonzero(products[:, j] == 32) == 1,
                    "A second-layer owner is not unique")
            products[owner, j] = -32
        maximum_off_owner = max(maximum_off_owner, int(products.max()))
    require(maximum_off_owner <= 16, "Second-layer point touches another deleted shell point")

    triangles, axis, lines = geometry()
    thresholds = np.array([
        [int(144 - 96 * max(u.dot(v) for u in first for v in second))
         for second in triangles] for first in triangles], dtype=np.int64)
    YY = Y @ Y.T
    np.fill_diagonal(YY, -192)
    require(np.all(YY <= thresholds[side[:, None], side[None, :]]), "First-layer pair conflict")
    require(thresholds.tolist() == [[48 if i == j else 96 for j in range(4)] for i in range(4)],
            "First-layer tail geometry")
    require(all(sp.simplify(u.dot(v) + sp.Rational(1, 2)) == 0
                for tri in triangles for i, u in enumerate(tri) for v in tri[i + 1:]),
            "A triangle is not equilateral")
    for i, a in enumerate(axis):
        require(a.dot(a) == 4, "Axis norm")
        require(all(sp.simplify(2 - a.dot(b)).is_nonnegative is True for b in axis[i + 1:]), "Axis pair conflict")

    inequalities = {}
    inequalities["first_head_axis"] = [sp.simplify(2 * u.dot(a) / sp.sqrt(3))
        for tri in triangles for u in tri for a in axis]
    inequalities["second_head_axis"] = [abs(v.dot(a)) for v in lines for a in axis]
    max_yu = int((Y @ U.T).max())
    require(max_yu <= 32, "First/second-layer head conflict")
    inequalities["first_second"] = [sp.simplify(sp.sqrt(3) * max_yu / 48
        + abs(2 * u.dot(v) / sp.sqrt(3))) for tri in triangles for u in tri for v in lines]
    inequalities["second_equator"] = [sp.sqrt(3) * maximum_off_owner / 16]
    inequalities["paired_second_head"] = [sp.Integer(2)]
    UU = U @ U.T
    np.fill_diagonal(UU, -32)
    same = line[:, None] == line[None, :]
    same_max = int(UU[same].max())
    cross_max = int(UU[~same].max())
    require(same_max <= 8 and cross_max <= 16, "Second-layer pair conflict")
    inequalities["second_same_line"] = [sp.Rational(3, 32) * same_max + 1]
    inequalities["second_distinct_lines"] = [sp.Rational(3, 32) * cross_max]
    exact_bounds = {}
    for name, values in inequalities.items():
        require(all(sp.simplify(2 - value).is_nonnegative is True for value in values),
                "Exact symbolic inequality failed: " + name)
        maximum = max(values)
        exact_bounds[name] = str(sp.simplify(maximum))
    require(exact_bounds["second_head_axis"] == "2", "Actual second-layer axis contact")
    first_total = len(M) - len(deleted) + 3 * len(Y) + len(axis)
    total = first_total + len(U)
    require(first_total == 201256 and total == 201567, "Unexpected construction cardinality")
    return {"passed": True, "dimension": 27, "points": total,
            "first_layer_heads": len(Y), "first_layer_deleted": len(deleted),
            "second_layer_owners": len(U), "axis_points": len(axis),
            "equator_points": len(M) - len(deleted) - len(U),
            "first_second_integer_max": max_yu,
            "second_layer_integer_maxima": {"same_line": same_max, "different_lines": cross_max},
            "exact_symbolic_upper_bounds": exact_bounds,
            "coordinate_files": {name: {"file": path.name, "sha256": sha256(path)}
                                 for name, path in paths.items()},
            "leech_generator_sha256": sha256(library / "leech.py"),
            "premise": "The standard Golay construction of the Leech shell has squared norm 32 and maximum inner product 16 between distinct points.",
            "arithmetic": "bounded int64 dot products and exact algebraic sign comparisons",
            "external_verifiers_run": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = check(args.data.resolve(), args.library.resolve())
    write_json(args.output, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
