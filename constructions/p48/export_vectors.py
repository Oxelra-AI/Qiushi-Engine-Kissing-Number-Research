#!/usr/bin/env python3
"""Materialize complete 49D--55D integer Cartesian direction sets.

Each row is normalized by its own Euclidean length. Equatorial and lifted
rows need not have the same integer squared norm. A complete independently
verified P48p line index and an exact Cartesian Gram factor are required.
"""
import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path
import time

import numpy as np

from verify import canon, tail_roots, rank_q, LAMBDAS, TAIL_SIZES

ROOT = Path(__file__).resolve().parent
COUNTS = {49: 52430156, 50: 52458468, 51: 52500930, 52: 52585772,
          53: 52698696, 54: 52923774, 55: 53301140}
N_LINES = 26208000


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_basis(path):
    from sage.all import ZZ, matrix
    saved = json.loads(Path(path).read_text())
    b = matrix(ZZ, saved["basis_B"])
    scale = ZZ(saved["basis_scale"])
    g = matrix(ZZ, np.load(ROOT / "data/p48p_gram.npy", allow_pickle=False).tolist())
    if b.nrows() != 48 or scale <= 0 or b * b.transpose() != scale * g:
        raise ValueError("Cartesian basis does not reproduce the exact P48p Gram")
    # Doubling the head basis makes 2*scale divisible by every tail norm
    # (1, 2, or 8). Tail scalar radicals can then be represented by repeated
    # integer coordinate blocks, without changing the intrinsic tail rank.
    b, scale = 2 * b, 4 * scale
    maximum = max(abs(int(x)) for x in b.list())
    bound = 48 * 32 * maximum
    if bound > np.iinfo(np.int64).max or b.ncols() * bound ** 2 > np.iinfo(np.int64).max:
        raise ValueError("Cartesian conversion exceeds exact int64 bounds")
    return np.asarray(b.rows(), dtype=np.int64), int(scale)


def prepare_dimension(dimension, head_scale):
    from sage.arith.misc import four_squares
    from sage.all import ZZ, matrix
    k = dimension - 48
    roots, root_norm, name = tail_roots(k)
    representatives = np.asarray(sorted(set(map(tuple, canon(roots).tolist()))), dtype=np.int64)
    if len(representatives) != LAMBDAS[dimension]:
        raise ValueError("Incorrect number of tail lines")
    multiplier = 2 * head_scale // root_norm
    if multiplier * root_norm != 2 * head_scale:
        raise ValueError("Nonintegral tail multiplier")
    factors = [int(x) for x in four_squares(multiplier) if x]
    tails = np.concatenate([factor * representatives for factor in factors], axis=1)
    if not np.all(np.sum(tails * tails, axis=1) == 2 * head_scale):
        raise ValueError("Incorrect embedded tail norm")
    if rank_q(tails) != k:
        raise ValueError("Incorrect exact tail rank")
    c = np.load(ROOT / "data/class_p48_7077.npy", allow_pickle=False).astype(np.int64)
    if matrix(ZZ, c.tolist()).rank() != 48:
        raise ValueError("The first assigned class does not span the head space")
    g = np.load(ROOT / "data/p48p_gram.npy", allow_pickle=False).astype(np.int64)
    matrices = ([np.eye(48, dtype=np.int64)] if dimension == 49 else
                np.load(ROOT / f"data/dim{dimension}_group_elems.npy", allow_pickle=False).astype(np.int64))
    assigned = {}
    sizes = []
    for tail, a in enumerate(matrices):
        if not np.array_equal(a @ g @ a.T, g):
            raise ValueError("Selected image is not an exact lattice isometry")
        image = canon(c @ a)
        if np.any(np.abs(image) > 32):
            raise ValueError("Minimal-vector coefficient bound exceeded")
        before = len(assigned)
        for row in image.astype(np.int8):
            assigned.setdefault(row.tobytes(), tail)
        sizes.append(len(assigned) - before)
    keys = sorted(assigned)
    coefficients = np.frombuffer(b"".join(keys), dtype=np.int8).reshape(-1, 48)
    indices = np.asarray([assigned[key] for key in keys], dtype=np.int32)
    if 2 * N_LINES + 2 * len(keys) + 2 * len(tails) != COUNTS[dimension]:
        raise ValueError("Selected-image union does not give the published cardinality")
    return {"coefficients": coefficients, "tail_indices": indices, "tails": tails,
            "assigned_sizes": sizes, "tail_name": name, "tail_factors": factors,
            "tail_original_columns": int(roots.shape[1]), "tail_root_norm": int(root_norm)}


def record_dtype(maximum_squared_norm):
    bound = isqrt(maximum_squared_norm)
    for name in ("i1", "<i2", "<i4", "<i8"):
        dtype = np.dtype(name)
        if bound <= np.iinfo(dtype).max:
            return dtype
    raise ValueError("Cartesian coordinates exceed int64")


def export(shell_path, basis_path, output_directory, dimensions=range(49, 56), chunk_lines=32768):
    shell_path, basis_path, output_directory = map(Path, (shell_path, basis_path, output_directory))
    receipt = json.loads(shell_path.with_name(shell_path.name + ".json").read_text())
    if not receipt.get("passed") or receipt.get("canonical_lines") != N_LINES:
        raise ValueError("A fully verified canonical mother shell is required")
    if shell_path.stat().st_size != N_LINES * 48 or sha256_file(shell_path) != receipt["sha256"]:
        raise ValueError("Mother-shell size or checksum differs from its verification receipt")
    basis, scale = load_basis(basis_path)
    shell = np.memmap(shell_path, mode="r", dtype=np.int8, shape=(N_LINES, 48))
    shell_keys = shell.view(np.dtype("V48")).reshape(-1)
    dtype = record_dtype(8 * scale)
    extension = {1: "i8", 2: "i16", 4: "i32", 8: "i64"}[dtype.itemsize]
    output_directory.mkdir(parents=True, exist_ok=True)
    states = []
    started = time.monotonic()
    for dimension in dimensions:
        data = prepare_dimension(dimension, scale)
        used_keys = data["coefficients"].view(np.dtype("V48")).reshape(-1)
        positions = np.searchsorted(shell_keys, used_keys)
        if np.any(positions >= N_LINES) or not np.array_equal(shell_keys[positions], used_keys):
            raise ValueError("A lifted line is absent from the independently verified full shell")
        mask = np.zeros(N_LINES, dtype=bool)
        mask[positions] = True
        path = output_directory / f"configuration{dimension}.{extension}"
        if path.exists() or path.with_suffix(".json").exists():
            raise FileExistsError("Existing coordinate artifacts are retained")
        state = dict(data, dimension=dimension, mask=mask, path=path, stream=path.open("xb"),
                     digest=hashlib.sha256(), rows=0, columns=basis.shape[1] + data["tails"].shape[1])
        states.append(state)

    def write(state, rows):
        if not len(rows):
            return
        if rows.dtype != dtype:
            if np.any(np.abs(rows) > np.iinfo(dtype).max):
                raise ValueError("Output coordinate dtype would overflow")
            rows = rows.astype(dtype)
        buffer = memoryview(np.ascontiguousarray(rows)).cast("B")
        state["stream"].write(buffer)
        state["digest"].update(buffer)
        state["rows"] += len(rows)

    try:
        for start in range(0, N_LINES, chunk_lines):
            coefficients = shell[start:start + chunk_lines].astype(np.int64)
            heads = coefficients @ basis
            if not np.all(np.sum(heads * heads, axis=1, dtype=np.int64) == 6 * scale):
                raise ValueError("Converted equatorial point has incorrect exact Cartesian norm")
            for state in states:
                retained = heads[~state["mask"][start:start + len(heads)]]
                rows = np.zeros((2 * len(retained), state["columns"]), dtype=dtype)
                rows[0::2, :basis.shape[1]] = retained
                rows[1::2, :basis.shape[1]] = -retained
                write(state, rows)
            if start % (chunk_lines * 32) == 0:
                print(json.dumps({"mother_lines_converted": start + len(heads),
                                  "elapsed_seconds": time.monotonic() - started}), flush=True)
        for state in states:
            equatorial_rows = state["rows"]
            for start in range(0, len(state["coefficients"]), chunk_lines):
                c = state["coefficients"][start:start + chunk_lines].astype(np.int64)
                heads = c @ basis
                tails = state["tails"][state["tail_indices"][start:start + len(c)]]
                if not np.all(np.sum(heads * heads, axis=1) == 6 * scale):
                    raise ValueError("Incorrect Cartesian cap-head norm")
                for head_sign, tail_sign in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                    rows = np.concatenate((head_sign * heads, tail_sign * tails), axis=1)
                    if not np.all(np.sum(rows * rows, axis=1) == 8 * scale):
                        raise ValueError("Incorrect complete Cartesian cap norm")
                    write(state, rows)
            cap_rows = state["rows"] - equatorial_rows
            for sign in (1, -1):
                rows = np.zeros((len(state["tails"]), state["columns"]), dtype=np.int64)
                rows[:, basis.shape[1]:] = sign * state["tails"]
                if not np.all(np.sum(rows * rows, axis=1) == 2 * scale):
                    raise ValueError("Incorrect pure-tail norm")
                write(state, rows)
            state["stream"].close()
            if state["rows"] != COUNTS[state["dimension"]]:
                raise ValueError("Incorrect final coordinate count")
            report = {
                "passed": True, "dimension": state["dimension"], "rows": state["rows"],
                "columns": state["columns"], "rank": state["dimension"],
                "rank_verification": "first assigned cap-head class spans rank48; pure tails have exact rank dimension-48",
                "format": f"raw {dtype.name}; little-endian; no header",
                "file": state["path"].name, "sha256": state["digest"].hexdigest(),
                "normalization": "Divide EACH ROW by its own Euclidean length",
                "head_columns": int(basis.shape[1]), "head_gram_scale": scale,
                "blocks": [{"kind": "equatorial", "first_row": 0, "rows": equatorial_rows,
                            "squared_norm": 6 * scale},
                           {"kind": "caps", "first_row": equatorial_rows, "rows": cap_rows,
                            "squared_norm": 8 * scale},
                           {"kind": "pure_tails", "first_row": equatorial_rows + cap_rows,
                            "rows": TAIL_SIZES[state["dimension"]], "squared_norm": 2 * scale}],
                "tail_root_system": state["tail_name"], "tail_repetition_factors": state["tail_factors"],
                "selected_union_lines": len(state["coefficients"]), "assigned_class_sizes": state["assigned_sizes"],
                "basis_sha256": sha256_file(basis_path), "canonical_mother_shell_sha256": receipt["sha256"],
                "checks": ["complete exact mother-shell membership and distinctness",
                           "every assigned line belongs to the mother shell",
                           "exact Cartesian basis Gram identity", "every generated Cartesian norm",
                           "published total and block counts", "disjoint assigned classes and tail lines"],
                "distinctness": "injective Cartesian head map; distinct mother lines; four signed caps per assigned line; disjoint equatorial/cap/pure-tail types",
                "pairwise_inner_products_checked_exhaustively": False,
                "pairwise_bound": "at most 1/2 after row-wise normalization, by the verified lifting pair classification",
            }
            with state["path"].with_suffix(".json").open("x") as stream:
                json.dump(report, stream, indent=2)
                stream.write("\n")
            print(json.dumps({"dimension": state["dimension"], "rows": state["rows"], "file": str(state["path"])}), flush=True)
    finally:
        for state in states:
            state["stream"].close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shell", required=True, type=Path)
    parser.add_argument("--basis", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dimensions", nargs="+", type=int, choices=range(49, 56), default=list(range(49, 56)))
    args = parser.parse_args()
    if len(set(args.dimensions)) != len(args.dimensions):
        parser.error("Dimensions must be distinct")
    export(args.shell, args.basis, args.output, args.dimensions)


if __name__ == "__main__":
    main()
