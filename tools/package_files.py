"""File enumeration shared by the portable package tools."""
from pathlib import Path
import hashlib
import json

IGNORED_DIRECTORIES = {".git", ".venv", "__pycache__", ".pytest_cache"}


def files(root):
    root = Path(root).resolve()
    pending = [root]
    while pending:
        directory = pending.pop()
        for path in sorted(directory.iterdir()):
            if path.is_symlink():
                yield path
            elif path.is_dir():
                if path.name not in IGNORED_DIRECTORIES and not (directory == root and path.name in {"message", "build", "dist"}):
                    pending.append(path)
            elif path.is_file() and path.name != ".git":
                yield path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def contained_file(root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("The package index contains a nonrelative path")
    candidate = Path(root) / path
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("The package index contains a symbolic or escaping path")
    return candidate


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
