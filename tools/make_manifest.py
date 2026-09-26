#!/usr/bin/env python3
"""Record the paths, sizes and SHA-256 digests of the source files."""
import argparse
from pathlib import Path
from package_files import approved_paths, write_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--include", action="append", default=[], metavar="PATH",
                        help="Explicitly add a reviewed relative file path")
    parser.add_argument("--exclude", action="append", default=[], metavar="PATH",
                        help="Explicitly remove a relative file path")
    args = parser.parse_args()
    root = args.root.resolve()
    names = (set(approved_paths(root)) | set(args.include)) - set(args.exclude)
    write_manifest(root, names, args.output)
    print(f"Indexed {len(names)} files.")


if __name__ == "__main__":
    main()
