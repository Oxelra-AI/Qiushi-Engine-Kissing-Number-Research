#!/usr/bin/env python3
"""Export the complete final 32--37D and 39D integer Cartesian directions.

Rows in 32--37D have squared norm 32. In 39D the top layer has squared
norm 39 and the other layers have squared norm 32: normalize each row by
its own Euclidean norm. Dimension 38 uses a different construction.
"""
import argparse
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

import numpy as np

try:
    from .reference_checker import read_hex_file, rref, span_words
except ImportError:
    from reference_checker import read_hex_file, rref, span_words

ROOT = Path(__file__).resolve().parent
EXPECTED = {32: 347584, 33: 363968, 34: 384196, 35: 409676,
            36: 484760, 37: 498024, 39: 763668}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare(dimension):
    """Load the final witnesses, including all signed replacements."""
    if dimension not in EXPECTED:
        raise ValueError("Supported dimensions are 32--37 and 39")
    sources = {}

    def path(name):
        result = ROOT / name
        sources[result.relative_to(ROOT.parents[1]).as_posix()] = sha256(result)
        return result

    def read_json(name):
        return json.loads(path(name).read_text())

    def binary_supports(name):
        lines = [line.strip() for line in path(name).read_text().splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
        if any(len(line) != dimension or set(line) - {"0", "1"} for line in lines):
            raise ValueError("Invalid binary support string")
        # The 37D patch numbers coordinates from left to right, starting at 1.
        return [sum(1 << i for i, bit in enumerate(line) if bit == "1") for line in lines]

    patch = []
    top_length = 32
    if dimension in (35, 36):
        top = read_json("hadamard/data/top_code.json")
        basis = [sum(int(bit) << i for i, bit in enumerate(row))
                 for row in top["generator_matrix"]]
        top_words = span_words(rref(basis, 32))
        certificate = read_json(f"hadamard/data/d{dimension}_construction.json")
        support_path = path("hadamard/" + certificate["source_support_file"])
        old = read_hex_file(support_path)
        if sha256(support_path) != certificate["source_support_sha256"]:
            raise ValueError("Hadamard parent hash mismatch")
        if old != [int(word, 16) for word in certificate["old_supports_hex"]]:
            raise ValueError("Hadamard parent support mismatch")
        deleted = set(certificate["chamber"]["delete_old_support_indices"])
        retained = [word for i, word in enumerate(old) if i not in deleted]
        patch = [(int(row["support_hex"], 16), int(row["sign_hex"], 16))
                 for row in certificate["added_signed_vectors"]]
    else:
        claim_dimension = dimension if dimension in (33, 34, 39) else 33
        claim = next(row for row in read_json("data/claims.json")
                     if row["dimension"] == claim_dimension)
        top_length = claim["top_length"]
        basis = rref(read_hex_file(path(claim["kernel_file"])), top_length)
        kernel = span_words(basis)
        top_words = [representative ^ word
                     for representative in read_hex_file(path(claim["representatives_file"]))
                     for word in kernel]
        if dimension == 32:
            retained = binary_supports("data/d32_supports_binary.txt")
        elif dimension == 37:
            old = binary_supports("data/d37_supports_binary.txt")
            certificate = read_json("data/d37_signed_patch.json")
            if sha256(ROOT / "data/d37_supports_binary.txt") != certificate["base_seed_sha256"]:
                raise ValueError("37D parent hash mismatch")
            deleted = set(certificate["triple_indices_0based"])
            retained = [word for i, word in enumerate(old) if i not in deleted]
            patch = [(sum(1 << (i - 1) for i in row["support_1indexed"]),
                      sum(1 << (i - 1) for i in row["negative_1indexed"]))
                     for row in certificate["vectors"]]
        else:
            retained = read_hex_file(path(claim["support_file"]))
    if len(set(top_words)) != len(top_words) or any(not 0 <= w < 1 << top_length for w in top_words):
        raise ValueError("Invalid or repeated top sign word")
    if len(set(retained)) != len(retained) or any(w.bit_count() != 8 or not 0 <= w < 1 << dimension
                                                for w in retained):
        raise ValueError("Invalid or repeated retained support")
    if len(set(patch)) != len(patch) or any(w.bit_count() != 8 or not 0 <= w < 1 << dimension
                                          or negative < 0 or negative & ~w for w, negative in patch):
        raise ValueError("Invalid or repeated signed replacement")
    count = len(top_words) + 128 * len(retained) + len(patch) + 2 * dimension * (dimension - 1)
    if count != EXPECTED[dimension]:
        raise ValueError("Final construction count differs from the published result")
    return {"dimension": dimension, "expected_rows": count, "top_length": top_length,
            "top_words": top_words, "retained_supports": retained, "signed_patch": patch,
            "source_sha256": sources}


def generate(spec):
    n = spec["dimension"]
    rows = np.zeros((spec["expected_rows"], n), dtype=np.int8)
    top = np.asarray(spec["top_words"], dtype=np.uint64)
    bits = ((top[:, None] >> np.arange(spec["top_length"], dtype=np.uint64)) & 1).astype(np.int8)
    rows[:len(top), :spec["top_length"]] = 1 - 2 * bits
    position = len(top)
    signs = np.array([[(-2 if mask >> i & 1 else 2) for i in range(8)]
                     for mask in range(256) if mask.bit_count() % 2 == 0], dtype=np.int8)
    for mask in spec["retained_supports"]:
        columns = [i for i in range(n) if mask >> i & 1]
        rows[position:position + 128, columns] = signs
        position += 128
    for mask, negative in spec["signed_patch"]:
        rows[position] = [(-2 if negative >> i & 1 else 2) if mask >> i & 1 else 0
                          for i in range(n)]
        position += 1
    for i, j in combinations(range(n), 2):
        for a, b in product((-4, 4), repeat=2):
            rows[position, i], rows[position, j] = a, b
            position += 1
    if position != len(rows):
        raise ValueError("Generator did not fill the expected number of rows")
    return rows


def verify(rows, spec):
    """Check every Cartesian row against source-defined layer membership."""
    n = spec["dimension"]
    if rows.shape != (spec["expected_rows"], n) or rows.dtype.kind not in "iu":
        raise ValueError("Incorrect integer array shape")
    if np.any(rows < -4) or np.any(rows > 4):
        raise ValueError("Coordinate outside the construction range")
    absolute = np.abs(rows.astype(np.int16))
    weights = np.left_shift(np.uint64(1), np.arange(n, dtype=np.uint64))
    support = (rows != 0).astype(np.uint64) @ weights
    negative = (rows < 0).astype(np.uint64) @ weights
    top_mask = np.all(absolute[:, :spec["top_length"]] == 1, axis=1)
    top_mask &= np.all(absolute[:, spec["top_length"]:] == 0, axis=1)
    top_good = top_mask & np.isin(negative, np.asarray(spec["top_words"], dtype=np.uint64))
    middle_mask = np.all((absolute == 0) | (absolute == 2), axis=1)
    middle_mask &= np.count_nonzero(rows, axis=1) == 8
    retained_good = middle_mask & np.isin(support, np.asarray(spec["retained_supports"], dtype=np.uint64))
    retained_good &= np.count_nonzero(rows < 0, axis=1) % 2 == 0
    patch_set = set(spec["signed_patch"])
    patch_good = np.zeros(len(rows), dtype=bool)
    for i in np.flatnonzero(middle_mask & ~retained_good):
        patch_good[i] = (int(support[i]), int(negative[i])) in patch_set
    bottom_good = np.all((absolute == 0) | (absolute == 4), axis=1)
    bottom_good &= np.count_nonzero(rows, axis=1) == 2
    if not np.all(top_good | retained_good | patch_good | bottom_good):
        raise ValueError("A row is not a member of the source-defined construction")
    norms = np.sum(rows.astype(np.int32) ** 2, axis=1)
    if not np.all(norms == np.where(top_good, spec["top_length"], 32)):
        raise ValueError("Incorrect squared norm")
    unique = np.unique(np.ascontiguousarray(rows, dtype=np.int8).view(np.dtype(f"V{n}")).reshape(-1)).size
    if unique != len(rows):
        raise ValueError("Repeated Cartesian row")
    layer_counts = {"top": int(top_good.sum()), "retained_middle": int(retained_good.sum()),
                    "signed_replacement": int(patch_good.sum()), "bottom": int(bottom_good.sum())}
    expected_layers = {"top": len(spec["top_words"]), "retained_middle": 128 * len(spec["retained_supports"]),
                       "signed_replacement": len(spec["signed_patch"]), "bottom": 2 * n * (n - 1)}
    if layer_counts != expected_layers:
        raise ValueError("Incorrect source layer counts")
    values, counts = np.unique(norms, return_counts=True)
    return {"passed": True, "all_rows_exact_source_members": True,
            "all_squared_norms_exact": True, "all_rows_unique": True,
            "unique_rows": int(unique), "layer_rows": layer_counts,
            "squared_norm_counts": {str(int(q)): int(count) for q, count in zip(values, counts)},
            "full_pairwise_inner_products_checked": False,
            "scope": "Exact source membership, norms, uniqueness and complete layer counts"}


def export(dimension, output_dir, csv=False):
    output_dir = Path(output_dir)
    names = [f"configuration{dimension}.i8.gz", f"configuration{dimension}.json"]
    if csv:
        names.append(f"configuration{dimension}.csv.gz")
    if any((output_dir / name).exists() for name in names):
        raise FileExistsError("Choose new output paths; existing exports are retained")
    spec = prepare(dimension)
    rows = generate(spec)
    checked = verify(rows, spec)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = memoryview(rows).cast("B")
    binary_path = output_dir / names[0]
    with binary_path.open("xb") as destination:
        with gzip.GzipFile(filename="", mode="wb", fileobj=destination, mtime=0, compresslevel=6) as stream:
            stream.write(raw)
    with gzip.open(binary_path, "rb") as stream:
        if stream.read() != raw:
            raise ValueError("Binary gzip round-trip changed the coordinate bytes")
    artifacts = {binary_path.name: {"sha256": sha256(binary_path), "bytes": binary_path.stat().st_size}}
    if csv:
        csv_path = output_dir / names[2]
        with csv_path.open("xb") as destination:
            with gzip.GzipFile(filename="", mode="wb", fileobj=destination, mtime=0, compresslevel=6) as stream:
                np.savetxt(stream, rows, fmt="%d", delimiter=",")
        with gzip.open(csv_path, "rt") as stream:
            decoded = np.loadtxt(stream, dtype=np.int64, delimiter=",")
        if not np.array_equal(decoded, rows):
            raise ValueError("CSV gzip round-trip changed the Cartesian coordinates")
        artifacts[csv_path.name] = {"sha256": sha256(csv_path), "bytes": csv_path.stat().st_size}
        checked["csv_binary_coordinates_equal"] = True
    norms = checked["squared_norm_counts"]
    report = {"dimension": dimension, "coordinate_columns": dimension,
              "rows": len(rows), "expected_rows": EXPECTED[dimension], "complete": True,
              "representation": "integer Cartesian directions, not Gram-basis coefficients",
              "binary_format": "gzip-compressed signed int8, row-major, no header",
              "csv_format": "gzip-compressed integer CSV, no header" if csv else None,
              "unit_normalization": "divide EACH row by the square root of its own squared norm",
              "squared_norm": int(next(iter(norms))) if len(norms) == 1 else None,
              "squared_norm_counts": norms, "raw_bytes": rows.nbytes,
              "raw_sha256": hashlib.sha256(raw).hexdigest(),
              "coordinate_minimum": int(rows.min()), "coordinate_maximum": int(rows.max()),
              "verification": checked, "artifacts": artifacts,
              "source_sha256": spec["source_sha256"],
              "generator": "constructions/codes/export_vectors.py"}
    with (output_dir / names[1]).open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", required=True, type=int, choices=sorted(EXPECTED))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--csv", action="store_true", help="also write and verify integer CSV gzip")
    args = parser.parse_args()
    print(json.dumps(export(args.dimension, args.output_dir, args.csv), indent=2))


if __name__ == "__main__":
    main()
