#!/usr/bin/env python3
"""Independently verify raw 48-column signed-int8 section coordinates.

SageMath prepares exact inverse-basis congruences; NumPy checks every point
in bounded chunks. Completeness uses the proved cardinalities, not an
enumerator's receipt. This checker does not perform an all-pairs calculation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

import numpy as np


ROOT = Path(__file__).resolve().parent
EXPECTED_ROWS = {43: 2553792, 45: 7380090}
FIBRE_ROWS = 2460030


def _text_matrix(text, marker, count, width):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(marker)) + 1
    rows = [[int(x) for x in re.findall(r"-?\d+", line)]
            for line in lines[start:start + count]]
    if len(rows) != count or any(len(row) != width for row in rows):
        raise ValueError("Invalid source matrix: " + marker)
    return rows


def prepare_checks(dimension):
    """Derive exact lattice/coset membership directly from the stored basis."""
    from sage.all import ZZ, matrix, vector

    read = lambda name: json.loads((ROOT / name).read_text())
    if dimension == 43:
        text = (ROOT / "d43/data/parent-section.txt").read_text()
        g = matrix(ZZ, _text_matrix(text, "ambient Gram G", 48, 48))
        t = matrix(ZZ, _text_matrix(text, "coefficient rows w.r.t.", 8, 48))[:5]
        b = matrix(ZZ, read("d43/data/euclidean-basis.json")["basis_B"])
        scale, squared_norm = 96, 576
    elif dimension == 45:
        g = matrix(ZZ, read("d45/data/gram.json")["ambient_G"])
        t = matrix(ZZ, read("d45/data/compact.json")["section_basis_T_rows"])
        b = matrix(ZZ, read("d45/data/parent.json")["basis_scaled_by_sqrt12"])
        scale, squared_norm = 12, 4416
    else:
        raise ValueError("Dimension must be 43 or 45")
    if b * b.transpose() != scale * g or t.rank() != 48 - dimension:
        raise ValueError("Source basis Gram or section rank mismatch")
    inverse = scale * b.inverse()
    if any(x not in ZZ for x in inverse.list()):
        raise ValueError("Scaled inverse basis must be integral")
    if b * inverse != scale * matrix.identity(ZZ, 48):
        raise ValueError("Inverse basis identity failed")
    if dimension == 43:
        residues = [[0] * 48]
    else:
        if t * g * t.transpose() != 8 * matrix.identity(ZZ, 3) - 2 * matrix.ones(ZZ, 3):
            raise ValueError("Incorrect 45D section Gram")
        residues = [[int(x % 96) for x in -12 * vector(ZZ, [1 + (i == j) for j in range(3)]) * t]
                    for i in range(3)]
    if len(set(map(tuple, residues))) != len(residues):
        raise ValueError("Fibre congruences must be distinct")
    return {
        "dimension": dimension, "squared_norm": squared_norm,
        "expected_rows": EXPECTED_ROWS[dimension], "modulus": 96,
        "inverse_scaled": [[int(x) for x in row] for row in inverse.rows()],
        "orthogonal_to_rows": [[int(x) for x in row] for row in (t * b).rows()],
        "residues": residues,
    }


def arithmetic_dtype(inverse, orthogonal):
    """Bound every dot product for any signed-int8 input, before NumPy casts."""
    bound = 48 * 128 ** 2
    for rows in (list(zip(*inverse)), orthogonal):
        for row in rows:
            bound = max(bound, 128 * sum(abs(int(x)) for x in row))
    if bound <= np.iinfo(np.int32).max:
        return np.dtype(np.int32)
    if bound <= np.iinfo(np.int64).max:
        return np.dtype(np.int64)
    raise ValueError("Exact products exceed int64; refusing possible overflow")


def verify(input_path, checks, chunk_rows=65536):
    """Return a report; a partial, duplicate, or invalid input never passes.

    For 43D, r*(96 B^-1) = 0 mod 96 is lattice membership.
    For 45D, r*(12 B^-1) = -12*(e_i+1)*T mod 96 gives an integral
    z=(r B^-1+(e_i+1)T)/8. Orthogonality then forces zGT^t=e_i,
    and the checked projected norm forces zGz^t=6 exactly.
    """
    if chunk_rows <= 0:
        raise ValueError("chunk_rows must be positive")
    input_path = Path(input_path)
    before = input_path.stat()
    if not input_path.is_file() or before.st_size % 48:
        raise ValueError("Input must be a raw binary file of complete 48-byte rows")
    count = before.st_size // 48
    dtype = arithmetic_dtype(checks["inverse_scaled"], checks["orthogonal_to_rows"])
    inverse = np.asarray(checks["inverse_scaled"], dtype=dtype)
    orthogonal = np.asarray(checks["orthogonal_to_rows"], dtype=dtype)
    residues = np.asarray(checks["residues"], dtype=dtype)
    rows = np.memmap(input_path, mode="r", dtype=np.int8, shape=(count, 48)) if count else np.empty((0, 48), dtype=np.int8)
    bad_norm = bad_orthogonal = bad_membership = 0
    fibre_counts = [0] * len(residues)
    digest = hashlib.sha256()
    for start in range(0, count, chunk_rows):
        raw = rows[start:start + chunk_rows]
        digest.update(memoryview(raw).cast("B"))
        block = raw.astype(dtype)
        norms = np.sum(block * block, axis=1, dtype=dtype)
        bad_norm += int(np.count_nonzero(norms != checks["squared_norm"]))
        products = block @ orthogonal.T
        bad_orthogonal += int(np.count_nonzero(np.any(products != 0, axis=1)))
        coefficients = (block @ inverse) % checks["modulus"]
        matches = np.zeros(len(block), dtype=np.int8)
        for i, residue in enumerate(residues):
            match = np.all(coefficients == residue, axis=1)
            fibre_counts[i] += int(np.count_nonzero(match))
            matches += match
        bad_membership += int(np.count_nonzero(matches != 1))
    # Fixed-width byte records compare all 48 coordinates exactly. This is
    # intentionally not a hash-based uniqueness claim; the sort uses memory
    # proportional to the input (about 354 MB of raw rows for full 45D).
    unique_count = int(np.unique(rows.view(np.dtype("V48")).reshape(-1)).size)
    after = input_path.stat()
    stable = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    results = {
        "expected_row_count": count == checks["expected_rows"],
        "all_squared_norms": bad_norm == 0,
        "all_orthogonal": bad_orthogonal == 0,
        "all_lattice_and_fibre_memberships": bad_membership == 0,
        "all_unique": unique_count == count,
        "input_unchanged_during_verification": stable,
    }
    if checks["dimension"] == 45:
        results["expected_fibre_counts"] = fibre_counts == [FIBRE_ROWS] * 3
    return {
        "passed": all(results.values()), "checks": results,
        "dimension": checks["dimension"], "format": "raw signed int8; 48 columns; no header",
        "input": str(input_path.resolve()), "input_bytes": before.st_size,
        "sha256": digest.hexdigest(), "rows": count, "unique_rows": unique_count,
        "expected_rows": checks["expected_rows"], "squared_norm": checks["squared_norm"],
        "invalid_norm_rows": bad_norm, "nonorthogonal_rows": bad_orthogonal,
        "invalid_membership_rows": bad_membership,
        "fibre_rows": fibre_counts if checks["dimension"] == 45 else None,
        "expected_rows_per_fibre": FIBRE_ROWS if checks["dimension"] == 45 else None,
        "integer_arithmetic": dtype.name, "pairwise_inner_products_checked": False,
        "completeness_basis": "exact membership, distinctness, and proved cardinalities",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", required=True, type=int, choices=(43, 45))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="new JSON verification report")
    parser.add_argument("--chunk-rows", type=int, default=65536)
    args = parser.parse_args()
    if args.chunk_rows <= 0:
        parser.error("--chunk-rows must be positive")
    if args.output.exists():
        raise FileExistsError("Choose a new report path; existing reports are retained")
    report = verify(args.input, prepare_checks(args.dimension), args.chunk_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
