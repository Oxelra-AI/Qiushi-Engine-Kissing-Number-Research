"""Explicit package membership and filesystem integrity checks."""
from pathlib import Path
import hashlib
import json

IGNORED_DIRECTORIES = {".git", ".venv", "__pycache__", ".pytest_cache"}


def files(root):
    """Inspect a directory, including unlisted files; not a publication list."""
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
    if not isinstance(relative, str):
        raise ValueError("The package index contains a nonrelative path")
    path = Path(relative)
    if (not relative or path.is_absolute() or ".." in path.parts
            or path.as_posix() != relative or "\\" in relative
            or any(ord(c) < 32 for c in relative)):
        raise ValueError("The package index contains a nonrelative path")
    candidate = Path(root) / path
    if (any(parent.is_symlink() for parent in (candidate, *candidate.parents)
            if parent != Path(root) and parent.is_relative_to(Path(root)))
            or not candidate.resolve().is_relative_to(Path(root).resolve())):
        raise ValueError("The package index contains a symbolic or escaping path")
    return candidate


def approved_paths(root):
    """Return the explicit file list, without admitting working-directory extras."""
    root = Path(root).resolve()
    index = json.loads(contained_file(root, "manifest.json").read_text())
    if index.get("schema_version") != 1 or not isinstance(index.get("files"), list):
        raise ValueError("Unsupported package manifest")
    names = [entry["path"] for entry in index["files"]]
    if len(names) != len(set(names)) or "manifest.json" in names:
        raise ValueError("Duplicate or self-indexed package path")
    for name in names:
        contained_file(root, name)
    return tuple(sorted(names))


def write_manifest(root, names, output=None):
    """Refresh hashes for an explicitly supplied set; never discover new files."""
    root = Path(root).resolve()
    entries = []
    for name in sorted(set(names)):
        if name == "manifest.json":
            raise ValueError("The manifest cannot index itself")
        path = contained_file(root, name)
        if not path.is_file():
            raise FileNotFoundError(name)
        entries.append({"path": name, "sha256": sha256(path), "bytes": path.stat().st_size})
    write_json(output or root / "manifest.json", {"schema_version": 1, "scope": "file integrity",
                                                  "files": entries})


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
