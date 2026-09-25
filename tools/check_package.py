#!/usr/bin/env python3
"""Check file paths, sizes and SHA-256 digests against the source manifest."""
import argparse
import json
from pathlib import Path
from package_files import contained_file, files, sha256, write_json


def check(root, manifest):
    root = Path(root).resolve()
    manifest = Path(manifest).resolve()
    index = json.loads(manifest.read_text())
    if index.get("schema_version") != 1:
        raise ValueError("Unsupported manifest schema")
    failures, indexed = [], set()
    for entry in index["files"]:
        relative = entry["path"]
        if relative in indexed:
            failures.append({"path": relative, "category": "duplicate_entry"})
            continue
        indexed.add(relative)
        try:
            path = contained_file(root, relative)
        except ValueError:
            failures.append({"path": "[invalid indexed path]", "category": "invalid_path"})
            continue
        if not path.is_file():
            failures.append({"path": relative, "category": "missing_file"})
        elif path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            failures.append({"path": relative, "category": "changed_file"})
    for path in files(root):
        if path.resolve() != manifest and path.relative_to(root).as_posix() not in indexed:
            failures.append({"path": path.relative_to(root).as_posix(), "category": "unindexed_file"})
    return {"passed": not failures, "scope": "file integrity",
            "indexed_files": len(indexed), "failures": failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = check(args.root, args.manifest or args.root / "manifest.json")
    except (OSError, ValueError, KeyError, TypeError):
        parser.error("Cannot read a valid package manifest")
    if args.output:
        write_json(args.output, report)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
