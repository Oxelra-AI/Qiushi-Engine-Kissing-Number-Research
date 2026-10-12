#!/usr/bin/env python3
"""Independently reconstruct every 49--55D binary row in bounded chunks.

The common mother-shell Cartesian conversion is performed once for all seven
files. Exact source equality proves membership and transfers distinctness
from the independently verified canonical line index. No global output sort
or all-pairs calculation is performed. NumPy and SymPy are required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import sympy as sp

try:
    from .verify import tail_roots
except ImportError:
    from verify import tail_roots

ROOT = Path(__file__).resolve().parent
N_LINES = 26208000
COUNTS = {49: 52430156, 50: 52458468, 51: 52500930, 52: 52585772,
          53: 52698696, 54: 52923774, 55: 53301140}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(rows):
    first = np.argmax(rows != 0, axis=1)
    return rows * np.sign(rows[np.arange(len(rows)), first])[:, None]


def independent_row_indices(rows, wanted):
    """Find a small witness modulo a prime; its integer minor is checked later."""
    prime, pivots, chosen = 65521, {}, []
    for index, row in enumerate(rows):
        values = [int(x) % prime for x in row]
        for pivot in sorted(pivots):
            coefficient = values[pivot]
            values = [(x - coefficient * y) % prime for x, y in zip(values, pivots[pivot])]
        if any(values):
            pivot = next(j for j, value in enumerate(values) if value)
            inverse = pow(values[pivot], -1, prime)
            pivots[pivot] = [(x * inverse) % prime for x in values]
            chosen.append(index)
        if len(chosen) == wanted:
            return chosen
    raise ValueError("Could not find the expected full-rank source witness")


def verify(shell_path, basis_path, directory, dimensions=range(49, 56), chunk_lines=32768):
    if chunk_lines <= 0:
        raise ValueError("chunk_lines must be positive")
    shell_path, basis_path, directory = map(Path, (shell_path, basis_path, directory))
    started = time.monotonic()
    receipt = json.loads(shell_path.with_name(shell_path.name + ".json").read_text())
    if (not receipt.get("passed") or receipt.get("canonical_lines") != N_LINES
            or receipt.get("all_lines_distinct") is not True):
        raise ValueError("The source must be a complete verified canonical line index")
    if shell_path.stat().st_size != N_LINES * 48 or sha256(shell_path) != receipt["sha256"]:
        raise ValueError("Canonical line index does not match its verification receipt")
    saved = json.loads(basis_path.read_text())
    basis_digest = sha256(basis_path)
    b = np.asarray(saved["basis_B"], dtype=np.int64)
    g = np.load(ROOT / "data/p48p_gram.npy", allow_pickle=False).astype(np.int64)
    if b.shape != (48, 48) or saved["basis_scale"] != 6:
        raise ValueError("Expected the released square Cartesian basis of Gram scale six")
    if sp.Matrix(b.tolist()) * sp.Matrix(b.tolist()).T != 6 * sp.Matrix(g.tolist()):
        raise ValueError("Exact Cartesian Gram identity failed")
    c = np.load(ROOT / "data/class_p48_7077.npy", allow_pickle=False).astype(np.int64)
    basis = 2 * b
    witness = independent_row_indices(c, 48)
    head_minor = int(sp.Matrix((c[witness] @ basis).tolist()).det())
    if head_minor == 0:
        raise ValueError("The mother class does not have exact rank 48")
    shell = np.memmap(shell_path, dtype=np.int8, mode="r", shape=(N_LINES, 48))
    shell_keys = shell.view("V48").reshape(-1)
    states = []

    try:
        for dimension in dimensions:
            metadata = json.loads((directory / f"configuration{dimension}.json").read_text())
            if (metadata.get("passed") is not True or metadata.get("dimension") != dimension
                    or metadata.get("rank") != dimension
                    or metadata.get("basis_sha256") != basis_digest
                    or metadata.get("canonical_mother_shell_sha256") != receipt["sha256"]):
                raise ValueError("Incorrect export identity or source digests")
            roots, q, name = tail_roots(dimension - 48)
            factors = metadata["tail_repetition_factors"]
            if not factors or any(type(x) is not int or x <= 0 for x in factors) or q * sum(x*x for x in factors) != 48:
                raise ValueError("Incorrect integer tail Gram scaling")
            representatives = np.array(sorted(set(map(tuple, canonical(roots)))), dtype=np.int64)
            tails = np.concatenate([factor * representatives for factor in factors], axis=1)
            if not np.array_equal(q * (tails @ tails.T), 48 * (representatives @ representatives.T)):
                raise ValueError("Embedded tail unit Gram differs from the source")
            tail_rank = int(sp.Matrix(tails.tolist()).rank())
            if tail_rank != dimension - 48:
                raise ValueError("Incorrect exact tail rank")
            matrices = ([np.eye(48, dtype=np.int64)] if dimension == 49 else
                        np.load(ROOT / f"data/dim{dimension}_group_elems.npy", allow_pickle=False).astype(np.int64))
            if len(matrices) != len(tails):
                raise ValueError("Tail lines are not assigned injectively to source images")
            assigned = {}
            for tail_index, a in enumerate(matrices):
                if not np.array_equal(a @ g @ a.T, g):
                    raise ValueError("Source image is not a Gram isometry")
                image = canonical(c @ a)
                if np.any(np.abs(image) > 127):
                    raise ValueError("Coefficient key would overflow")
                for row in image.astype(np.int8):
                    assigned.setdefault(row.tobytes(), tail_index)
            keys = sorted(assigned)
            coefficients = np.frombuffer(b"".join(keys), dtype=np.int8).reshape(-1, 48)
            positions = np.searchsorted(shell_keys, coefficients.view("V48").reshape(-1))
            if np.any(positions >= N_LINES) or not np.array_equal(shell_keys[positions], coefficients.view("V48").reshape(-1)):
                raise ValueError("An assigned source line is absent from the canonical index")
            mask = np.zeros(N_LINES, dtype=bool)
            mask[positions] = True
            expected_count = 2*N_LINES + 2*len(keys) + 2*len(tails)
            columns = 48 + tails.shape[1]
            if expected_count != COUNTS[dimension] or metadata["rows"] != expected_count or metadata["columns"] != columns:
                raise ValueError("Incorrect complete count or Cartesian column count")
            equator_count = 2 * (N_LINES - len(keys))
            cap_count = 4 * len(keys)
            blocks = [{"kind": "equatorial", "first_row": 0, "rows": equator_count,
                       "squared_norm": 144},
                      {"kind": "caps", "first_row": equator_count, "rows": cap_count,
                       "squared_norm": 192},
                      {"kind": "pure_tails", "first_row": equator_count + cap_count,
                       "rows": 2 * len(tails), "squared_norm": 48}]
            if metadata.get("blocks") != blocks or metadata.get("head_columns") != 48:
                raise ValueError("Incorrect row-block or normalization metadata")
            source_chunk_lines = metadata.get("source_chunk_lines", 32768)
            if type(source_chunk_lines) is not int or source_chunk_lines <= 0:
                raise ValueError("Invalid cap source chunk length")
            path = directory / f"configuration{dimension}.i8"
            before = path.stat()
            if before.st_size != expected_count * columns:
                raise ValueError("Incomplete raw binary file")
            states.append({"dimension": dimension, "metadata": metadata, "mask": mask,
                           "coefficients": coefficients, "tail_indices": [assigned[key] for key in keys],
                           "tails": tails, "tail_rank": tail_rank, "columns": columns,
                           "source_chunk_lines": source_chunk_lines,
                           "path": path, "before": before, "stream": path.open("rb"),
                           "digest": hashlib.sha256(), "rows": 0})

        def compare(state, expected):
            if np.any(expected < -12) or np.any(expected > 12):
                raise ValueError("Unexpected Cartesian coordinate bound")
            expected_bytes = np.ascontiguousarray(expected, dtype=np.int8).tobytes()
            actual = state["stream"].read(len(expected_bytes))
            if actual != expected_bytes:
                raise ValueError(f"Source reconstruction mismatch in dimension {state['dimension']} at row {state['rows']}")
            state["digest"].update(actual)
            state["rows"] += len(expected)

        for start in range(0, N_LINES, chunk_lines):
            heads = shell[start:start + chunk_lines].astype(np.int64) @ basis
            if not np.all(np.sum(heads * heads, axis=1) == 144):
                raise ValueError("A mother-shell head has an incorrect exact norm")
            for state in states:
                retained = heads[~state["mask"][start:start + len(heads)]]
                expected = np.zeros((2*len(retained), state["columns"]), dtype=np.int8)
                expected[::2, :48], expected[1::2, :48] = retained, -retained
                compare(state, expected)
            if start % (chunk_lines * 128) == 0:
                print(json.dumps({"verified_mother_lines": start + len(heads),
                                  "elapsed_seconds": time.monotonic() - started}), flush=True)

        results = []
        for state in states:
            equator_count = state["rows"]
            # The exporter records the size of each four-sign source chunk.
            cap_chunk = state["source_chunk_lines"]
            for start in range(0, len(state["coefficients"]), cap_chunk):
                coefficients = state["coefficients"][start:start + cap_chunk].astype(np.int64)
                heads = coefficients @ basis
                tails = state["tails"][state["tail_indices"][start:start + len(coefficients)]]
                for head_sign, tail_sign in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                    expected = np.concatenate((head_sign * heads, tail_sign * tails), axis=1)
                    if not np.all(np.sum(expected * expected, axis=1) == 192):
                        raise ValueError("Incorrect reconstructed cap norm")
                    compare(state, expected)
            cap_count = state["rows"] - equator_count
            for sign in (1, -1):
                expected = np.zeros((len(state["tails"]), state["columns"]), dtype=np.int64)
                expected[:, 48:] = sign * state["tails"]
                if not np.all(np.sum(expected * expected, axis=1) == 48):
                    raise ValueError("Incorrect pure-tail norm")
                compare(state, expected)
            if state["stream"].read(1) or state["rows"] != COUNTS[state["dimension"]]:
                raise ValueError("Incorrect final binary length")
            digest = state["digest"].hexdigest()
            if digest != state["metadata"]["sha256"]:
                raise ValueError("Export digest does not match independently read bytes")
            after = state["path"].stat()
            fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
            if any(getattr(state["before"], field) != getattr(after, field) for field in fields):
                raise ValueError("Input changed during verification")
            results.append({"dimension": state["dimension"], "coordinate_columns": state["columns"],
                            "rows": state["rows"], "sha256": digest,
                            "source_reconstruction_equal": True, "all_exact_norms": True,
                            "equatorial_rows": equator_count, "cap_rows": cap_count,
                            "pure_tail_rows": 2*len(state["tails"]),
                            "exact_rank": 48 + state["tail_rank"],
                            "all_normalized_directions_distinct": True})
        return {"passed": True, "results": results,
                "head_rank_witness_source_rows": witness, "head_minor_determinant": str(head_minor),
                "rank_proof": "The complete first image of the rank-48 mother class is present in cap pairs; opposite-tail sums span its heads. Pure tails have exact rank k in a disjoint coordinate block.",
                "distinctness_proof": "Exact source equality; verified distinct mother lines and injective Cartesian head map; four independent sign choices per disjoint assigned line; distinct tail lines; disjoint zero-head/zero-tail layer patterns.",
                "source_index_sha256": receipt["sha256"], "basis_sha256": basis_digest,
                "full_pairwise_inner_products_checked": False,
                "elapsed_seconds": time.monotonic() - started}
    finally:
        for state in states:
            state["stream"].close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shell", required=True, type=Path)
    parser.add_argument("--basis", required=True, type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("Choose a new report path")
    result = verify(args.shell, args.basis, args.directory)
    with args.report.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
