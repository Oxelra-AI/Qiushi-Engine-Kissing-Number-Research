#!/usr/bin/env python3
"""Verify all P48p shell vectors and sort one exact representative per line."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

ROOT = Path(__file__).resolve().parent
SHELL_ROWS = 52416000


def build(shards, output, chunk_pairs=32768, follow=False):
    shards, output = Path(shards), Path(output)
    report_path = output.with_name(output.name + ".json")
    if output.exists() or report_path.exists():
        raise FileExistsError("Choose new index and report paths")
    paths = sorted(shards.glob("part-*.i8"), key=lambda p: int(p.stem.split("-")[-1]))
    if not paths:
        raise ValueError("No native shell shards found")
    if not follow:
        receipt = json.loads((shards / "enumeration.json").read_text())
        if str(receipt["stopped"]).lower() not in ("false", "0") or int(receipt["rows"]) != SHELL_ROWS:
            raise ValueError("Enumeration receipt does not report a full shell")
    g = np.load(ROOT / "data/p48p_gram.npy", allow_pickle=False).astype(np.int32)
    # This bound covers both matrix multiplication and the final dot product.
    bound = 48 ** 2 * 128 ** 2 * max(abs(int(x)) for x in g.flat)
    if bound > np.iinfo(np.int32).max:
        raise ValueError("Gram products exceed int32 safety bound")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.truncate((SHELL_ROWS // 2) * 48)
    lines = np.memmap(output, mode="r+", dtype=np.int8, shape=(SHELL_ROWS // 2, 48))
    started = time.monotonic()
    position, maximum = 0, 0
    source_hashes = {}
    cursors = {path: 0 for path in paths}
    digests = {path: hashlib.sha256() for path in paths}
    identities = {path: (path.stat().st_dev, path.stat().st_ino) for path in paths}
    while True:
        prior_position = position
        for path in paths:
            before = path.stat()
            available = before.st_size // 96
            if (before.st_dev, before.st_ino) != identities[path] or available < cursors[path]:
                raise ValueError("Native shard was replaced or truncated")
            if not available:
                continue
            pairs = np.memmap(path, mode="r", dtype=np.int8, shape=(available, 2, 48))
            for start in range(cursors[path], available, chunk_pairs):
                chunk = pairs[start:min(start + chunk_pairs, available)]
                digests[path].update(memoryview(chunk).cast("B"))
                both = chunk.astype(np.int32)
                if not np.all(both[:, 0] == -both[:, 1]):
                    raise ValueError("Non-antipodal adjacent pair in " + path.name)
                points = both[:, 0]
                if not np.all(np.sum((points @ g) * points, axis=1, dtype=np.int32) == 6):
                    raise ValueError("Invalid exact shell norm in " + path.name)
                first = np.argmax(points != 0, axis=1)
                signs = np.sign(points[np.arange(len(points)), first])
                normalized = points * signs[:, None]
                maximum = max(maximum, int(np.abs(normalized).max()))
                if position + len(points) > len(lines):
                    raise ValueError("Too many mother-shell rows")
                lines[position:position + len(points)] = normalized
                position += len(points)
            cursors[path] = available
        if position != prior_position:
            print(json.dumps({"verified_lines": position, "elapsed_seconds": time.monotonic() - started}), flush=True)
        receipt_path = shards / "enumeration.json"
        if receipt_path.exists():
            try:
                receipt = json.loads(receipt_path.read_text())
            except json.JSONDecodeError:
                if not follow:
                    raise
            else:
                if str(receipt["stopped"]).lower() not in ("false", "0") or int(receipt["rows"]) != SHELL_ROWS:
                    raise ValueError("Enumeration receipt does not report a full shell")
                if all(path.stat().st_size == cursors[path] * 96 for path in paths):
                    break
        if not follow:
            raise ValueError("Incomplete or concurrently changing shell")
        time.sleep(2)
    for path in paths:
        before = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(8 << 20), b""):
                digest.update(chunk)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise ValueError("Input shard changed during final verification")
        if digest.digest() != digests[path].digest():
            raise ValueError("An already indexed shard prefix was changed")
        source_hashes[path.name] = digest.hexdigest()
    if position != SHELL_ROWS // 2:
        raise ValueError("Incomplete line index")
    keys = lines.view(np.dtype("V48")).reshape(-1)
    keys.sort(kind="quicksort")
    digest = hashlib.sha256()
    previous = None
    for start in range(0, len(lines), chunk_pairs):
        chunk = keys[start:start + chunk_pairs]
        if (previous is not None and previous == chunk[0]) or np.any(chunk[1:] == chunk[:-1]):
            raise ValueError("Repeated antipodal line")
        previous = chunk[-1].copy()
        digest.update(memoryview(lines[start:start + chunk_pairs]).cast("B"))
    lines.flush()
    report = {"passed": True, "rows_in_full_shell": SHELL_ROWS, "canonical_lines": len(lines),
              "format": "raw signed int8; 48 catalogue-basis coefficients per row",
              "canonical_sign": "first nonzero catalogue coefficient positive",
              "order": "lexicographic unsigned-byte order of 48-byte rows",
              "gram_norm": 6, "all_antipodal_pairs_checked": True,
              "all_exact_norms_checked": True, "all_lines_distinct": True,
              "maximum_absolute_coefficient": maximum, "int32_product_bound": bound,
              "sha256": digest.hexdigest(), "source_shard_sha256": source_hashes,
              "completeness_basis": "52416000 distinct norm-six lattice vectors, matching the proved shell size",
              "elapsed_seconds": time.monotonic() - started}
    with report_path.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shards", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--follow", action="store_true", help="verify immutable prefixes while native shards grow")
    args = parser.parse_args()
    print(json.dumps(build(args.shards, args.output, follow=args.follow), indent=2))


if __name__ == "__main__":
    main()
