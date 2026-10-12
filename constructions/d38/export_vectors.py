#!/usr/bin/env python3
"""Export all 591900 points as integer directions in a 38-dimensional subspace."""

import argparse
import gzip
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from verify_dimension38 import shell  # noqa: E402


def integer_rows(data, added_path):
    """The isometry (x,y) -> (x,y/sqrt(2),y/sqrt(2)) rationalizes the caps."""
    _, lines = shell(data)
    labels = np.loadtxt(data / "class_labels.txt", dtype=np.int64)
    triples = np.loadtxt(data / "triples.txt", dtype=np.int64)
    directions = np.loadtxt(data / "dim14_directions.txt", delimiter=",", dtype=np.int64)
    keep = np.loadtxt(data / "axis_keep.txt", dtype=np.int64)
    rotation = np.array([[int(v) for v in line.split()]
                         for line in (data / "axis_rotation.txt").read_text().splitlines()
                         if line.strip()], dtype=object)
    denominator = int((data / "axis_rotation_D.txt").read_text())
    if not np.array_equal(rotation @ rotation.T,
                          denominator**2 * np.eye(14, dtype=object)):
        raise ValueError("The supplied rotation is not orthogonal")
    if directions.shape != (1932, 14) or not np.all((directions**2).sum(1) == 8):
        raise ValueError("Unexpected tail directions")
    added = np.loadtxt(added_path, dtype=np.int64)
    if added.shape != (144, 24) or not np.all((added**2).sum(1) == 48):
        raise ValueError("Unexpected equatorial directions")

    rows = np.zeros((591900, 52), dtype=np.int64)
    cursor = 0
    for label in range(3):
        tails = directions[triples[labels, label]]
        for sign in (1, -1):
            block = rows[cursor:cursor + len(lines)]
            block[:, :24] = sign * lines
            block[:, 24:38] = tails
            block[:, 38:] = tails
            cursor += len(lines)
    cap_end = cursor
    rotated = directions[keep].astype(object) @ rotation.T
    if any(abs(int(v)) > np.iinfo(np.int64).max for v in rotated.flat):
        raise ValueError("Axis coordinate exceeds signed int64")
    rows[cursor:cursor + len(keep), 24:38] = rotated.astype(np.int64)
    rows[cursor:cursor + len(keep), 38:] = rotated.astype(np.int64)
    cursor += len(keep)
    axis_end = cursor
    for sign in (1, -1):
        rows[cursor:cursor + len(added), :24] = sign * added
        cursor += len(added)
    if cursor != len(rows):
        raise ValueError("Incomplete point set")
    if not np.all(np.einsum("ij,ij->i", rows[:cap_end], rows[:cap_end]) == 48):
        raise ValueError("Cap norm mismatch")
    if not np.all(np.einsum("ij,ij->i", rows[axis_end:], rows[axis_end:]) == 48):
        raise ValueError("Equatorial norm mismatch")
    for row in rows[cap_end:axis_end]:
        if sum(int(x)**2 for x in row) != 16 * denominator**2:
            raise ValueError("Axis norm mismatch")
    distinct = len(np.unique(rows.view(np.dtype((np.void, rows.dtype.itemsize * 52)))))
    if distinct != len(rows):
        raise ValueError("Repeated direction")
    metadata = {
        "dimension": 38, "ambient_coordinates": 52, "rows": len(rows),
        "coordinate_type": "integer Cartesian directions; normalize each row by its Euclidean norm",
        "binary_dtype": "little-endian signed int64", "binary_shape": [len(rows), 52],
        "csv": "52 comma-separated integers per line, no header",
        "layers": [
            {"name": "caps", "start": 0, "stop": cap_end, "squared_norm": 48},
            {"name": "rotated axes", "start": cap_end, "stop": axis_end,
             "squared_norm": str(16 * denominator**2), "normalizing_divisor": str(4 * denominator)},
            {"name": "added equator", "start": axis_end, "stop": len(rows), "squared_norm": 48}],
        "isometry": "(x,y) -> (x,y/sqrt(2),y/sqrt(2)) from R24+R14 into R24+R14+R14",
        "axis_rotation_denominator": str(denominator),
        "checks": {"all_norms": True, "distinct_rows": distinct,
                   "all_tail_copies_equal": bool(np.array_equal(rows[:, 24:38], rows[:, 38:])),
                   "exact_rational_rotation": True},
    }
    return rows, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, metadata = integer_rows(ROOT / "constructions/d38/base-data",
                                  ROOT / "constructions/d38/added-lines.txt")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("configuration38.csv.gz", "configuration38.i64.gz", "configuration38.json"):
        if (args.output_dir / name).exists():
            parser.error("Existing export: " + name)
    with gzip.open(args.output_dir / "configuration38.csv.gz", "wt", compresslevel=6) as stream:
        np.savetxt(stream, rows, fmt="%d", delimiter=",")
    with gzip.open(args.output_dir / "configuration38.i64.gz", "wb", compresslevel=6) as stream:
        for start in range(0, len(rows), 8192):
            stream.write(rows[start:start + 8192].astype("<i8").tobytes())
    with (args.output_dir / "configuration38.json").open("x") as stream:
        json.dump(metadata, stream, indent=2)
        stream.write("\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
