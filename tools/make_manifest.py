#!/usr/bin/env python3
"""Record the paths, sizes and SHA-256 digests of the source files."""
import argparse
from pathlib import Path
from package_files import files, sha256, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / "manifest.json").resolve()
    entries = []
    for path in files(root):
        if path.resolve() == output:
            continue
        if path.is_symlink():
            parser.error("Remove symbolic links before creating the manifest")
        entries.append({"path": path.relative_to(root).as_posix(),
                        "sha256": sha256(path), "bytes": path.stat().st_size})
    write_json(output, {"schema_version": 1, "scope": "file integrity",
                        "files": sorted(entries, key=lambda entry: entry["path"])})
    print(f"Indexed {len(entries)} files.")


if __name__ == "__main__":
    main()
